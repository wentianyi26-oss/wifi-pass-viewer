from pathlib import Path

from wifi_pass_viewer.scanner import parse_profiles

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_chinese_profiles_preserves_order_and_spaces():
    text = (FIXTURES / "profiles_zh.txt").read_text(encoding="utf-8")
    assert parse_profiles(text) == [
        "HomeWiFi_5G",
        "星巴克-免费WiFi",
        "FB-社区 yxr",
        "Office_5G",
    ]


def test_parse_english_profiles():
    text = (FIXTURES / "profiles_en.txt").read_text(encoding="utf-8")
    assert parse_profiles(text) == ["HomeNet", "Cafe_Guest", "Office-Annex"]


def test_parse_profiles_dedupes_and_ignores_noise():
    text = (
        "用户配置文件\n"
        "-------------\n"
        "    所有用户配置文件 : A\n"
        "    所有用户配置文件 : A\n"
        "    SSID 名称 : 不该出现\n"
        "    所有用户配置文件 : B\n"
    )
    assert parse_profiles(text) == ["A", "B"]


def test_parse_profiles_with_no_profiles():
    text = "用户配置文件\n-------------\n    无\n"
    assert parse_profiles(text) == []
