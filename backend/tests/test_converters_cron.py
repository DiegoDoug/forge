"""Baseline characterization tests for the Converters cron tool.

Written as part of Universal Converter (Phase 04) Milestone 1, before any
production code in this phase changes — `cron.py` has shipped with zero test
coverage until now. These pin the current, real behavior so any later
regression (e.g. while this module is exposed through the new
`ConverterProvider` surface) is a failing test, not a hunch.
"""

from __future__ import annotations

import pytest

from app.core.errors import AppError
from app.services.converters import cron


def test_parse_cron_valid_expression_returns_description_and_default_count():
    result = cron.parse_cron("30 4 * * *")
    assert result["description"] == "minute=30, hour=4, day of month=*, month=*, day of week=*"
    assert len(result["next_runs"]) == 5


def test_parse_cron_respects_explicit_count():
    result = cron.parse_cron("0 0 * * *", count=3)
    assert len(result["next_runs"]) == 3


def test_parse_cron_next_runs_are_strictly_increasing_iso_timestamps():
    result = cron.parse_cron("*/15 * * * *", count=4)
    assert result["next_runs"] == sorted(result["next_runs"])
    assert len(set(result["next_runs"])) == 4


def test_parse_cron_rejects_invalid_expression():
    with pytest.raises(AppError):
        cron.parse_cron("not a cron expression")


def test_parse_cron_rejects_out_of_range_field():
    with pytest.raises(AppError):
        cron.parse_cron("99 * * * *")


def test_parse_cron_strips_surrounding_whitespace():
    result = cron.parse_cron("  0 12 * * *  ")
    assert result["description"] == "minute=0, hour=12, day of month=*, month=*, day of week=*"
