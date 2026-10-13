# WiFi 密码查看器（WiFi Pass Viewer）

一个用来**便捷查看本机已保存的 WiFi 密码**的 Windows 桌面小工具。

- 数据来源：Windows 本机 `netsh wlan` 存档（这台电脑曾经输入并保存过的 WiFi）
- 定位：个人自用、单机、只读；**不联网、不上传、不改系统设置**
- 界面：主从分栏（左列表 / 右详情），默认遮罩密码，一键复制 / 二维码分享

## 快速开始

```bat
pip install pywebview qrcode
:: 然后双击 run.bat（无控制台窗口启动）
```

或者命令行启动：

```bash
py wifi_pass_viewer/app.py
```

> 依赖：Windows 10/11 + Python 3.10+（开发环境 3.14）。界面基于 WebView2（Win11/新版 Edge 自带）。

## 功能与快捷键

| 功能 | 操作 |
|------|------|
| 搜索网络 | `/` 聚焦搜索框，输入即时过滤，`Esc` 清空 |
| 选择网络 | 鼠标点击，或 `↑` `↓` |
| 显示 / 隐藏密码 | 点眼睛图标，或 `Enter` |
| 一键全部显隐 | 侧栏「全部显示 / 全部隐藏」按钮；`Esc` = 全部隐藏（防投屏/截图泄漏） |
| 复制密码 | 「复制密码」按钮或 `C`（提示不出现明文） |
| 二维码分享 | 「二维码」按钮，手机扫码直连（本地生成，可扫） |
| 刷新 | 左上角 `↻` |

已连接的网络会置顶并默认选中（若系统「位置」服务未开启导致查询受限，会降级显示，不影响密码查看）。

## 开发流程（Matt Pocock 技能包驱动）

1. ✅ HTML 原型先行（`prototype/`，三个结构不同的变体 + 截图存档）
2. ✅ 用户视角评审与迭代（`docs/review-round-1.md` → 原型 v2 落实 P0）
3. ✅ TDD 实现（`tests/` 26 个测试；`docs/PRD.md` 约定测试缝）
4. ✅ 真实机器集成冒烟（`scripts/smoke_real.py`，密码仅打印长度）
5. ⏳ GitHub CLI 管理文档与版本

## 目录结构

```
wifi_pass_viewer/     # 应用（Python + pywebview + WebView2）
  app.py              # 入口与 JS API 桥
  scanner.py          # netsh 解析（纯函数）与扫描器
  qrshare.py          # WiFi 二维码载荷与矩阵
  ui/                 # 界面（原型 B 定稿）
tests/                # pytest 夹具与测试
prototype/            # 原型（一次性产物，含 shots 截图）
scripts/smoke_real.py # 真实数据冒烟（脱敏输出）
docs/                 # PRD、评审记录、应用截图
run.bat               # 双击启动
```

## 界面截图（docs/app-shots/）

| 状态 | 截图 |
|------|------|
| 默认（遮罩 + 已连接置顶） | `01-loaded.png` |
| 显示密码 | `02-revealed.png` |
| 开放网络（给出原因） | `03-open-network.png` |
| 二维码分享 | `04-qr.png` |
| Esc 全部隐藏 | `05-esced.png` |
| 真实运行（本机 24 个网络） | `real-01.png` |

## 测试

```bash
py -m pytest -q        # 26 passed
py scripts/smoke_real.py   # 真实 netsh 冒烟（不输出密码明文）
```

## 打包 exe（可选，未在范围）

```bash
pyinstaller --noconsole --name wifi-pass-viewer --add-data "wifi_pass_viewer/ui;wifi_pass_viewer/ui" wifi_pass_viewer/app.py
```
