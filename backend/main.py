from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import video, workout, chat, transcribe, douyin

app = FastAPI(title="FitFlow API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video.router, prefix="/api/videos", tags=["videos"])
app.include_router(workout.router, prefix="/api/workout", tags=["workout"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(transcribe.router, prefix="/api/transcribe", tags=["transcribe"])
app.include_router(douyin.router, prefix="/api/douyin", tags=["douyin"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
