from qrcode.utils import get_total_data_capacity_bytes


def test_get_data_codewords_per_block():
    assert get_total_data_capacity_bytes(ecl="H", version=11) == 140
