import math
import time

import pytest

from app.core.errors import AppError
from app.services.generators import service


def test_password_length_and_charset():
    pw = service.generate_password(length=32, use_symbols=False)
    assert len(pw) == 32
    assert all(c.isalnum() for c in pw)


def test_password_requires_at_least_one_pool():
    with pytest.raises(AppError):
        service.generate_password(use_upper=False, use_lower=False, use_digits=False, use_symbols=False)


def test_password_rejects_out_of_range_length():
    with pytest.raises(AppError):
        service.generate_password(length=2)


def test_password_excludes_ambiguous_characters():
    pw = service.generate_password(length=200, exclude_ambiguous=True)
    assert not any(c in service.AMBIGUOUS for c in pw)


def test_uuid4_is_valid_and_random():
    a, b = service.generate_uuid4(), service.generate_uuid4()
    assert a != b
    assert len(a) == 36


def test_uuid7_is_time_ordered():
    # v7 only guarantees ordering at millisecond granularity (the first 48
    # bits are a timestamp; within the same millisecond, ordering falls back
    # to random bits) — sleep past a millisecond boundary so the comparison
    # is actually meaningful rather than flaky.
    first = service.generate_uuid7()
    time.sleep(0.005)
    second = service.generate_uuid7()
    assert first < second


def test_nanoid_respects_size():
    assert len(service.generate_nanoid(size=10)) == 10
    assert len(service.generate_nanoid(size=1)) == 1


def test_nanoid_rejects_invalid_size():
    with pytest.raises(AppError):
        service.generate_nanoid(size=0)


def test_random_bytes_encodings():
    assert len(service.generate_random_bytes(16, "hex")) == 32
    assert service.generate_random_bytes(16, "base64")
    with pytest.raises(AppError):
        service.generate_random_bytes(16, "not-a-real-encoding")


def test_api_key_has_prefix():
    key = service.generate_api_key("myapp")
    assert key.startswith("myapp_")


def test_entropy_estimate_scales_with_charset_and_length():
    weak = service.estimate_entropy("aaaa")
    strong = service.estimate_entropy("aB3!xQ9#zK2$")
    assert strong["bits"] > weak["bits"]
    assert weak["strength"] in {"very weak", "weak"}


def test_entropy_estimate_matches_known_formula():
    # 8 lowercase-only chars: log2(26) * 8
    result = service.estimate_entropy("abcdefgh")
    assert result["bits"] == pytest.approx(8 * math.log2(26), abs=0.5)
