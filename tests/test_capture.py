import pytest

pytest.importorskip("Quartz")
pytest.importorskip("pyautogui")

from src.pipeline import capture


def fake_window(owner, width, height, name=""):
    return {
        "kCGWindowOwnerName": owner,
        "kCGWindowName": name,
        "kCGWindowBounds": {"X": 10, "Y": 20, "Width": width, "Height": height},
    }


def use_windows(monkeypatch, windows):
    monkeypatch.setattr(capture.Quartz, "CGWindowListCopyWindowInfo", lambda *_args: windows)


def test_skips_tiny_windows_of_the_same_app(monkeypatch):
    use_windows(monkeypatch, [fake_window("WeChat", 38, 25), fake_window("WeChat", 330, 630)])
    assert capture.get_window_bounds("WeChat") == (10, 20, 330, 630)


def test_returns_frontmost_large_match(monkeypatch):
    use_windows(monkeypatch, [fake_window("Other", 500, 500), fake_window("WeChat", 330, 630), fake_window("WeChat", 900, 700)])
    assert capture.get_window_bounds("WeChat") == (10, 20, 330, 630)


def test_only_tiny_windows_gives_a_clear_error(monkeypatch):
    use_windows(monkeypatch, [fake_window("WeChat", 38, 25)])
    with pytest.raises(RuntimeError, match="tiny"):
        capture.get_window_bounds("WeChat")


def test_no_window_gives_a_clear_error(monkeypatch):
    use_windows(monkeypatch, [fake_window("Finder", 800, 600)])
    with pytest.raises(RuntimeError, match="No window found"):
        capture.get_window_bounds("WeChat")
