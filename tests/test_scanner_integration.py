from pathlib import Path

import pytest

from wifi_pass_viewer.scanner import WindowsWifiScanner

FIXTURES = Path(__file__).parent / "fixtures"


def gbk(name: str) -> bytes:
    """夹具用 GBK 字节喂入，顺带验证真实编码链路。"""
    return (FIXTURES / name).read_text(encoding="utf-8").encode("gbk")


class FakeRunner:
    def __init__(self, responses: list[tuple[str, bytes]]):
        self.responses = responses
        self.calls: list[str] = []

    def __call__(self, args: list[str]) -> bytes:
        cmd = " ".join(args)
        self.calls.append(cmd)
        for needle, payload in self.responses:
            if needle in cmd:
                return payload
        raise AssertionError(f"unexpected command: {cmd}")


ALL_DETAILS = {
    "HomeWiFi_5G": "detail_zh_wpa2.txt",
    "星巴克-免费WiFi": "detail_zh_open.txt",
    "FB-社区 yxr": "detail_zh_enterprise.txt",
    "Office_5G": "detail_zh_wpa2.txt",
}


def build_runner(details=None, interfaces="interfaces_zh_connected.txt"):
    responses = [
        ("show profiles", gbk("profiles_zh.txt")),
        ("show interfaces", gbk(interfaces)),
    ]
    for ssid, fixture in (ALL_DETAILS if details is None else details).items():
        responses.append((f"show profile name={ssid}", gbk(fixture)))
    return FakeRunner(responses)


def test_scan_assembles_networks_with_passwords_and_connected_flag():
    result = WindowsWifiScanner(build_runner()).scan()
    assert [n.ssid for n in result.networks] == [
        "HomeWiFi_5G",
        "星巴克-免费WiFi",
        "FB-社区 yxr",
        "Office_5G",
    ]
    home = result.networks[0]
    assert home.has_password is True
    assert home.password == "Home:Pass:123"
    assert home.authentication == "WPA2 - 个人"
    assert home.connected is True
    assert result.connected_available is True
    assert result.networks[1].connected is False


def test_open_network_gets_reason_instead_of_password():
    result = WindowsWifiScanner(build_runner()).scan()
    cafe = result.networks[1]
    assert cafe.has_password is False
    assert cafe.password is None
    assert "开放" in (cafe.note or "")


def test_open_network_reason_supports_legacy_wording():
    """不同 Windows 版本对开放网络的表述可能是"打开"（旧）或"开放式"（新）。"""
    open_text = "安全设置\n    身份验证         : 打开\n    密码                 : 无\n"
    responses = [
        ("show profiles", gbk("profiles_zh.txt")),
        ("show interfaces", gbk("interfaces_error_zh.txt")),
        ("show profile name=HomeWiFi_5G", open_text.encode("utf-8")),
    ]
    result = WindowsWifiScanner(FakeRunner(responses)).scan()
    home = result.networks[0]
    assert "开放" in (home.note or "")


def test_enterprise_network_gets_reason_instead_of_password():
    result = WindowsWifiScanner(build_runner()).scan()
    office = result.networks[2]
    assert office.has_password is False
    assert "企业" in (office.note or "")


def test_interfaces_error_degrades_without_blocking_list():
    result = WindowsWifiScanner(build_runner(interfaces="interfaces_error_zh.txt")).scan()
    assert result.connected_available is False
    assert len(result.networks) == 4
    assert all(not n.connected for n in result.networks)
    assert result.note  # 给界面展示的降级说明


def test_detail_failure_keeps_network_with_note():
    details = dict(ALL_DETAILS)
    del details["Office_5G"]
    runner = build_runner(details=details)
    result = WindowsWifiScanner(runner).scan()
    office = result.networks[3]
    assert office.ssid == "Office_5G"
    assert office.has_password is False
    assert "读取失败" in (office.note or "")


def test_empty_output_detail_is_treated_as_failure():
    details = dict(ALL_DETAILS)
    details["Office_5G"] = None  # FakeRunner 返回空字节串
    responses = [
        ("show profiles", gbk("profiles_zh.txt")),
        ("show interfaces", gbk("interfaces_zh_connected.txt")),
    ]
    for ssid, fixture in details.items():
        payload = gbk(fixture) if fixture else b""
        responses.append((f"show profile name={ssid}", payload))
    result = WindowsWifiScanner(FakeRunner(responses)).scan()
    office = result.networks[3]
    assert office.has_password is False
    assert "读取失败" in (office.note or "")


def test_scan_raises_with_netsh_error_message_when_profiles_empty():
    responses = [
        ("show profiles", gbk("profiles_error_zh.txt")),
        ("show interfaces", gbk("interfaces_error_zh.txt")),
    ]
    with pytest.raises(RuntimeError) as excinfo:
        WindowsWifiScanner(FakeRunner(responses)).scan()
    assert "未运行" in str(excinfo.value)


def test_scan_with_genuinely_empty_profiles_returns_empty_list():
    empty = "接口 WLAN 上的配置文件:\n\n用户配置文件\n-------------\n"
    responses = [
        ("show profiles", empty.encode("utf-8")),
        ("show interfaces", gbk("interfaces_error_zh.txt")),
    ]
    result = WindowsWifiScanner(FakeRunner(responses)).scan()
    assert result.networks == []
