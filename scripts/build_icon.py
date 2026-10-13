"""从 assets/icon.src.html 渲染应用图标（PNG + 多尺寸 ICO）。

用法：py scripts/build_icon.py
"""

from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 256, "height": 256}, device_scale_factor=1)
    page.goto((ASSETS / "icon.src.html").as_uri())
    page.wait_for_timeout(250)
    page.screenshot(path=str(ASSETS / "icon.png"), omit_background=True)
    browser.close()

image = Image.open(ASSETS / "icon.png").convert("RGBA")
image.save(
    ASSETS / "wifi-pass-viewer.ico",
    sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
)
print("icon built:", ASSETS / "wifi-pass-viewer.ico")
