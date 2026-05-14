import json
import re
import httpx


async def extract_subtitle_from_url(url: str) -> dict:
    """
    从抖音视频链接提取字幕。
    流程：解析短链接 → 获取视频页面 → 提取视频信息 → 尝试获取字幕
    如果无法获取自动字幕，则返回视频标题和描述作为上下文。
    """
    real_url = await resolve_short_url(url)
    video_info = await fetch_video_info(real_url)
    return video_info


async def resolve_short_url(url: str) -> str:
    """解析抖音短链接/口令中的真实URL"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, url)
    if not urls:
        raise ValueError("未找到有效链接")

    target_url = urls[0]

    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        resp = await client.get(target_url, headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
        })
        return str(resp.url)


def extract_video_url(html: str) -> str | None:
    """从抖音页面 HTML 中提取视频播放地址"""
    patterns = [
        r'"play_addr"\s*:\s*\{[^}]*"url_list"\s*:\s*\["([^"]+)"',
        r'"playAddr"\s*:\s*"([^"]+)"',
        r'"play_addr_h264"\s*:\s*\{[^}]*"url_list"\s*:\s*\["([^"]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            raw_url = match.group(1)
            try:
                decoded = json.loads(f'"{raw_url}"')
            except (json.JSONDecodeError, ValueError):
                decoded = raw_url
            if decoded.startswith("http"):
                return decoded
    return None


async def fetch_video_info(url: str) -> dict:
    """从抖音视频页面提取视频信息"""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers={
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "Referer": "https://www.douyin.com/",
        })
        html = resp.text

    title = ""
    desc = ""

    title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()

    desc_match = re.search(r'"desc"\s*:\s*"([^"]*)"', html)
    if desc_match:
        desc = desc_match.group(1)

    if not title and not desc:
        desc_match = re.search(r'content="([^"]*)".*?name="description"', html)
        if desc_match:
            desc = desc_match.group(1)

    video_url = extract_video_url(html)
    content = f"{title}\n{desc}" if desc else title

    return {
        "title": title or "抖音视频",
        "description": desc,
        "subtitle_text": content,
        "source_url": url,
        "video_url": video_url,
    }
