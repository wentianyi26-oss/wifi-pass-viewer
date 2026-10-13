from wifi_pass_viewer.scanner import decode_output


def test_utf8_bytes_decode_correctly():
    text = "接口 WLAN 上的配置文件"
    assert decode_output(text.encode("utf-8")) == text


def test_gbk_bytes_decode_correctly():
    text = "接口 WLAN 上的配置文件"
    assert decode_output(text.encode("gbk")) == text


def test_undecodable_bytes_do_not_raise():
    out = decode_output(b"\xff\xfe\x00abc")
    assert "abc" in out
