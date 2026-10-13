"""二维码分享：生成 WiFi 连接载荷与二维码矩阵。

载荷遵循 WIFI: URI 约定（手机相机/扫码器可直接识别）：
    WIFI:T:WPA;S:<ssid>;P:<password>;;
特殊字符按约定转义，避免坏掉解析。
"""

from __future__ import annotations

import qrcode

_ESCAPE_CHARS = ("\\", ";", ",", ":", '"')


def _escape(value: str) -> str:
    for ch in _ESCAPE_CHARS:
        value = value.replace(ch, "\\" + ch)
    return value


def make_wifi_payload(ssid: str, password: str, security: str = "WPA") -> str:
    return f"WIFI:T:{security};S:{_escape(ssid)};P:{_escape(password)};;"


def matrix_for(payload: str) -> list[list[bool]]:
    """把任意载荷编码为二维码矩阵（True=深色格）。"""
    qr = qrcode.QRCode(border=0)
    qr.add_data(payload)
    qr.make(fit=True)
    return [[bool(cell) for cell in row] for row in qr.get_matrix()]
