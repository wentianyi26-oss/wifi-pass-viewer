"""安全剪贴板：写入文本并排除 Windows 剪贴板历史（Win+V）与云同步。

通过设置三个标准剪贴板格式实现（密码管理器通用做法）：
  · CanIncludeInClipboardHistory = 0   → 不写入剪贴板历史
  · CanUploadToCloudClipboard = 0      → 不上传云剪贴板
  · ExcludeClipboardContentFromMonitorProcessing = 1 → 排除一切剪贴板监视
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002

_EXCLUDE_FORMAT = "ExcludeClipboardContentFromMonitorProcessing"
_CAN_INCLUDE_FORMAT = "CanIncludeInClipboardHistory"
_CAN_UPLOAD_FORMAT = "CanUploadToCloudClipboard"

_user32 = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32

_user32.OpenClipboard.argtypes = [wintypes.HWND]
_user32.OpenClipboard.restype = wintypes.BOOL
_user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
_user32.SetClipboardData.restype = wintypes.HANDLE
_user32.GetClipboardData.argtypes = [wintypes.UINT]
_user32.GetClipboardData.restype = wintypes.HANDLE
_user32.RegisterClipboardFormatW.argtypes = [wintypes.LPCWSTR]
_user32.RegisterClipboardFormatW.restype = wintypes.UINT
_kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
_kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
_kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
_kernel32.GlobalLock.restype = ctypes.c_void_p
_kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
_kernel32.GlobalUnlock.restype = wintypes.BOOL


def _global_from_bytes(data: bytes) -> int:
    handle = _kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
    if not handle:
        raise OSError("GlobalAlloc 失败")
    ptr = _kernel32.GlobalLock(handle)
    if not ptr:
        raise OSError("GlobalLock 失败")
    try:
        ctypes.memmove(ptr, data, len(data))
    finally:
        _kernel32.GlobalUnlock(handle)
    return handle


def _set_dword_format(fmt_name: str, value: int) -> None:
    fmt = _user32.RegisterClipboardFormatW(fmt_name)
    handle = _global_from_bytes(int(value).to_bytes(4, "little"))
    if not _user32.SetClipboardData(fmt, handle):
        raise OSError(f"写入剪贴板格式失败: {fmt_name}")


def copy_without_history(text: str) -> None:
    """把文本写入剪贴板，并标记为“不进历史 / 不同步 / 不被监视”。"""
    if not _user32.OpenClipboard(None):
        raise OSError("无法打开剪贴板（可能被其他程序占用，请稍后重试）")
    try:
        _user32.EmptyClipboard()
        _set_dword_format(_CAN_INCLUDE_FORMAT, 0)
        _set_dword_format(_CAN_UPLOAD_FORMAT, 0)
        _set_dword_format(_EXCLUDE_FORMAT, 1)
        handle = _global_from_bytes((text + "\0").encode("utf-16-le"))
        if not _user32.SetClipboardData(CF_UNICODETEXT, handle):
            raise OSError("写入剪贴板失败")
    finally:
        _user32.CloseClipboard()


def read_text() -> str | None:
    """读取剪贴板中的文本；没有文本内容时返回 None。"""
    if not _user32.OpenClipboard(None):
        return None
    try:
        handle = _user32.GetClipboardData(CF_UNICODETEXT)
        if not handle:
            return None
        ptr = _kernel32.GlobalLock(handle)
        if not ptr:
            return None
        try:
            return ctypes.wstring_at(ptr)
        finally:
            _kernel32.GlobalUnlock(handle)
    finally:
        _user32.CloseClipboard()


def clear_if_matches(expected: str) -> bool:
    """仅当剪贴板内容仍等于 expected 时才清空（避免误删用户后来复制的其他内容）。"""
    if read_text() != expected:
        return False
    if not _user32.OpenClipboard(None):
        return False
    try:
        _user32.EmptyClipboard()
        return True
    finally:
        _user32.CloseClipboard()
