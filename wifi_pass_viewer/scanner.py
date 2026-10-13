"""netsh 输出的解析与扫描。

纯解析函数（decode_output / parse_*）与运行器注入的 WindowsWifiScanner 分离，
便于在测试中用夹具数据在"缝"上验证行为。
"""

from __future__ import annotations

import subprocess

from wifi_pass_viewer.models import InterfaceStatus, Network, ProfileDetail, ScanResult

_ENCODINGS = ("utf-8", "gbk", "cp936", "latin-1")


def decode_output(raw: bytes) -> str:
    """把 netsh 的原始输出解码为文本。

    netsh 的输出编码随环境（控制台代码页）而变，可能是 UTF-8 或本地代码页
    （简体中文即 GBK）。逐个候选编码尝试，全失败时用替换字符兜底，保证不抛异常。
    """
    for enc in _ENCODINGS:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _value_after_label(line: str, labels: tuple[str, ...]) -> str | None:
    """单行解析：返回 label 之后、冒号后面的值（两侧去空白，保留值内冒号）。"""
    s = line.strip()
    for label in labels:
        if s.startswith(label):
            rest = s[len(label):].lstrip()  # netsh 标签与冒号之间有对齐空格
            if rest[:1] in (":", "："):
                return rest[1:].strip()
    return None


def _first_value(text: str, labels: tuple[str, ...]) -> str | None:
    for line in text.splitlines():
        value = _value_after_label(line, labels)
        if value is not None:
            return value
    return None


_PROFILE_LABELS = ("所有用户配置文件", "All User Profile")


def parse_profiles(text: str) -> list[str]:
    """从 `netsh wlan show profiles` 的输出中提取配置文件（SSID）名。

    按出现顺序返回并去重；忽略组策略段落里的"无/<None>"等非配置行。
    """
    names: list[str] = []
    for line in text.splitlines():
        value = _value_after_label(line, _PROFILE_LABELS)
        if value and value not in names:
            names.append(value)
    return names


def parse_profile_detail(text: str) -> ProfileDetail:
    """解析 `netsh wlan show profile name=X key=clear` 的输出。

    中英文标签兼容；"关键内容 / Key Content" 是密码唯一可靠来源，
    开放网络与企业网络没有该行，返回 password=None。
    """
    return ProfileDetail(
        authentication=_first_value(text, ("身份验证", "Authentication")),
        cipher=_first_value(text, ("密码", "Cipher")),
        password=_first_value(text, ("关键内容", "Key Content")) or None,
    )


_CONNECTED_STATES = ("已连接", "connected")


def parse_interfaces(text: str) -> InterfaceStatus:
    """解析 `netsh wlan show interfaces` 的输出。

    找到 状态/State 行即认为接口信息可用；仅"已连接"的接口才取其 SSID。
    权限/位置服务受限时 netsh 只报错、不输出状态行，此时 available=False（优雅降级）。
    """
    available = False
    connected_ssid: str | None = None
    state: str | None = None
    for line in text.splitlines():
        if _value_after_label(line, ("名称", "Name")) is not None:
            state = None  # 新接口块开始
            continue
        value = _value_after_label(line, ("状态", "State"))
        if value is not None:
            available = True
            state = value
            continue
        value = _value_after_label(line, ("SSID",))
        if value and state in _CONNECTED_STATES and connected_ssid is None:
            connected_ssid = value
    return InterfaceStatus(
        available=available,
        connected_ssid=connected_ssid,
        state=state if available else None,
    )


def _default_runner(args: list[str], timeout: float = 20.0) -> bytes:
    """真实运行器：调 netsh 并返回 stdout 原始字节（不弹控制台窗口）。"""
    proc = subprocess.run(
        args,
        capture_output=True,
        timeout=timeout,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    return proc.stdout


_ERROR_MARKERS = ("未运行", "not running", "返回错误", "error", "错误", "异常")


def _looks_like_error(text: str) -> bool:
    low = text.lower()
    return any(marker.lower() in low for marker in _ERROR_MARKERS)


def _first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return "netsh 未返回任何内容"


class WindowsWifiScanner:
    """扫描本机已保存的 WiFi：列表 → 逐个详情（含密码）→ 连接状态。"""

    def __init__(self, runner=None):
        self._run = runner or _default_runner

    def scan(self) -> ScanResult:
        profiles_text = decode_output(self._run(["netsh", "wlan", "show", "profiles"]))
        names = parse_profiles(profiles_text)
        if not names and _looks_like_error(profiles_text):
            # 服务未运行/权限异常等情况：把 netsh 的报错原文交给界面展示
            raise RuntimeError(_first_non_empty_line(profiles_text))

        try:
            interface_text = decode_output(self._run(["netsh", "wlan", "show", "interfaces"]))
            interface = parse_interfaces(interface_text)
        except Exception:
            interface = InterfaceStatus(available=False)

        networks = [self._read_network(name, interface.connected_ssid) for name in names]
        note = None
        if not interface.available:
            note = "无法获取当前连接状态（可能需要开启“位置”服务，不影响密码查看）"
        return ScanResult(networks=networks, connected_available=interface.available, note=note)

    def _read_network(self, ssid: str, connected_ssid: str | None) -> Network:
        detail = None
        try:
            text = decode_output(
                self._run(["netsh", "wlan", "show", "profile", f"name={ssid}", "key=clear"])
            )
            detail = parse_profile_detail(text)
        except Exception:
            detail = None
        return Network.from_detail(ssid, detail, connected=(ssid == connected_ssid))
