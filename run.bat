@echo off
rem WiFi 密码查看器 —— 双击启动（无控制台窗口）
cd /d "%~dp0"
where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw -3 "wifi_pass_viewer\app.py"
) else (
    start "" py -3 "wifi_pass_viewer\app.py"
)
