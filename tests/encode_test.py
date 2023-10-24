from qrcode.encode import get_best_mode
import pytest


@pytest.mark.parametrize(
    "data,expected_mode", [("1234567890", "numeric"), ("OMEGA", "alphanumeric"), ("help@omegaseed.co.uk", "byte")]
)
def test_get_best_mode(data, expected_mode):
    assert get_best_mode(data) == expected_mode
