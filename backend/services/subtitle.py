import json
import tempfile
from pathlib import Path

from openai import OpenAI
from config import ARK_API_KEY, ARK_BASE_URL

DATA_DIR = Path(__file__).parent.parent / "data" / "presets"


def get_video_list() -> list[dict]:
    with open(DATA_DIR / "videos.json", encoding="utf-8") as f:
        return json.load(f)


def get_subtitle_by_video_id(video_id: str) -> str | None:
    videos = get_video_list()
    for v in videos:
        if v["id"] == video_id:
            subtitle_path = DATA_DIR / v["subtitle_file"]
            if subtitle_path.exists():
                return subtitle_path.read_text(encoding="utf-8")
    return None


def transcribe_audio(file_bytes: bytes, filename: str) -> str:
    """Use OpenAI-compatible Whisper API to transcribe audio."""
    client = OpenAI(api_key=ARK_API_KEY, base_url=ARK_BASE_URL)

    suffix = Path(filename).suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="zh",
            )
        return transcript.text
    finally:
        Path(tmp_path).unlink(missing_ok=True)
