"""Central place for all tunables: window title, board size, OCR credentials."""

import json
import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Written by prerun.py; overrides the board margin defaults below when present.
CALIBRATION_PATH = Path(__file__).resolve().parent.parent / "calibration.json"


def _load_calibration() -> dict:
    if CALIBRATION_PATH.exists():
        return json.loads(CALIBRATION_PATH.read_text())
    return {}


_CALIBRATION = _load_calibration()


@dataclass
class Config:
    window_title: str = os.environ.get("WINDOW_TITLE", "WeChat")
    rows: int = 16
    cols: int = 10
    capture_crop_percent: float = 0.85
    # Board margins within the cropped screenshot: (top, left) and (bottom, right), in
    # screenshot pixels. Run prerun.py to measure and save these automatically.
    board_begin_position: tuple = tuple(_CALIBRATION.get("board_begin_position", (26, 15)))
    board_end_margin: tuple = tuple(_CALIBRATION.get("board_end_margin", (57, 15)))
    gemini_api_key: str = os.environ.get("GEMINI_API_KEY", "")
    gemini_model: str = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")

    # Which solver plays: "greedy", "smallest" or "beam" (see src/pipeline/solve.py).
    # Larger beam_width / beam_branching plan better but take longer before the first move.
    solver: str = os.environ.get("SOLVER", "beam")
    beam_width: int = 200
    beam_branching: int = 20

    # Mouse timing: the mini-program's webview needs real time between move/click/drag
    # to register input reliably. Increase these if moves still get missed.
    move_duration: float = 0.05
    drag_duration: float = 0.15
    settle_delay: float = 0.08


DEFAULT_CONFIG = Config()
