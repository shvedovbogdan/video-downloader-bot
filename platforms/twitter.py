# platforms/twitter.py
import os
import yt_dlp
from pathlib import Path
from typing import Dict, List
from utils import download_image_from_url
import requests
from bs4 import BeautifulSoup
import re

def extract_twitter_images(url: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            if 'media.twimg.com' in src and 'profile_images' not in src:
                clean_url = re.sub(r'\?.*$', '', src)
                if clean_url not in images:
                    images.append(clean_url)
        return images
    except Exception:
        return []

def download(url: str, temp_dir: str) -> Dict[str, List[Path]]:
    result = {"videos": [], "photos": [], "audios": []}
    base_path = os.path.join(temp_dir, "twitter")

    # Спроба через yt-dlp (відео)
    try:
        ydl_opts = {
            'format': 'best[height<=1080][filesize<50M]/best',
            'outtmpl': base_path + ".%(ext)s",
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for ext in ['mp4', 'webm']:
            f = Path(f"{base_path}.{ext}")
            if f.exists():
                result["videos"].append(f)
                return result

    except Exception:
        pass

    # Спроба фото
    images = extract_twitter_images(url)
    for i, img_url in enumerate(images[:10]):
        photo_path = Path(temp_dir) / f"tw_{i}.jpg"
        download_image_from_url(img_url, photo_path)
        result["photos"].append(photo_path)

    return result