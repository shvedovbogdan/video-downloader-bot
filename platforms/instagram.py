# platforms/instagram.py
import os
import yt_dlp
from pathlib import Path
from typing import Dict, List
from utils import download_image_from_url

def download(url: str, temp_dir: str) -> Dict[str, List[Path]]:
    result = {"videos": [], "photos": [], "audios": []}
    base_path = os.path.join(temp_dir, "instagram")

    try:
        ydl_opts = {
            'format': 'best[height<=1080][filesize<50M]/best',
            'outtmpl': base_path + ".%(ext)s",
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Відео
        for ext in ['mp4', 'webm']:
            f = Path(f"{base_path}.{ext}")
            if f.exists():
                result["videos"].append(f)
                return result

        # Альбом фото
        if 'entries' in info:
            for i, entry in enumerate(info['entries'][:10]):
                if entry.get('thumbnails'):
                    thumb_url = entry['thumbnails'][-1]['url']
                    photo_path = Path(temp_dir) / f"ig_{i}.jpg"
                    download_image_from_url(thumb_url, photo_path)
                    result["photos"].append(photo_path)
        elif info.get('thumbnails'):
            thumb_url = info['thumbnails'][-1]['url']
            photo_path = Path(temp_dir) / "ig.jpg"
            download_image_from_url(thumb_url, photo_path)
            result["photos"].append(photo_path)

    except Exception:
        pass

    return result