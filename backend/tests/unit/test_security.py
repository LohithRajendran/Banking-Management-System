"""
Unit Tests for Core Security & Auth Utilities
"""

import pytest
from core.security import hash_password, verify_password, create_access_token, decode_token


@pytest.mark.unit
def test_password_hashing():
    password = "MySecretPassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


@pytest.mark.unit
def test_jwt_token_generation_and_decoding():
    data = {"sub": "123"}
    token = create_access_token(data)
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "123"
    assert decoded["type"] == "access"
