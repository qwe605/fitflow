from fastapi import APIRouter, HTTPException

from models.schemas import GenerateRequest, GenerateResponse, WorkoutPlan
from services.ai_service import generate_workout_plan
from services.subtitle import get_subtitle_by_video_id

router = APIRouter()


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
