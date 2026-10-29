"""Tests for config load/save round-trips."""

import json

from patchbeast import config


def test_load_defaults_when_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "CONFIG_DIR", str(tmp_path))
    monkeypatch.setattr(config, "CONFIG_FILE", str(tmp_path / "config.json"))
    monkeypatch.setattr(config, "CACHE_DIR", str(tmp_path / "cache"))
    cfg = config.load()
    assert cfg["schedule"] == "manual"
    assert cfg["dry_run"] is False


def test_save_and_load_roundtrip(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "CONFIG_DIR", str(tmp_path))
    monkeypatch.setattr(config, "CONFIG_FILE", str(tmp_path / "config.json"))
    monkeypatch.setattr(config, "CACHE_DIR", str(tmp_path / "cache"))
    config.save({"dry_run": True})
    assert config.load()["dry_run"] is True


def test_load_corrupt_file(tmp_path, monkeypatch) -> None:
    bad = tmp_path / "config.json"
    bad.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(config, "CONFIG_DIR", str(tmp_path))
    monkeypatch.setattr(config, "CONFIG_FILE", str(bad))
    monkeypatch.setattr(config, "CACHE_DIR", str(tmp_path / "cache"))
    assert config.load()["schedule"] == "manual"
    assert json.loads  # sanity: json module available
