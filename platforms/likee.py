# platforms/likee.py
import os
import yt_dlp
from pathlib import Path
from typing import Dict, List
from utils import download_image_from_url

def download(url: str, temp_dir: str) -> Dict[str, List[Path]]:
    result = {"videos": [], "photos": [], "audios": []}
    base_path = os.path.join(temp_dir, "likee")

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
                break

    except Exception:
        pass

    return result