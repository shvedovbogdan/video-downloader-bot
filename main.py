# main.py
import os
import asyncio
import tempfile
import json
from pathlib import Path
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, InputMediaPhoto
from aiogram.filters import Command
from platforms import PLATFORM_HANDLERS
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO)

# === НАЛАШТУВАННЯ ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # в .env: OWNER_ID=123456789

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдено. Створи .env файл.")

STATS_FILE = Path("active_users.json")

def load_users():
    if STATS_FILE.exists():
        try:
            return set(json.loads(STATS_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
    return set()

def save_users(users):
    try:
        STATS_FILE.write_text(json.dumps(list(users)), encoding="utf-8")
    except Exception:
        pass

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 📊 Статистика: унікальні користувачі
active_users = load_users()

def get_handler(url: str):
    for domain, handler in PLATFORM_HANDLERS.items():
        if domain in url:
            return handler
    return None

# --- /start ---
@dp.message(Command("start"))
async def start(message: Message):
    active_users.add(message.from_user.id)
    save_users(active_users)
    await message.answer(
        "👋 Привіт! Я допоможу тобі завантажити відео або фото з:\n"
        "• YouTube • TikTok • Instagram • Twitter (X)\n"
        "• Pinterest • Likee\n\n"
        "📌 Просто надішли посилання!\n"
        "ℹ️ Детальніше — команда /help"
    )

# --- /stats (тільки для власника) ---
@dp.message(Command("stats"))
async def stats(message: Message):
    if message.from_user.id != OWNER_ID:
        return
    user_count = len(active_users)
    await message.answer(f"📊 Унікальних користувачів: {user_count}")

# --- /help ---
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "📘 <b>Як користуватися ботом:</b>\n\n"
        "1. Знайди пост з рецептом, малюнком чи відео.\n"
        "2. Скопіюй посилання (URL) з Instagram, TikTok тощо.\n"
        "3. Надішли його сюди.\n"
        "4. Отримай файл без водяних знаків! ✅\n\n"
        "<b>Підтримувані платформи:</b>\n"
        "• TikTok — відео без логотипу\n"
        "• Instagram — фото/відео (Reels, пости)\n"
        "• YouTube — будь-яка якість\n"
        "• Twitter (X), Pinterest, Likee — відео/фото\n\n"
        "<i>⚠️ Відео має бути менше 50 МБ (обмеження Telegram).</i>"
    )
    await message.answer(help_text, parse_mode="HTML")

# --- /lang ---
@dp.message(Command("lang"))
async def cmd_lang(message: Message):
    await message.answer(
        "🇺🇦 Мова бота: українська\n"
        "🇬🇧 Bot language: Ukrainian\n"
        "🇺🇿 Botning tili: Ukrain"
    )

# --- Обробка посилань ---
@dp.message(F.text)
async def handle_url(message: Message):
    url = message.text.strip()
    logging.info(f"User {message.from_user.id} requested: {url}")

    if not url.startswith(("http://", "https://")):
        await message.answer("Надішліть дійсне посилання.")
        return

    handler = get_handler(url)
    if not handler:
        await message.answer("❌ Ця платформа не підтримується.")
        return

    # Додаємо ТІЛЬКИ тих, хто надіслав валідне посилання
    active_users.add(message.from_user.id)
    save_users(active_users)

    await message.answer("Завантажую... ⏳")

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            result = await asyncio.to_thread(handler, url, temp_dir)

            # Особливий випадок: TikTok фото
            if result.get("is_tiktok_photo"):
                await message.answer(
                    "📸 Це фото-пост з TikTok.\n\n"
                    "На жаль, автоматичне завантаження не підтримується.\n\n"
                    "✅ Щоб зберегти фото:\n"
                    "1. Відкрий посилання в браузері\n"
                    "2. Дочекайся завантаження фото\n"
                    "3. Клацни правою кнопкою → «Копіювати адресу зображення»\n"
                    "4. Надішли це посилання сюди."
                )
                return

            for video in result["videos"]:
                await message.answer_video(FSInputFile(video))

            for audio in result["audios"]:
                await message.answer_audio(FSInputFile(audio))

            photos = result["photos"]
            if len(photos) == 1:
                await message.answer_photo(FSInputFile(photos[0]))
            elif len(photos) > 1:
                media = [InputMediaPhoto(media=FSInputFile(p)) for p in photos[:10]]
                await message.answer_media_group(media)

            if not any(result.get(k) for k in ["videos", "photos", "audios"]):
                raise Exception("No content found")

        except Exception as e:
            logging.error(f"Error processing {url}: {e}")

    # --- Fallback-інструкції ---
    if "pinterest." in url:
        await message.answer(
            "📌 Це фото з Pinterest. Щоб завантажити його:\n"
            "1. Відкрий пост у браузері\n"
            "2. Клацни правою кнопкою на фото → «Копіювати адресу зображення»\n"
            "3. Надішли це посилання сюди."
        )
    elif "tiktok.com" in url and "/photo/" in url:
        await message.answer(
            "📸 Це фото-пост з TikTok.\n\n"
            "На жаль, автоматичне завантаження не підтримується.\n\n"
            "✅ Щоб зберегти фото:\n"
            "1. Відкрий посилання в браузері\n"
            "2. Дочекайся завантаження фото\n"
            "3. Клацни правою кнопкою → «Копіювати адресу зображення»\n"
            "4. Надішли це посилання сюди."
        )
    else:
        await message.answer("❌ Контент не знайдено.")

# --- Запуск ---
async def main():
    bot_info = await bot.get_me()
    print(f"✅ Бот запущено!")
    print(f"🤖 Ім'я: {bot_info.full_name}")
    print(f"🆔 Username: @{bot_info.username}")
    print(f"🔗 ID: {bot_info.id}")
    print(f"👥 Унікальних користувачів на старті: {len(active_users)}")
    print("-" * 50)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())