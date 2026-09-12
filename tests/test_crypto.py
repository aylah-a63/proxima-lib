import os
import pytest
from unittest.mock import patch

TEST_KEY = os.urandom(32)


@pytest.fixture
def mock_key():
    with patch("proxima_lib.crypto._get_or_create_key", return_value=TEST_KEY):
        yield


def test_roundtrip(mock_key):
    from proxima_lib.crypto import encrypt_per, decrypt_per
    data = b"FROM llama3.2\nSYSTEM \"\"\"\nhello\n\"\"\"\n"
    assert decrypt_per(encrypt_per(data)) == data


def test_tamper_detected(mock_key):
    from proxima_lib.crypto import encrypt_per, decrypt_per
    enc = bytearray(encrypt_per(b"secret"))
    enc[-1] ^= 0xFF
    with pytest.raises(Exception):
        decrypt_per(bytes(enc))


def test_plaintext_rejected():
    from proxima_lib.crypto import decrypt_per
    with pytest.raises(ValueError, match="Not an encrypted"):
        decrypt_per(b"FROM llama3.2\n")
