# utils.py
import requests
from pathlib import Path

def download_image_from_url(url: str, path: Path):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    with open(path, "wb") as f:
        f.write(resp.content)

def extract_tiktok_photo(url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        import re, json
        match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__".*?>(.*?)</script>', response.text)
        if match:
            data = json.loads(match.group(1))
            item = data["__DEFAULT_SCOPE__"]["webapp.photo-detail"]["itemInfo"]["itemStruct"]
            if "imagePost" in item:
                return item["imagePost"]["images"][0]["imageURL"]["urlList"][0]
    except Exception:
        pass
    return None