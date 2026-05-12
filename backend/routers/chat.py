from fastapi import APIRouter

from models.schemas import ChatRequest, ChatResponse
from services.ai_service import chat_about_exercise

router = APIRouter()


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    answer = chat_about_exercise(
        exercise_name=req.exercise_name,
        exercise_context=req.exercise_context,
        question=req.question,
        history=req.history,
    )
    return ChatResponse(answer=answer)
