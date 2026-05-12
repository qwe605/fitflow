import json
import os
import re
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
from enum import Enum

# --- Config ---
ARK_API_KEY = os.environ.get("ARK_API_KEY", "")
ARK_MODEL_ID = os.environ.get("ARK_MODEL_ID", "")
ARK_BASE_URL = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")

client = OpenAI(api_key=ARK_API_KEY, base_url=ARK_BASE_URL)
DATA_DIR = Path(__file__).parent / "data" / "presets"

# --- Models ---
class UserLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"

class GenerateRequest(BaseModel):
    video_id: str | None = None
    subtitle_text: str | None = None
    user_level: UserLevel = UserLevel.intermediate
    goal: str = ""

class ChatRequest(BaseModel):
    exercise_name: str
    exercise_context: str
    question: str
    history: list[dict] = []

class ParseRequest(BaseModel):
    url: str

# --- App ---
app = FastAPI(title="FitFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Prompts ---
SYSTEM_PROMPT_GENERATE = """你是一位专业健身教练，拥有运动科学背景。
你的任务是将健身视频的字幕/文字稿解析为结构化的训练计划。

用户会提供：
1. 视频字幕文本
2. 用户体能水平（beginner/intermediate/advanced）
3. 可选的训练目标

请严格按以下 JSON 格式输出，不要输出任何其他内容：
{
  "title": "训练计划标题",
  "estimated_time": "预计时长，如 25min",
  "calories": "预计消耗热量，如 180kcal",
  "warmup": ["热身动作1", "热身动作2"],
  "exercises": [
    {
      "name": "动作名称",
      "target_muscle": "目标肌群",
      "sets": 3,
      "reps": 12,
      "rest_seconds": 60,
      "key_points": ["要点1", "要点2"],
      "common_mistakes": ["常见错误1"],
      "breathing": "呼吸节奏说明"
    }
  ],
  "cooldown": ["拉伸动作1", "拉伸动作2"],
  "next_suggestion": "下次训练建议"
}

规则：
- beginner：组数少（2-3组），次数适中（8-10次），休息时间长（90秒），必须包含热身和拉伸
- intermediate：标准组数（3-4组），标准次数（10-12次），休息60秒
- advanced：高组数（4-5组），高次数（12-15次），休息45秒，可加入超级组建议
- 如果字幕中提到了具体的组数次数，优先参考视频内容，再根据用户水平微调
- common_mistakes 要具体实用，不要泛泛而谈
- breathing 要对应具体动作的发力和还原阶段"""

SYSTEM_PROMPT_CHAT = """你是一位专业健身教练助手。用户正在执行训练计划，对某个动作有疑问。
请基于提供的动作上下文，给出简洁、实用的回答。
回答要求：简洁明了，不超过150字，针对性强，如果涉及安全问题优先提醒。"""

# --- Helper functions ---
def get_video_list():
    with open(DATA_DIR / "videos.json", encoding="utf-8") as f:
        return json.load(f)

def get_subtitle_by_video_id(video_id: str):
    videos = get_video_list()
    for v in videos:
        if v["id"] == video_id:
            subtitle_path = DATA_DIR / v["subtitle_file"]
            if subtitle_path.exists():
                return subtitle_path.read_text(encoding="utf-8")
    return None

# --- Routes ---
@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/videos")
def list_videos():
    return get_video_list()

@app.get("/api/videos/{video_id}")
def get_video(video_id: str):
    videos = get_video_list()
    for v in videos:
        if v["id"] == video_id:
            return v
    raise HTTPException(status_code=404, detail="Video not found")

@app.get("/api/videos/{video_id}/subtitle")
def get_video_subtitle(video_id: str):
    subtitle = get_subtitle_by_video_id(video_id)
    if subtitle is None:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    return {"video_id": video_id, "subtitle": subtitle}

@app.post("/api/workout/generate")
def generate_workout(req: GenerateRequest):
    subtitle_text = req.subtitle_text
    if not subtitle_text and req.video_id:
        subtitle_text = get_subtitle_by_video_id(req.video_id)
        if not subtitle_text:
            raise HTTPException(status_code=404, detail="Video subtitle not found")
    if not subtitle_text:
        raise HTTPException(status_code=400, detail="Either video_id or subtitle_text is required")

    try:
        user_message = f"视频字幕内容：\n{subtitle_text}\n\n用户体能水平：{req.user_level.value}\n"
        if req.goal:
            user_message += f"训练目标：{req.goal}\n"

        response = client.chat.completions.create(
            model=ARK_MODEL_ID,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_GENERATE},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]
        plan = json.loads(content)
        return {"success": True, "plan": plan}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/chat")
def chat(req: ChatRequest):
    messages = [{"role": "system", "content": SYSTEM_PROMPT_CHAT}]
    context_msg = f"当前动作：{req.exercise_name}\n动作要点：{req.exercise_context}"
    messages.append({"role": "user", "content": context_msg})
    messages.append({"role": "assistant", "content": "好的，我了解这个动作的上下文了。请问你有什么问题？"})
    if req.history:
        for h in req.history[-4:]:
            messages.append(h)
    messages.append({"role": "user", "content": req.question})

    response = client.chat.completions.create(
        model=ARK_MODEL_ID,
        messages=messages,
        temperature=0.5,
        max_tokens=300,
    )
    return {"answer": response.choices[0].message.content.strip()}

@app.post("/api/douyin")
async def parse_douyin(req: ParseRequest):
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="请输入抖音视频链接或口令")
    try:
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, req.url)
        if not urls:
            raise ValueError("未找到有效链接")

        target_url = urls[0]
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as http_client:
            resp = await http_client.get(target_url, headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
            })
            real_url = str(resp.url)
            html = resp.text

        title = ""
        desc = ""
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
        desc_match = re.search(r'"desc"\s*:\s*"([^"]*)"', html)
        if desc_match:
            desc = desc_match.group(1)

        content = f"{title}\n{desc}" if desc else title
        return {
            "title": title or "抖音视频",
            "description": desc,
            "subtitle_text": content,
            "source_url": real_url,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")
