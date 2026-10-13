# PRD · WiFi 密码查看器

> 版本：v1（对应原型 v2 + 评审 round-1 结论）
> 状态：待实现 → 实现中 → 已验收（本文件随开发更新）

## 1. 背景与目标

Windows 会把连过的 WiFi（SSID + 密码）加密存在本机。原生查看路径太绕（设置→网络→管理→属性，还得过 UAC/位置权限），普通用户"找回自家 WiFi 密码"成本高。

**目标**：做一个双击即开的单机小工具，**3 秒内**找到任意已保存 WiFi 的密码并复制/分享。

**用户故事**
- US1：我想找回家里 WiFi 密码，发给新来的客人 → 选中网络→点"复制密码"→发给对方。
- US2：朋友手机要连我的热点，输密码麻烦 → 点"二维码"→对方扫码直连。
- US3：身边有人时，我不想密码晾在屏幕上 → 默认遮罩；`Esc` 一键全部隐藏。
- US4：我记得网络名，一次搜索直达 → `/` 搜索即定位。

## 2. 功能需求（来自原型 v2 + 评审 round-1）

| # | 需求 | 来源 | 验收标准 |
|---|------|------|----------|
| F1 | 列出本机全部已保存 WiFi（含中文/特殊字符名称） | 原型 | 与 `netsh wlan show profiles` 结果一致；列表可滚动 |
| F2 | 查看密码：选中网络后在详情区显示；默认遮罩 | 原型 B | 点眼睛/回车可切换；开放网络/企业网络给出原因而非空白 |
| F3 | 复制密码（无需先显示），提示不出现明文 | 评审 #3 | 点击复制→剪贴板=完整密码；屏上提示为「密码已复制到剪贴板」（不含明文）；失败时提示复制失败 |
| F4 | 二维码分享（真实可扫） | 评审 #4 | 弹窗显示 QR（内容 `WIFI:T:WPA;S:<ssid>;P:<pwd>;;`），手机可扫 |
| F5 | 一键全部显示 / 全部隐藏（按钮 + `Esc`） | 评审 #2 | 按钮随状态换文案；Esc 任意界面全部变遮罩 |
| F6 | 已连接网络置顶 + 默认选中 + 高亮 | 评审 #1 | 若系统能提供连接信息则置顶默认选中；**取不到时不阻塞主功能**，仅弱提示 |
| F7 | 搜索：`/` 聚焦；过滤按名称 | 评审 P1 | 输入即时过滤；空结果有空状态；Esc 清空 |
| F8 | 键盘流：`↑↓` 选择、`Enter` 显隐、`C` 复制 | 评审 P1 | 不干扰输入框打字 |
| F9 | 刷新按钮（重新扫描） | 原型 | 点后重新读取，展示加载态 |
| F10 | 安全说明（不联网/只读/来自本机存档） | 评审 P1 | 窗口底部常驻一行小字 |

## 3. 非功能需求

- **单机离线**：不发起任何网络请求（二维码在本地生成）。
- **只读**：不修改系统配置；不写任何文件。
- **免管理员**：普通用户权限可用（已实测 `show profile key=clear` 免提权）；`show interfaces` 可能需要"位置"服务，属降级项。
- **编码兼容**：netsh 输出可能是 UTF-8 或本地代码页（GBK），需自动兜底。
- **启动快**：双击启动到可用 < 3 秒（实测：本机 24 个配置文件 ≈ 2.8s，顺序调用 netsh）。
- **不落盘敏感数据**：密码只在内存与剪贴板。

## 4. 技术方案

- **UI**：pywebview（WebView2）+ 本地 HTML/CSS/JS —— 直接复用原型 B 的视觉与交互（v2 全部改进）。
- **数据**：Python 调 `netsh wlan`（列表 / 详情 `key=clear` / 接口），纯函数解析成 `Network`。
- **二维码**：`qrcode` 库生成矩阵，前端 canvas 绘制。
- **结构**：

```
wifi_pass_viewer/
  __init__.py
  models.py        # Network / ScanResult（数据模型）
  scanner.py       # decode_output / parse_* 纯函数 + WindowsWifiScanner（注入命令运行器）
  qrshare.py       # 生成二维码矩阵
  app.py           # pywebview 入口 + JS API 桥
  ui/index.html    # 最终界面（原型 B 定稿 + v2 改进）
  ui/style.css
  ui/app.js
tests/             # pytest：缝上的行为测试
run.bat            # 双击启动
```

## 5. 测试缝（TDD 约定，公开接口）

1. `decode_output(bytes) -> str` —— netsh 输出编码兜底（utf-8→gbk→cp936→latin-1）。
2. `parse_profiles(text) -> list[str]` —— 列表解析（中/英标签、去重、忽略无关行）。
3. `parse_profile_detail(text) -> ProfileDetail` —— 详情解析（认证/加密/关键内容/无障碍网络）。
4. `parse_interfaces(text) -> InterfaceStatus` —— 连接状态解析（含错误文本降级）。
5. `WindowsWifiScanner(runner).scan() -> ScanResult` —— 组装（注入假 runner，覆盖异常与降级）。
6. `qrshare.matrix_for(payload) -> list[list[bool]]` —— 二维码矩阵（方形、可区分）。

## 6. 范围外（本轮不做，评审 P2）

导出 CSV/TXT、排序切换、深色主题跟随、托盘/安装器、打包 exe（README 给命令）。
