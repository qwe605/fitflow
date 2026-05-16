import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.douyin import extract_subtitle_from_url, resolve_short_url, fetch_video_info
from services.video_analyzer import (
    download_video, extract_frames, analyze_frames_stream
)
from config import ARK_VISION_MODEL_ID

router = APIRouter()


class ParseRequest(BaseModel):
    url: str


def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/stream")
async def parse_douyin_url_stream(req: ParseRequest):
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="请输入抖音视频链接或口令")

    async def event_generator():
        yield sse_event({"step": "resolving", "message": "正在解析链接..."})

        try:
            real_url = await resolve_short_url(req.url)
        except Exception as e:
            yield sse_event({"step": "error", "message": f"链接解析失败: {e}"})
            return

        yield sse_event({"step": "fetching", "message": "正在获取视频信息..."})

        try:
            result = await fetch_video_info(real_url)
        except Exception as e:
            yield sse_event({"step": "error", "message": f"获取视频信息失败: {e}"})
            return

        video_url = result.get("video_url")

        if not video_url or not ARK_VISION_MODEL_ID:
            yield sse_event({"step": "done", "data": result})
            return

        yield sse_event({"step": "downloading", "message": "正在下载视频..."})

        last_progress = 0

        def on_progress(pct):
            nonlocal last_progress
            last_progress = pct

        try:
            video_path = await download_video(video_url, on_progress=on_progress)
        except Exception as e:
            yield sse_event({"step": "error", "message": f"视频下载失败: {e}"})
            yield sse_event({"step": "done", "data": result})
            return

        yield sse_event({"step": "extracting", "message": "正在提取关键帧..."})

        frame_paths = []
        try:
            frame_paths = extract_frames(video_path, max_frames=8)
            if not frame_paths:
                yield sse_event({"step": "done", "data": result})
                return
        except Exception:
            yield sse_event({"step": "done", "data": result})
            return
        finally:
            video_path.unlink(missing_ok=True)

        yield sse_event({"step": "analyzing", "message": "AI 正在分析动作..."})

        full_text = ""
        try:
            for chunk in analyze_frames_stream(frame_paths):
                full_text += chunk
                yield sse_event({"step": "analyzing", "partial": chunk})
        except Exception:
            pass
        finally:
            for fp in frame_paths:
                fp.unlink(missing_ok=True)
            if frame_paths:
                frame_paths[0].parent.rmdir()

        if full_text:
            result["subtitle_text"] = full_text

        yield sse_event({"step": "done", "data": result})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("")
async def parse_douyin_url(req: ParseRequest):
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="请输入抖音视频链接或口令")

    try:
        result = await extract_subtitle_from_url(req.url)

        video_url = result.get("video_url")
        if video_url and ARK_VISION_MODEL_ID:
            from services.video_analyzer import analyze_video
            try:
                description = await analyze_video(video_url)
                result["subtitle_text"] = description
            except Exception:
                pass

        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")
