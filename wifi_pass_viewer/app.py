"""WiFi 密码查看器 —— 应用入口（pywebview + WebView2）。

数据流：前端调用 window.pywebview.api.scan() → 本模块调 netsh 扫描本机
已保存的 WiFi（含密码）→ 返回 JSON；二维码由 qrshare 在本地生成矩阵。
整个过程不联网、不写文件、不改系统设置。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if __package__ in (None, ""):  # 支持直接以脚本方式运行：py wifi_pass_viewer\app.py
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import webview

from wifi_pass_viewer.qrshare import make_wifi_payload, matrix_for
from wifi_pass_viewer.scanner import WindowsWifiScanner

UI_DIR = Path(__file__).parent / "ui"


class Api:
    """暴露给前端 JS 的接口（window.pywebview.api.*）。"""

    def __init__(self) -> None:
        self._scanner = WindowsWifiScanner()

    def scan(self) -> dict:
        try:
            result = self._scanner.scan()
            return {"ok": True, **result.to_dict()}
        except Exception as exc:  # 兜底：任何异常都以结构化的错误给前端
            return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    def qr_matrix(self, ssid: str, password: str, authentication: str = "") -> list[list[bool]]:
        security = "WEP" if "wep" in (authentication or "").lower() else "WPA"
        payload = make_wifi_payload(ssid, password, security=security)
        return matrix_for(payload)


def main() -> None:
    api = Api()
    webview.create_window(
        "WiFi 密码查看器",
        url=str(UI_DIR / "index.html"),
        js_api=api,
        width=1150,
        height=760,
        min_size=(900, 620),
        background_color="#f3f3f3",
    )
    debug = os.environ.get("WIFI_VIEWER_DEBUG") == "1"
    webview.start(debug=debug)


if __name__ == "__main__":
    sys.exit(main())
