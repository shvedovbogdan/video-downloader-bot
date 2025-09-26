import os
import asyncio
import logging
import re
import uuid
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, InputMediaPhoto
from aiogram.filters import Command
import yt_dlp
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# === НАЛАШТУВАННЯ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдено. Створи файл .env з токеном.")

DOWNLOADS_DIR = os.getenv("DOWNLOADS_DIR", "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def extract_twitter_images(url: str):
    """Повертає список посилань на фото з твіту"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
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

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Надішли посилання на пост з відео або фото з:\n"
        "• TikTok • Instagram • YouTube • Twitter (X)\n"
        "• Pinterest • Likee\n\n"
        "Я завантажу все без водяних знаків і надішлю альбомом, якщо можливо!"
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📘 <b>Як користуватися:</b>\n\n"
        "1. Скопіюй посилання на пост.\n"
        "2. Надішли його сюди.\n"
        "3. Отримай відео або фото!\n\n"
        "<i>💡 Для Pinterest: якщо це фото — іноді краще скопіювати пряме посилання на зображення (права кнопка → «Копіювати адресу зображення»).</i>",
        parse_mode="HTML"
    )

@dp.message(F.text)
async def handle_url(message: Message):
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        await message.answer("Будь ласка, надішли дійсне посилання.")
        return

    await message.answer("Аналізую посилання... ⏳")

    # Унікальне ім'я файлу
    unique_id = str(uuid.uuid4())
    base_path = os.path.join(DOWNLOADS_DIR, unique_id)

    # --- Спроба 1: yt-dlp (відео + фото) ---
    try:
        ydl_opts = {
            'format': 'best[height<=1080][filesize<50M]/best',
            'outtmpl': base_path + ".%(ext)s",
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # --- Відео ---
        for ext in ['mp4', 'webm', 'mkv', 'mov']:
            fpath = f"{base_path}.{ext}"
            if os.path.exists(fpath):
                await message.answer_video(FSInputFile(fpath))
                os.remove(fpath)
                return

        # --- Альбом (Instagram, Pinterest) ---
        if 'entries' in info and info['entries']:
            album_urls = []
            for entry in info['entries']:
                if 'url' in entry:
                    album_urls.append(entry['url'])
                elif 'thumbnails' in entry and entry['thumbnails']:
                    album_urls.append(entry['thumbnails'][-1]['url'])
            if album_urls:
                media = [InputMediaPhoto(media=url) for url in album_urls[:10]]
                await message.answer_media_group(media)
                return

        # --- Одне фото (thumbnails) ---
        thumbnails = [t['url'] for t in info.get('thumbnails', []) if t.get('url')]
        if thumbnails:
            await message.answer_photo(thumbnails[-1])
            return

    except Exception as e:
        error_msg = str(e)
        # Ці помилки означають "немає відео, але може бути фото"
        if not any(kw in error_msg for kw in [
            "No video formats found",
            "No video could be found in this tweet",
            "Video unavailable",
            "This video is not available",
            "Unsupported URL"
        ]):
            await message.answer(f"❌ Помилка: {error_msg[:300]}")
            return

    # --- Спроба 2: Twitter фото ---
    if "twitter.com" in url or "x.com" in url:
        images = extract_twitter_images(url)
        if images:
            if len(images) == 1:
                await message.answer_photo(images[0])
            else:
                media = [InputMediaPhoto(media=url) for url in images[:10]]
                await message.answer_media_group(media)
            return

    # --- Спроба 3: пряме фото (наприклад, Pinterest .jpg) ---
    if url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        try:
            await message.answer_photo(url)
            return
        except Exception:
            pass

    await message.answer("❌ Не вдалося знайти відео або фото за цим посиланням.")

# --- Запуск ---
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())