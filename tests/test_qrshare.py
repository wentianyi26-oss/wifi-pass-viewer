from wifi_pass_viewer.qrshare import make_wifi_payload, matrix_for


def test_payload_escapes_special_characters():
    payload = make_wifi_payload("Home;Net", "pa:ss,wo\\rd")
    assert payload == r"WIFI:T:WPA;S:Home\;Net;P:pa\:ss\,wo\\rd;;"


def test_matrix_is_square_of_booleans():
    matrix = matrix_for("WIFI:T:WPA;S:Home;P:abc123;;")
    assert len(matrix) >= 21
    assert all(len(row) == len(matrix) for row in matrix)
    assert all(isinstance(cell, bool) for row in matrix for cell in row)


def test_different_payloads_produce_different_matrices():
    a = matrix_for("WIFI:T:WPA;S:A;P:1;;")
    b = matrix_for("WIFI:T:WPA;S:B;P:2;;")
    assert a != b
