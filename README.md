# WiFi 密码查看器（WiFi Pass Viewer）

一个用来**便捷查看本机已保存的 WiFi 密码**的 Windows 桌面小工具。

- 数据来源：Windows 本机 `netsh wlan` 存档（这台电脑曾经输入并保存过的 WiFi）
- 定位：个人自用、单机、只读；**不联网、不上传、不改系统设置**
- 界面：主从分栏（左列表 / 右详情），默认遮罩密码，一键复制 / 二维码分享

## 快速开始

**方式一（普通用户）：免安装 exe**

1. 下载 `wifi-pass-viewer-vX.Y.Z-win64.zip`，解压到任意文件夹
2. 双击 `wifi-pass-viewer.exe`（不需要安装 Python）
3. 如果 Windows 提示“未知发布者”，点「更多信息 → 仍要运行」——原因见《安全说明》

**方式二（开发者）：源码运行**

```bat
pip install -r requirements.txt
py wifi_pass_viewer/app.py
:: 或双击 run.bat
```

**打包 exe**：见 `docs/release-checklist.md`（含图标生成与杀软误报应对）。

## 功能与快捷键

| 功能 | 操作 |
|------|------|
| 搜索网络 | `/` 聚焦搜索框，输入即时过滤，`Esc` 清空 |
| 选择网络 | 鼠标点击，或 `↑` `↓` |
| 显示 / 隐藏密码 | 点眼睛图标，或 `Enter` |
| 一键全部显隐 | 侧栏「全部显示 / 全部隐藏」按钮；`Esc` = 全部隐藏（防投屏/截图泄漏） |
| 复制密码 | 「复制密码」按钮或 `C`；**自动排除剪贴板历史（Win+V）与云同步，60 秒后自动清除** |
| 二维码分享 | 「二维码」按钮，手机扫码直连（本机生成，可扫） |
| 查看版本 / 检查更新 | 左下角「关于」 |
| 刷新 | 左上角 `↻` |

其他细节：

- 已连接的网络会置顶并默认选中；若系统「位置」服务未开启导致查询受限，
  会降级显示并在左下角给出「去开启」按钮（不影响密码查看）。
- 列表右侧标签说明网络的密码可查看性：`开放网络`（无密码）、
  `企业网络`（802.1X 不保存明文）、`读取失败`（可刷新重试）。
- 首次启动会显示一条安全说明，点「知道了」后不再打扰。

## 安全说明

- **密码从哪来**：只读取 Windows 自己保存的存档（`netsh wlan show profile key=clear`
  的「关键内容」字段），不生成、不猜测、不联网；密码可随时与
  系统「管理已知网络 → 显示密码」对照验证。
- **剪贴板安全**：复制密码时会写入三个标准标记，使其**不进入剪贴板历史（Win+V）、
  不上传云剪贴板、不被剪贴板监视器记录**；60 秒后若剪贴板仍是该密码则自动清除。
- **为什么可能被杀软误报**：读取 WiFi 密码正是恶意软件的常见行为，个别安全软件
  会对未签名的新软件过度敏感。本软件不联网、不写文件、源码开放可审计。
  如遇拦截：选「仍要运行」，或先丢 VirusTotal 查毒。误报申诉流程见
  `docs/release-checklist.md`。

## 开发流程（Matt Pocock 技能包驱动）

1. ✅ HTML 原型先行（`prototype/`，三个结构不同的变体 + 截图存档）
2. ✅ 用户视角评审与迭代（`docs/review-round-1.md`）
3. ✅ TDD 实现（`tests/` 31 个测试；`docs/PRD.md` 约定测试缝）
4. ✅ 真实机器集成冒烟（`scripts/smoke_real.py`，密码仅打印长度）
5. ✅ 双轴代码评审 + 修正；GitHub CLI 管理文档与版本
6. ✅ 公众号文章与发布物料（`docs/article/`，ui-ux-pro-max 设计系统）

## 目录结构

```
wifi_pass_viewer/     # 应用（Python + pywebview + WebView2）
  app.py              # 入口与 JS API 桥
  scanner.py          # netsh 解析（纯函数）与扫描器
  clipboard_win.py    # 安全剪贴板（排除 Win+V / 云同步）
  qrshare.py          # WiFi 二维码载荷与矩阵
  ui/                 # 界面
tests/                # pytest 夹具与测试（31 个）
prototype/            # 原型（一次性产物，含 shots 截图）
scripts/              # 冒烟、文章构建、图标构建等工具脚本
assets/               # 应用图标（源 HTML + 产物）
docs/                 # PRD、评审记录、发布清单、文章物料、截图
run.bat               # 源码方式启动
```

## 测试

```bash
py -m pytest -q            # 31 passed
py scripts/smoke_real.py   # 真实 netsh 冒烟（不输出密码明文）
```

## License

MIT（见 `LICENSE`）。
