telegram_downloader_bot/\
├── main.py                 # Головний файл (роутинг + запуск)\
├── platforms/
│   ├── __init__.py\
│   ├── tiktok.py\
│   ├── instagram.py\
│   ├── youtube.py\
│   ├── twitter.py\
│   ├── pinterest.py\
│   └── likee.py\
├── .env\
├── .gitignore\
└── requirements.txt            ← опціонально, але добре мати


# Video Downloader Bot

Бот для особистого використання: завантажує відео з TikTok, Instagram, YouTube тощо без водяних знаків.

## Як запустити
1. `pip install -r requirements.txt`
2. Створи `.env` з `BOT_TOKEN=...`
3. `python main.py`


# === НАЛАШТУВАННЯ ===
DOWNLOADS_DIR = os.getenv("DOWNLOADS_DIR", "downloads")  # "downloads" — значення за замовчуванням
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
