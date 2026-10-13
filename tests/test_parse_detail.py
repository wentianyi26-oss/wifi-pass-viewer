from pathlib import Path

from wifi_pass_viewer.scanner import parse_profile_detail

FIXTURES = Path(__file__).parent / "fixtures"


def test_wpa2_detail_with_password_containing_colon():
    text = (FIXTURES / "detail_zh_wpa2.txt").read_text(encoding="utf-8")
    detail = parse_profile_detail(text)
    assert detail.authentication == "WPA2 - 个人"
    assert detail.cipher == "CCMP"
    assert detail.password == "Home:Pass:123"
    assert detail.has_password is True


def test_open_network_has_no_password():
    text = (FIXTURES / "detail_zh_open.txt").read_text(encoding="utf-8")
    detail = parse_profile_detail(text)
    assert detail.authentication == "开放式"
    assert detail.password is None
    assert detail.has_password is False


def test_enterprise_network_has_no_password():
    text = (FIXTURES / "detail_zh_enterprise.txt").read_text(encoding="utf-8")
    detail = parse_profile_detail(text)
    assert detail.authentication == "WPA2 - 企业"
    assert detail.password is None


def test_english_detail():
    text = (FIXTURES / "detail_en_wpa2.txt").read_text(encoding="utf-8")
    detail = parse_profile_detail(text)
    assert detail.authentication == "WPA2-Personal"
    assert detail.password == "testpass123"


def test_empty_text_yields_empty_detail():
    detail = parse_profile_detail("")
    assert detail.authentication is None
    assert detail.password is None
    assert detail.has_password is False
