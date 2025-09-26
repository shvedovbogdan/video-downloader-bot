# main.py
import os
import asyncio
import tempfile
import types

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, InputMediaPhoto
from aiogram.filters import Command
from platforms import PLATFORM_HANDLERS
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдено. Створи .env файл.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_handler(url: str):
    for domain, handler in PLATFORM_HANDLERS.items():
        if domain in url:
            return handler
    return None

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Привіт! Я допоможу тобі завантажити відео або фото з:\n"
        "• YouTube • TikTok • Instagram • Twitter (X)\n"
        "• Pinterest • Likee\n\n"
        "📌 Просто надішли посилання!\n"
        "ℹ️ Детальніше — команда /help"
    )
# --- Команда /help ---
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "📘 <b>Як користуватися ботом:</b>\n\n"
        "1. Знайди пост з рецептом, малюнком чи відео.\n"
        "2. Скопіюй посилання (URL) з Instagram, TikTok тощо.\n"
        "3. Надішли його сюди.\n"
        "4. Бот запропонує вибрати якість або формат.\n"
        "5. Отримай файл без водяних знаків! ✅\n\n"
        "<b>Підтримувані платформи:</b>\n"
        "• TikTok — відео без логотипу\n"
        "• Instagram — фото/відео (Reels, пости)\n"
        "• YouTube — будь-яка якість\n"
        "• Twitter (X), Pinterest, Likee — відео/фото\n\n"
        "<i>⚠️ Відео має бути менше 50 МБ (обмеження Telegram).</i>"
    )
    await message.answer(help_text, parse_mode="HTML")

# --- Команда /lang ---
@dp.message(Command("lang"))
async def cmd_lang(message: types.Message):
    await message.answer(
        "🇺🇦 Мова бота: українська\n"
        "🇬🇧 Bot language: Ukrainian\n"
        "🇺🇿 Botning tili: Ukrain"
    )

@dp.message(F.text)
async def handle_url(message: Message):
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        await message.answer("Надішліть дійсне посилання.")
        return

    handler = get_handler(url)
    if not handler:
        await message.answer("❌ Ця платформа не підтримується.")
        return

    await message.answer("Завантажую... ⏳")

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            result = await asyncio.to_thread(handler, url, temp_dir)

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

            if not any(result.values()):
                await message.answer("❌ Контент не знайдено.")

        except Exception as e:
            await message.answer(f"❌ Помилка: {str(e)[:300]}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())