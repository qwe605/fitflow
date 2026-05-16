"""
测试视频内容解析流程
用法: python test_video_parse.py [抖音链接或口令]
不传参数则使用内置测试链接
"""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.douyin import extract_subtitle_from_url, resolve_short_url, extract_video_url
from services.video_analyzer import (
    download_video, extract_frames, analyze_frames, get_video_duration
)
from config import ARK_API_KEY, ARK_VISION_MODEL_ID

TEST_URL = "2.53 09/23 c@n.dA :0pm kpd:/ 【投屏版】45分钟无跑跳，暴汗燃脂+拉伸，每周3-5遍瘦全身 # 暴汗燃脂瘦全身 # 健身 # 运动 # 减肥 # 居家锻炼 @DOU+小助手  https://v.douyin.com/0sEYkDowAsY/ 复制此链接，打开Dou音搜索，直接观看视频！"


def section(title: str):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


async def test_url_resolve(url: str):
    """测试短链接解析"""
    section("1. 短链接解析")
    t0 = time.time()
    try:
        real_url = await resolve_short_url(url)
        print(f"  输入: {url}")
        print(f"  解析: {real_url[:80]}...")
        print(f"  耗时: {time.time()-t0:.2f}s")
        return real_url
    except Exception as e:
        print(f"  失败: {e}")
        return None


async def test_video_info(url: str):
    """测试视频信息提取"""
    section("2. 视频信息提取")
    t0 = time.time()
    try:
        info = await extract_subtitle_from_url(url)
        print(f"  标题: {info['title'][:60]}")
        print(f"  描述: {(info['description'] or '无')[:80]}")
        print(f"  字幕文本长度: {len(info['subtitle_text'])} 字符")
        print(f"  视频直链: {'有' if info.get('video_url') else '无'}")
        if info.get("video_url"):
            print(f"    {info['video_url'][:80]}...")
        print(f"  耗时: {time.time()-t0:.2f}s")
        return info
    except Exception as e:
        print(f"  失败: {e}")
        return None


async def test_video_download(video_url: str):
    """测试视频下载"""
    section("3. 视频下载")
    t0 = time.time()
    try:
        video_path = await download_video(video_url)
        size_mb = video_path.stat().st_size / 1024 / 1024
        print(f"  保存: {video_path}")
        print(f"  大小: {size_mb:.1f} MB")
        print(f"  耗时: {time.time()-t0:.2f}s")
        return video_path
    except Exception as e:
        print(f"  失败: {e}")
        return None


def test_frame_extract(video_path: Path):
    """测试帧提取"""
    section("4. 关键帧提取")
    t0 = time.time()
    try:
        duration = get_video_duration(video_path)
        print(f"  视频时长: {duration:.1f}s")

        frames = extract_frames(video_path, max_frames=6)
        print(f"  提取帧数: {len(frames)}")
        for i, fp in enumerate(frames):
            size_kb = fp.stat().st_size / 1024
            print(f"    帧{i}: {fp.name} ({size_kb:.0f} KB)")
        print(f"  耗时: {time.time()-t0:.2f}s")
        return frames
    except Exception as e:
        print(f"  失败: {e}")
        print(f"  提示: 需要安装 ffmpeg (https://ffmpeg.org/download.html)")
        return []


def test_vision_analyze(frames: list[Path]):
    """测试视觉模型分析"""
    section("5. 视觉模型分析")

    if not ARK_API_KEY:
        print("  跳过: 未配置 ARK_API_KEY")
        return None
    if not ARK_VISION_MODEL_ID:
        print("  跳过: 未配置 ARK_VISION_MODEL_ID")
        return None

    t0 = time.time()
    try:
        result = analyze_frames(frames)
        print(f"  分析结果 ({len(result)} 字符):")
        print(f"  {'─'*40}")
        for line in result.split("\n")[:20]:
            print(f"  {line}")
        if result.count("\n") > 20:
            print(f"  ... (共 {result.count(chr(10))+1} 行)")
        print(f"  {'─'*40}")
        print(f"  耗时: {time.time()-t0:.2f}s")
        return result
    except Exception as e:
        print(f"  失败: {e}")
        return None


def cleanup(video_path: Path | None, frames: list[Path]):
    """清理临时文件"""
    section("6. 清理")
    count = 0
    if video_path and video_path.exists():
        video_path.unlink()
        count += 1
    for fp in frames:
        if fp.exists():
            fp.unlink()
            count += 1
    print(f"  已清理 {count} 个临时文件")


async def main():
    url = sys.argv[1] if len(sys.argv) > 1 else TEST_URL
    print(f"测试视频解析流程")
    print(f"输入: {url}")

    real_url = await test_url_resolve(url)
    if not real_url:
        print("\n链接解析失败，终止测试")
        return

    info = await test_video_info(url)
    if not info:
        print("\n视频信息提取失败，终止测试")
        return

    video_url = info.get("video_url")
    video_path = None
    frames = []

    if video_url:
        video_path = await test_video_download(video_url)
        if video_path:
            frames = test_frame_extract(video_path)
            if frames:
                test_vision_analyze(frames)
    else:
        print("\n未获取到视频直链，跳过下载/截帧/分析步骤")
        print("将仅使用字幕文本进行训练计划生成")

    cleanup(video_path, frames)

    section("总结")
    print(f"  链接解析: {'通过' if real_url else '失败'}")
    print(f"  信息提取: {'通过' if info else '失败'}")
    print(f"  视频直链: {'有' if video_url else '无'}")
    print(f"  视频下载: {'通过' if video_path else '跳过/失败'}")
    print(f"  帧提取:   {len(frames)} 帧")
    print(f"  视觉分析: {'通过' if frames and ARK_API_KEY else '跳过'}")


if __name__ == "__main__":
    asyncio.run(main())
