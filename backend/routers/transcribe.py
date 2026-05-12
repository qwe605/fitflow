from fastapi import APIRouter, UploadFile, File, HTTPException
from services.subtitle import transcribe_audio

router = APIRouter()


@router.post("")
async def transcribe(file: UploadFile = File(...)):
    if not file.filename.endswith((".mp3", ".mp4", ".wav", ".m4a", ".webm")):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 25MB)")

    text = transcribe_audio(content, file.filename)
    return {"subtitle": text}
