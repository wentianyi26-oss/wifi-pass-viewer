"""数据模型：解析结果与扫描结果的类型定义。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProfileDetail:
    authentication: str | None = None
    cipher: str | None = None
    password: str | None = None

    @property
    def has_password(self) -> bool:
        return self.password is not None


@dataclass
class InterfaceStatus:
    available: bool = False
    connected_ssid: str | None = None
    state: str | None = None


@dataclass
class Network:
    ssid: str
    authentication: str | None = None
    cipher: str | None = None
    password: str | None = None
    has_password: bool = False
    connected: bool = False
    note: str | None = None

    @classmethod
    def from_detail(cls, ssid: str, detail: "ProfileDetail | None", connected: bool) -> "Network":
        """组装一个网络；detail 为空（读取失败）或无法取得密码时给出 note 说明。"""
        if detail is None or (detail.authentication is None and detail.password is None):
            return cls(ssid=ssid, connected=connected, note="读取失败（可尝试刷新）")
        network = cls(
            ssid=ssid,
            connected=connected,
            authentication=detail.authentication,
            cipher=detail.cipher,
        )
        if detail.has_password:
            network.password = detail.password
            network.has_password = True
        else:
            network.note = no_password_reason(detail.authentication)
        return network

    def to_dict(self) -> dict:
        return {
            "ssid": self.ssid,
            "authentication": self.authentication,
            "cipher": self.cipher,
            "password": self.password,
            "has_password": self.has_password,
            "connected": self.connected,
            "note": self.note,
        }


def no_password_reason(authentication: str | None) -> str:
    """无法取得密码时，向用户解释原因（开放网络 / 企业网络 / 其他）。"""
    auth = (authentication or "").strip()
    low = auth.lower()
    if auth.startswith(("打开", "开放")) or low.startswith("open"):
        return "开放网络（无密码）"
    if "企业" in auth or "enterprise" in low:
        return "企业网络（802.1X），无预共享密码"
    return "该网络没有保存密码"


@dataclass
class ScanResult:
    networks: list[Network]
    connected_available: bool = False
    note: str | None = None

    def to_dict(self) -> dict:
        return {
            "networks": [n.to_dict() for n in self.networks],
            "connected_available": self.connected_available,
            "note": self.note,
        }
