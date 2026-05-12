import json
from openai import OpenAI
from config import ARK_API_KEY, ARK_MODEL_ID, ARK_BASE_URL

client = OpenAI(api_key=ARK_API_KEY, base_url=ARK_BASE_URL)

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
回答要求：
- 简洁明了，不超过150字
- 针对性强，直接解决用户问题
- 如果涉及安全问题，优先提醒用户注意安全"""


def generate_workout_plan(subtitle_text: str, user_level: str, goal: str = "") -> dict:
    user_message = f"""视频字幕内容：
{subtitle_text}

用户体能水平：{user_level}
"""
    if goal:
        user_message += f"训练目标：{goal}\n"

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
    return json.loads(content)


def chat_about_exercise(
    exercise_name: str, exercise_context: str, question: str, history: list[dict] = None
) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT_CHAT}]

    context_msg = f"当前动作：{exercise_name}\n动作要点：{exercise_context}"
    messages.append({"role": "user", "content": context_msg})
    messages.append({"role": "assistant", "content": "好的，我了解这个动作的上下文了。请问你有什么问题？"})

    if history:
        for h in history[-4:]:
            messages.append(h)

    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=ARK_MODEL_ID,
        messages=messages,
        temperature=0.5,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()
