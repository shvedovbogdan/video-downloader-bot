# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import asyncio
import logging
from email import message
from fileinput import filename

from aiogram.types import FSInputFile
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import yt_dlp
from dotenv import load_dotenv



# === НАЛАШТУВАННЯ ===
DOWNLOADS_DIR = os.getenv("DOWNLOADS_DIR", "downloads")  # "downloads" — значення за замовчуванням
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- /start ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привіт! Надішли мені посилання на відео або пост з:\n"
        "• TikTok • Instagram • YouTube • Twitter (X)\n"
        "• Pinterest • Likee\n\n"
        "Я завантажу його без водяних знаків (де це можливо)!"
    )

# --- /help ---
@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📘 <b>Як користуватися:</b>\n\n"
        "1. Знайди відео з рецептом, малюнком чи інструкцією.\n"
        "2. Скопіюй посилання (натисни «Поділитися» → «Копіювати посилання»).\n"
        "3. Надішли його сюди.\n"
        "4. Отримай файл без логотипу!\n\n"
        "<i>⚠️ Відео має бути менше 50 МБ (обмеження Telegram).</i>",
        parse_mode="HTML"
    )

# --- /lang ---
@dp.message(Command("lang"))
async def cmd_lang(message: Message):
    await message.answer(
        "🇺🇦 Мова бота: українська\n"
        "🇬🇧 Bot language: Ukrainian\n"
        "🇺🇿 Botning tili: Ukrain"
    )

# --- Обробка посилання ---
@dp.message(F.text)
async def handle_url(message: Message):
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        await message.answer("Будь ласка, надішли дійсне посилання (з https://).")
        return

    await message.answer("Завантажую... ⏳")

    filename = os.path.join(DOWNLOADS_DIR, "video.mp4")

    ydl_opts = {
        'format': 'best[height<=1080][filesize<50M]/best',  # до 1080p і <50 МБ
        'outtmpl': filename,
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        import yt_dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(filename):
            video = FSInputFile(filename)
            await message.answer_video(video)
            os.remove(filename)
        else:
            await message.answer("Не вдалося знайти завантажений файл.")

    except Exception as e:
        if os.path.exists(filename):
            os.remove(filename)
        error_msg = str(e)
        if "Video unavailable" in error_msg:
            await message.answer("❌ Відео недоступне або приватне.")
        elif "This video is not available" in error_msg:
            await message.answer("❌ Це відео не можна завантажити (можливо, приватне).")
        else:
            await message.answer(f"❌ Помилка: {error_msg[:300]}")

# --- Запуск ---
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())