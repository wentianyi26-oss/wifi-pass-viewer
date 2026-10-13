import ctypes
import sys

import pytest

from wifi_pass_viewer import clipboard_win

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="仅 Windows 剪贴板实现")


def _format_available(name: str) -> bool:
    fmt = ctypes.windll.user32.RegisterClipboardFormatW(name)
    return bool(ctypes.windll.user32.IsClipboardFormatAvailable(fmt))


def test_copy_round_trip_and_excluded_from_history():
    clipboard_win.copy_without_history("WPV-TEST-123")
    assert clipboard_win.read_text() == "WPV-TEST-123"
    # 三种排除标记至少 "ExcludeClipboardContentFromMonitorProcessing" 存在
    assert _format_available("ExcludeClipboardContentFromMonitorProcessing")
    assert _format_available("CanIncludeInClipboardHistory")


def test_clear_if_matches_only_clears_matching_content():
    clipboard_win.copy_without_history("MATCH-ME")
    assert clipboard_win.clear_if_matches("other-value") is False
    assert clipboard_win.read_text() == "MATCH-ME"
    assert clipboard_win.clear_if_matches("MATCH-ME") is True
    assert clipboard_win.read_text() in (None, "")


def test_clear_if_matches_on_empty_clipboard_is_false():
    clipboard_win.clear_if_matches("anything")  # 先清空
    assert clipboard_win.clear_if_matches("anything") is False
