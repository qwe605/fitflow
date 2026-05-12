from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.douyin import extract_subtitle_from_url

router = APIRouter()


class ParseRequest(BaseModel):
    url: str


@router.post("")
async def parse_douyin_url(req: ParseRequest):
    if not req.url.strip():
        raise HTTPException(status_code=400, detail="请输入抖音视频链接或口令")

    try:
        result = await extract_subtitle_from_url(req.url)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")
