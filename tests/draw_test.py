from qrcode.draw import get_format_information


def test_get_format_information():
    result_format_info = get_format_information("M", 5)
    expected_format_info = 16590
    assert result_format_info == expected_format_info
