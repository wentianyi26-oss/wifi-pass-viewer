"""netsh 输出的解析与扫描。

纯解析函数（decode_output / parse_*）与运行器注入的 WindowsWifiScanner 分离，
便于在测试中用夹具数据在"缝"上验证行为。
"""

from __future__ import annotations

from wifi_pass_viewer.models import ProfileDetail

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


_PROFILE_LABELS = ("所有用户配置文件", "All User Profile")


def parse_profiles(text: str) -> list[str]:
    """从 `netsh wlan show profiles` 的输出中提取配置文件（SSID）名。

    按出现顺序返回并去重；忽略组策略段落里的"无/<None>"等非配置行。
    """
    names: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        for label in _PROFILE_LABELS:
            if s.startswith(label) and ":" in s:
                value = s.split(":", 1)[1].strip()
                if value and value not in names:
                    names.append(value)
    return names


def _first_value(text: str, labels: tuple[str, ...]) -> str | None:
    """取第一个以 label 开头行的冒号后的值（去掉两侧空白，保留值内冒号）。"""
    for line in text.splitlines():
        s = line.strip()
        for label in labels:
            if s.startswith(label):
                rest = s[len(label):].lstrip()  # netsh 标签与冒号之间有对齐空格
                if rest[:1] in (":", "："):
                    return rest[1:].strip()
    return None


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
