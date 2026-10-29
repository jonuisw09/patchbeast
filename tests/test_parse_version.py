"""Tests for version parsing helpers."""

from patchbeast.utils import parse_version, version_tuple


def test_parse_version_simple() -> None:
    assert parse_version("nginx version: nginx/1.24.0") == "1.24.0"


def test_parse_version_empty() -> None:
    assert parse_version("no version here") == ""


def test_parse_version_debian_suffix() -> None:
    assert parse_version("1.24.0-1ubuntu1") == "1.24.0-1ubuntu1"


def test_version_tuple_orders() -> None:
    assert version_tuple("1.24.0") > version_tuple("1.18.0")
    assert version_tuple("") == (0,)
