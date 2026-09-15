"""Central place for all tunables: window title, board size, OCR credentials."""

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
    gemini_api_key: str = os.environ.get("GEMINI_API_KEY", "")
    gemini_model: str = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


DEFAULT_CONFIG = Config()
