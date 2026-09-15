"""Central place for all tunables: window title, board size, OCR credentials, threading."""

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


@dataclass
class Config:
    window_title: str = "开局托儿所"
    rows: int = 16
    cols: int = 10
    capture_crop_percent: float = 0.85
    ocr_thread_count: int = 3
    save_tile_images: bool = False
    baidu_api_key: str = os.environ.get("BAIDU_API_KEY", "")
    baidu_secret_key: str = os.environ.get("BAIDU_SECRET_KEY", "")


DEFAULT_CONFIG = Config()
