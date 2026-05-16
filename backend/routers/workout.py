import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models.schemas import GenerateRequest, GenerateResponse, WorkoutPlan
from services.ai_service import generate_workout_plan, generate_workout_plan_stream
from services.subtitle import get_subtitle_by_video_id

router = APIRouter()


def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/generate/stream")
async def generate_stream(req: GenerateRequest):
    subtitle_text = req.subtitle_text

    if not subtitle_text and req.video_id:
        subtitle_text = get_subtitle_by_video_id(req.video_id)
        if not subtitle_text:
            raise HTTPException(status_code=404, detail="Video subtitle not found")

    if not subtitle_text:
        raise HTTPException(status_code=400, detail="Either video_id or subtitle_text is required")

    def event_generator():
        yield sse_event({"step": "generating", "message": "AI 正在生成训练计划..."})

        full_text = ""
        try:
            for chunk in generate_workout_plan_stream(
                subtitle_text=subtitle_text,
                user_level=req.user_level.value,
                goal=req.goal,
            ):
                full_text += chunk
                yield sse_event({"step": "generating", "partial": chunk})
        except Exception as e:
            yield sse_event({"step": "error", "message": str(e)})
            return

        content = full_text.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("```", 1)[0]

        try:
            plan_data = json.loads(content)
            yield sse_event({"step": "done", "data": {"success": True, "plan": plan_data}})
        except json.JSONDecodeError as e:
            yield sse_event({"step": "error", "message": f"JSON 解析失败: {e}"})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    subtitle_text = req.subtitle_text

    if not subtitle_text and req.video_id:
        subtitle_text = get_subtitle_by_video_id(req.video_id)
        if not subtitle_text:
            raise HTTPException(status_code=404, detail="Video subtitle not found")

    if not subtitle_text:
        raise HTTPException(status_code=400, detail="Either video_id or subtitle_text is required")

    try:
        result = generate_workout_plan(
            subtitle_text=subtitle_text,
            user_level=req.user_level.value,
            goal=req.goal,
        )
        plan = WorkoutPlan(**result)
        return GenerateResponse(success=True, plan=plan)
    except Exception as e:
        return GenerateResponse(success=False, error=str(e))
