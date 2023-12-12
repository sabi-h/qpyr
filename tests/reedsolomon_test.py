from qpyr._lib.error_correction import add_ecc_and_interleave


def test__add_ecc_and_interleave():
    data = bytearray(b"@V\x86V\xc6\xc6\xf0\xec\x11\xec\x11\xec\x11\xec\x11\xec")
    data_and_ecc = add_ecc_and_interleave(version=1, ecl="M", data=data)
    expected_result = bytearray(
        b"@V\x86V\xc6\xc6\xf0\xec\x11\xec\x11\xec\x11\xec\x11\xec\x16O\xdf\xd4\x8c\x11\xd1\\/\xb7"
    )
    assert data_and_ecc == expected_result
