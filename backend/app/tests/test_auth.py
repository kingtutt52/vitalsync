"""
Unit tests for auth utilities.
Run with: pytest app/tests/test_auth.py -v
"""
import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = hash_password("mysecretpassword")
        assert hashed != "mysecretpassword"

    def test_verify_correct_password(self):
        hashed = hash_password("correct-horse-battery")
        assert verify_password("correct-horse-battery", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correct-horse-battery")
        assert verify_password("wrong-password", hashed) is False

    def test_same_password_produces_different_hashes(self):
        h1 = hash_password("same-password")
        h2 = hash_password("same-password")
        # bcrypt salts — hashes must differ
        assert h1 != h2
        # but both should verify
        assert verify_password("same-password", h1)
        assert verify_password("same-password", h2)


class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token(subject="user-123")
        subject = decode_access_token(token)
        assert subject == "user-123"

    def test_tampered_token_returns_none(self):
        token = create_access_token(subject="user-123")
        tampered = token + "x"
        assert decode_access_token(tampered) is None

    def test_garbage_token_returns_none(self):
        assert decode_access_token("not.a.real.token") is None

    def test_empty_token_returns_none(self):
        assert decode_access_token("") is None
