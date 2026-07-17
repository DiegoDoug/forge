import time

from app.core.security import (
    VaultCrypto,
    hash_master_password,
    issue_session_token,
    verify_master_password,
    verify_session_token,
)


def test_vault_crypto_round_trip():
    crypto = VaultCrypto()
    ciphertext = crypto.encrypt_str("a very secret value")
    assert crypto.decrypt_str(ciphertext) == "a very secret value"
    assert ciphertext != b"a very secret value"


def test_vault_crypto_ciphertext_is_nondeterministic():
    # Same plaintext, different nonce each time -> different ciphertext,
    # which is what makes this authenticated encryption rather than a
    # lookup-able hash.
    crypto = VaultCrypto()
    a = crypto.encrypt_str("same value")
    b = crypto.encrypt_str("same value")
    assert a != b


def test_master_password_hash_verifies_correct_and_rejects_wrong():
    hashed = hash_master_password("correct-horse-battery-staple")
    assert verify_master_password("correct-horse-battery-staple", hashed) is True
    assert verify_master_password("wrong-password", hashed) is False


def test_session_token_round_trip():
    password_hash = hash_master_password("some-password")
    token = issue_session_token(password_hash, ttl_minutes=60)
    assert verify_session_token(token, password_hash) is True


def test_session_token_rejects_wrong_password_hash():
    token = issue_session_token(hash_master_password("password-a"), ttl_minutes=60)
    other_hash = hash_master_password("password-b")
    assert verify_session_token(token, other_hash) is False


def test_session_token_rejects_expired():
    password_hash = hash_master_password("some-password")
    # ttl_minutes=0 means the expiry timestamp is "now" -> already elapsed
    # by the time verify_session_token checks it against a fresh time.time().
    token = issue_session_token(password_hash, ttl_minutes=0)
    time.sleep(1.1)
    assert verify_session_token(token, password_hash) is False


def test_session_token_rejects_malformed():
    password_hash = hash_master_password("some-password")
    assert verify_session_token("not-a-real-token", password_hash) is False
