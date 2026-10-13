# WiFi 密码查看器（WiFi Pass Viewer）

一个用来**便捷查看本机已保存的 WiFi 密码**的 Windows 小工具。

- 数据来源：Windows 本机 `netsh wlan` 存档（即这台电脑曾经输入并保存过的 WiFi）
- 定位：个人自用、单机、只读；不联网、不上传任何数据

## 开发流程（已接入 Matt Pocock 技能包）

1. ✅ **HTML 原型先行**（`prototype/`，不做实现代码，先评审界面）
2. ✅ **用户视角评审 + 迭代**（`docs/review-round-1.md`）
3. ⏳ 按评审结论开发实现（TDD + code-review）
4. ⏳ GitHub CLI 管理文档与版本

## 目录结构

```
prototype/            # 原型（一次性产物）：ui-prototype.html 双击即可打开
  shots/              # 原型截图存档
docs/                 # 需求、评审、决策文档
```

## 原型怎么看

双击 `prototype/ui-prototype.html`，或浏览器打开：

```
file:///C:/Users/wty/wifi-pass-viewer/prototype/ui-prototype.html
```

- 3 个结构不同的界面变体：`?variant=A` 卡片网格 / `B` 主从分栏 / `C` 控制台表格
- 底部浮动条或键盘 `←` `→` 切换变体
