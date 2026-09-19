import json
from types import SimpleNamespace

import pytest

pytest.importorskip("google.genai")

from src.pipeline import ocr


def fake_gemini(monkeypatch, reply):
    client = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **_kw: SimpleNamespace(text=json.dumps(reply))))
    monkeypatch.setattr(ocr.genai, "Client", lambda api_key: client)


def board_image(tmp_path):
    path = tmp_path / "board.png"
    path.write_bytes(b"not a real png, the fake client never decodes it")
    return str(path)


def test_returns_digits(monkeypatch, tmp_path):
    fake_gemini(monkeypatch, [1, 2, 3, 4])
    assert ocr.recognize_board(board_image(tmp_path), 2, 2, "key", "model") == [1, 2, 3, 4]


def test_all_zero_board_is_rejected(monkeypatch, tmp_path):
    fake_gemini(monkeypatch, [0, 0, 0, 0])
    with pytest.raises(ValueError, match="all zeros"):
        ocr.recognize_board(board_image(tmp_path), 2, 2, "key", "model")


def test_wrong_digit_count_is_rejected(monkeypatch, tmp_path):
    fake_gemini(monkeypatch, [1, 2, 3])
    with pytest.raises(ValueError, match="expected 4"):
        ocr.recognize_board(board_image(tmp_path), 2, 2, "key", "model")
