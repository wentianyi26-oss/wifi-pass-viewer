# 发布清单（v1.0.0 起）

面向离线分发的发布流程。每次发版照此执行。

## 一、构建

```bat
:: 1) 图标（首次或改图标时）
py scripts\build_icon.py

:: 2) 打包（onedir，比 onefile 更少被杀软误报、启动更快）
py -m PyInstaller --noconfirm --clean --windowed --name wifi-pass-viewer ^
   --icon "assets\wifi-pass-viewer.ico" ^
   --add-data "wifi_pass_viewer/ui;wifi_pass_viewer/ui" wifi_pass_viewer/app.py
```

产物：`dist\wifi-pass-viewer\`（整目录）。压缩为
`wifi-pass-viewer-vX.Y.Z-win64.zip` 后上传到分发渠道。

## 二、杀软误报应对（重点）

"WiFi 密码查看器" 这个品类被恶意软件滥用过（读取密码正是恶意软件的标准动作、
PyInstaller 打包又是木马常用载体），**新版本首次发布后建议先自查**：

1. 上传 VirusTotal 自查（https://www.virustotal.com），记录结果；
2. 如 Defender 报毒/隔离：向 Microsoft 提交误报申诉
   https://www.microsoft.com/en-us/wdsi/filesubmission （选 "Software developer"），
   通常 24-72 小时内处理；
3. 给用户的说明模板（随下载说明一起提供）：

   > 由于工具使用系统命令读取本机 WiFi 存档，个别安全软件可能提示风险/未知发布者。
   > 这是误报：软件不联网、不写文件，代码全部开源可查。如遇拦截，选「仍要运行」；
   > 或先用 Virustotal 查毒后再运行。

4. SmartScreen「Windows 已保护你的电脑」是未签名软件的默认提示：
   点「更多信息 → 仍要运行」。代码签名（如 Azure Trusted Signing）可消除此提示，
   成本约 $10/月，可后续再上。

## 三、发布动作

1. 版本号：更新 `wifi_pass_viewer/__init__.py` 的 `__version__`，提交并打 tag：
   `git tag v1.0.0 && git push --tags`
2. 打包 `wifi-pass-viewer-vX.Y.Z-win64.zip`（文件名带版本号，旧版保留至少一版
   以备回滚说明），上传到你使用的分发渠道。
3. 如在 GitHub 创建 Release：把同名的 win64 zip 作为附件上传即可。

## 四、版本记录（维护在本文件）

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-10-13 | 首个发布版：主从分栏界面、搜索/复制/二维码、安全剪贴板（排除 Win+V/云同步）、Esc 隐藏、位置服务引导、关于/版本入口 |
