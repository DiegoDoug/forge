import pytest

from app.core.errors import AppError
from app.services.crypto import service


def test_base64_round_trip():
    assert service.base64_decode(service.base64_encode("hello forge")) == "hello forge"


def test_base64_url_safe_round_trip():
    text = "a/b+c==?"
    assert service.base64_decode(service.base64_encode(text, url_safe=True), url_safe=True) == text


def test_base64_decode_rejects_garbage():
    with pytest.raises(AppError):
        service.base64_decode("not base64 at all !!!")


def test_hash_is_deterministic_and_algorithm_specific():
    a = service.hash_text("forge", "sha256")
    b = service.hash_text("forge", "sha256")
    c = service.hash_text("forge", "sha512")
    assert a == b
    assert a != c
    assert len(a) == 64  # sha256 hex digest length


def test_hash_rejects_unknown_algorithm():
    with pytest.raises(AppError):
        service.hash_text("x", "sha999")


def test_verify_hash_matches_and_rejects():
    digest = service.hash_text("secret", "sha256")
    assert service.verify_hash("secret", "sha256", digest) is True
    assert service.verify_hash("wrong", "sha256", digest) is False


def test_aes_round_trip():
    result = service.aes_encrypt("top secret plaintext", "correct-horse-battery-staple")
    decrypted = service.aes_decrypt(result["ciphertext"], result["nonce"], result["salt"], "correct-horse-battery-staple")
    assert decrypted == "top secret plaintext"


def test_aes_wrong_passphrase_fails():
    result = service.aes_encrypt("data", "right-passphrase")
    with pytest.raises(AppError):
        service.aes_decrypt(result["ciphertext"], result["nonce"], result["salt"], "wrong-passphrase")


def test_jwt_build_decode_verify_round_trip():
    secret = "a-sufficiently-long-shared-secret-for-hs256"
    token = service.jwt_build({"sub": "user-1"}, secret, "HS256")

    decoded = service.jwt_decode_unverified(token)
    assert decoded["payload"]["sub"] == "user-1"

    verified = service.jwt_verify(token, secret, "HS256")
    assert verified["valid"] is True

    wrong = service.jwt_verify(token, "a-different-long-enough-secret-value", "HS256")
    assert wrong["valid"] is False


def test_jwt_build_rejects_unknown_algorithm():
    with pytest.raises(AppError):
        service.jwt_build({}, "secret", "RS256")


def test_rsa_round_trip():
    keys = service.rsa_generate_keypair(2048)
    ciphertext = service.rsa_encrypt(keys["public_key"], "hello via RSA")
    assert service.rsa_decrypt(keys["private_key"], ciphertext) == "hello via RSA"


def test_rsa_rejects_bad_key_size():
    with pytest.raises(AppError):
        service.rsa_generate_keypair(1024)


def test_ecc_sign_and_verify():
    keys = service.ecc_generate_keypair()
    signature = service.ecc_sign(keys["private_key"], "message to sign")
    assert service.ecc_verify(keys["public_key"], "message to sign", signature) is True
    assert service.ecc_verify(keys["public_key"], "tampered message", signature) is False
