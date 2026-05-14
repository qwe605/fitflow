import base64
import subprocess
import tempfile
from pathlib import Path

import httpx
from openai import OpenAI

from config import ARK_API_KEY, ARK_BASE_URL, ARK_VISION_MODEL_ID

VISION_PROMPT = (
    "这些是一个健身教学视频的关键帧截图（按时间顺序排列）。"
    "请仔细观察每一帧中的人物动作，描述视频中展示的所有健身动作。\n"
    "对每个动作，请说明：\n"
    "1. 动作名称\n"
    "2. 动作要领（起始姿势、发力方式、结束姿势）\n"
    "3. 目标肌群\n"
    "4. 如果能观察到组数或次数请注明\n"
    "请用中文回答，尽量详细。"
)


async def download_video(video_url: str) -> Path:
    """下载视频到临时文件"""
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        resp = await client.get(video_url, headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "Referer": "https://www.douyin.com/",
        })
        resp.raise_for_status()

    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    tmp.write(resp.content)
    tmp.close()
    return Path(tmp.name)


def get_video_duration(video_path: Path) -> float:
    """用 ffprobe 获取视频时长（秒）"""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def extract_frames(video_path: Path, max_frames: int = 8) -> list[Path]:
    """用 ffmpeg 等间隔截取关键帧"""
    output_dir = Path(tempfile.mkdtemp())
    duration = get_video_duration(video_path)
    interval = duration / (max_frames + 1)

    frame_paths = []
    for i in range(max_frames):
        timestamp = interval * (i + 1)
        out_path = output_dir / f"frame_{i:03d}.jpg"
        subprocess.run(
            ["ffmpeg", "-ss", f"{timestamp:.2f}", "-i", str(video_path),
             "-vframes", "1", "-q:v", "3", "-y", str(out_path)],
            capture_output=True
        )
        if out_path.exists() and out_path.stat().st_size > 0:
            frame_paths.append(out_path)

    return frame_paths


def analyze_frames(frame_paths: list[Path]) -> str:
    """将帧图片发送给视觉模型，获取动作描述"""
    client = OpenAI(api_key=ARK_API_KEY, base_url=ARK_BASE_URL)

    content: list[dict] = [{"type": "text", "text": VISION_PROMPT}]
    for fp in frame_paths:
        img_data = base64.b64encode(fp.read_bytes()).decode()
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}
        })

    response = client.chat.completions.create(
        model=ARK_VISION_MODEL_ID,
        messages=[{"role": "user", "content": content}],
        temperature=0.3,
        max_tokens=2000,
    )
    return response.choices[0].message.content.strip()


async def analyze_video(video_url: str) -> str:
    """完整流程：下载视频 → 截帧 → 视觉分析 → 清理临时文件"""
    video_path = await download_video(video_url)
    frame_paths: list[Path] = []
    try:
        frame_paths = extract_frames(video_path, max_frames=8)
        if not frame_paths:
            raise ValueError("无法从视频中提取帧")
        return analyze_frames(frame_paths)
    finally:
        video_path.unlink(missing_ok=True)
        for fp in frame_paths:
            fp.unlink(missing_ok=True)
