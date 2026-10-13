from pathlib import Path

from wifi_pass_viewer.scanner import parse_interfaces

FIXTURES = Path(__file__).parent / "fixtures"


def test_connected_interface_chinese():
    text = (FIXTURES / "interfaces_zh_connected.txt").read_text(encoding="utf-8")
    status = parse_interfaces(text)
    assert status.available is True
    assert status.connected_ssid == "HomeWiFi_5G"
    assert status.state == "已连接"


def test_connected_interface_english():
    text = (FIXTURES / "interfaces_en_connected.txt").read_text(encoding="utf-8")
    status = parse_interfaces(text)
    assert status.available is True
    assert status.connected_ssid == "HomeNet"
    assert status.state == "connected"


def test_permission_error_degrades_gracefully():
    text = (FIXTURES / "interfaces_error_zh.txt").read_text(encoding="utf-8")
    status = parse_interfaces(text)
    assert status.available is False
    assert status.connected_ssid is None


def test_empty_text_is_unavailable():
    status = parse_interfaces("")
    assert status.available is False
