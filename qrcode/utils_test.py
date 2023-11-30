from qrcode.utils import get_data_codewords_per_short_block


def test_get_data_codewords_per_block():
    assert get_data_codewords_per_short_block(ecl="H", version=4) == 9
