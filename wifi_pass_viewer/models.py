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
