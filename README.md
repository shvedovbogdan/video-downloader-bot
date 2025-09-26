video-downloader-bot/\
├── main.py \
├── .env                  ← НЕ комітиться (є в .gitignore)\
├── .gitignore\
├── requirements.txt      ← дуже корисно!\
└── README.md             ← опціонально, але добре мати


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
