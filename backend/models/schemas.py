from pydantic import BaseModel
from enum import Enum


class UserLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class VideoInfo(BaseModel):
    id: str
    title: str
    category: str
    duration: str
    difficulty: str
    cover_url: str = ""


class Exercise(BaseModel):
    name: str
    target_muscle: str
    sets: int | str
    reps: int | str
    rest_seconds: int | str
    key_points: list[str]
    common_mistakes: list[str]
    breathing: str


class WorkoutPlan(BaseModel):
    title: str
    estimated_time: str
    calories: str
    warmup: list[str] = []
    exercises: list[Exercise]
    cooldown: list[str] = []
    next_suggestion: str = ""


class GenerateRequest(BaseModel):
    video_id: str | None = None
    subtitle_text: str | None = None
    user_level: UserLevel = UserLevel.intermediate
    goal: str = ""


class GenerateResponse(BaseModel):
    success: bool
    plan: WorkoutPlan | None = None
    error: str | None = None


class ChatRequest(BaseModel):
    exercise_name: str
    exercise_context: str
    question: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    answer: str
