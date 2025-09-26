# platforms/tiktok.py
import os
import yt_dlp
from pathlib import Path
from typing import Dict, List
from utils import extract_tiktok_photo, download_image_from_url

def download(url: str, temp_dir: str) -> Dict[str, List[Path]]:
    result = {"videos": [], "photos": [], "audios": []}
    base_path = os.path.join(temp_dir, "tiktok")

    # Спроба завантажити відео (включаючи слайд-шоу)
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

        # Аудіо окремо
        audio_path = base_path + "_audio.m4a"
        try:
            ydl_opts_audio = {
                'format': 'bestaudio[ext=m4a]/bestaudio',
                'outtmpl': audio_path,
                'quiet': True,
                'noplaylist': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                ydl.download([url])
            if os.path.exists(audio_path):
                result["audios"].append(Path(audio_path))
        except Exception:
            pass

    except Exception:
        pass

    # Якщо це /photo/ — спробувати фото
    if "/photo/" in url:
        photo_url = extract_tiktok_photo(url)
        if photo_url:
            photo_path = Path(temp_dir) / "tiktok_photo.jpg"
            download_image_from_url(photo_url, photo_path)
            result["photos"].append(photo_path)

    return result