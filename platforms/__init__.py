# platforms/__init__.py
from .tiktok import download as tiktok_download
from .instagram import download as instagram_download
from .youtube import download as youtube_download
from .twitter import download as twitter_download
from .pinterest import download as pinterest_download
from .likee import download as likee_download

PLATFORM_HANDLERS = {
    "tiktok.com": tiktok_download,
    "instagram.com": instagram_download,
    "youtube.com": youtube_download,
    "youtu.be": youtube_download,
    "twitter.com": twitter_download,
    "x.com": twitter_download,
    "pinterest.com": pinterest_download,
    "pin.it": pinterest_download,
    "likee.video": likee_download,
}