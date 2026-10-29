"""Tests for cron expression building."""

from patchbeast.scheduler import cron_expression


def test_daily() -> None:
    assert cron_expression("daily", 30) == "0 2 * * *"


def test_weekly() -> None:
    assert cron_expression("weekly", 30) == "0 2 * * 0"


def test_monthly() -> None:
    assert cron_expression("monthly", 30) == "0 2 1 * *"


def test_custom_interval() -> None:
    assert cron_expression("custom", 7) == "0 2 */7 * *"


def test_custom_clamped() -> None:
    assert cron_expression("custom", 0) == "0 2 */1 * *"


def test_manual_returns_none() -> None:
    assert cron_expression("manual", 30) is None
