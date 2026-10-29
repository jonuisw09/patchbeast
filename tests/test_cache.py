"""Tests for the on-disk detection cache."""

from __future__ import annotations

import time

from patchbeast import scanner
from patchbeast.scanner import DetectedComponent


def _isolate_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(scanner.config, "CACHE_DIR", str(tmp_path))
    monkeypatch.setattr(scanner.config, "CONFIG_DIR", str(tmp_path))


def test_save_and_load_roundtrip(tmp_path, monkeypatch) -> None:
    _isolate_cache(tmp_path, monkeypatch)
    comps = [
        DetectedComponent(
            name="Nginx",
            command="nginx",
            installed=True,
            version="1.24.0",
            path="/usr/sbin/nginx",
            package="nginx",
        )
    ]
    scanner.save_detection(comps)
    assert scanner.load_detection() == comps


def test_stale_cache_returns_none(tmp_path, monkeypatch) -> None:
    _isolate_cache(tmp_path, monkeypatch)
    scanner.save_detection([])
    # Force staleness by backdating the file content timestamp.
    import json

    cache_file = tmp_path / "detection.json"
    payload = json.loads(cache_file.read_text(encoding="utf-8"))
    payload["timestamp"] = time.time() - 10_000
    cache_file.write_text(json.dumps(payload), encoding="utf-8")
    assert scanner.load_detection(max_age_seconds=60) is None


def test_missing_cache_returns_none(tmp_path, monkeypatch) -> None:
    _isolate_cache(tmp_path, monkeypatch)
    assert scanner.load_detection() is None


def test_corrupt_cache_returns_none(tmp_path, monkeypatch) -> None:
    _isolate_cache(tmp_path, monkeypatch)
    (tmp_path / "detection.json").write_text("{not json", encoding="utf-8")
    assert scanner.load_detection() is None


def test_cached_detect_uses_fresh_cache(tmp_path, monkeypatch) -> None:
    _isolate_cache(tmp_path, monkeypatch)
    scanner.save_detection([])

    def _fail(*args, **kwargs):
        raise AssertionError("live detect() must not run with fresh cache")

    monkeypatch.setattr(scanner, "detect", _fail)
    assert scanner.cached_detect() == []


def test_cached_detect_falls_back_to_live(tmp_path, monkeypatch) -> None:
    _isolate_cache(tmp_path, monkeypatch)
    sentinel = [
        DetectedComponent(
            name="Git", command="git", installed=True, version="2.0",
            path="/usr/bin/git", package="git",
        )
    ]
    monkeypatch.setattr(scanner, "detect", lambda: sentinel)
    assert scanner.cached_detect() == sentinel
    # Second call must come from cache even if live detect breaks.
    monkeypatch.setattr(scanner, "detect", lambda: (_ for _ in ()).throw(AssertionError("stale")))
    assert scanner.cached_detect() == sentinel
