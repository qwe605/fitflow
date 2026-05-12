from fastapi import APIRouter, HTTPException

from services.subtitle import get_video_list, get_subtitle_by_video_id
from models.schemas import VideoInfo

router = APIRouter()


@router.get("", response_model=list[VideoInfo])
def list_videos():
    videos = get_video_list()
    return [VideoInfo(**v) for v in videos]


@router.get("/{video_id}")
def get_video(video_id: str):
    videos = get_video_list()
    for v in videos:
        if v["id"] == video_id:
            return VideoInfo(**v)
    raise HTTPException(status_code=404, detail="Video not found")


@router.get("/{video_id}/subtitle")
def get_video_subtitle(video_id: str):
    subtitle = get_subtitle_by_video_id(video_id)
    if subtitle is None:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    return {"video_id": video_id, "subtitle": subtitle}
