"""Tests for component detection and apt queries (mocked subprocess)."""

from __future__ import annotations

from patchbeast import scanner


def test_detect_marks_missing(monkeypatch) -> None:
    monkeypatch.setattr(scanner.shutil, "which", lambda cmd: None)
    comps = scanner.detect()
    assert comps
    assert all(not c["installed"] for c in comps)


def test_detect_parses_version(monkeypatch) -> None:
    monkeypatch.setattr(scanner.shutil, "which", lambda cmd: f"/usr/bin/{cmd}")
    monkeypatch.setattr(scanner, "run", lambda *a, **k: (0, "nginx version: nginx/1.24.0", ""))
    comps = scanner.detect()
    nginx = next(c for c in comps if c["name"] == "Nginx")
    assert nginx["installed"] and nginx["version"] == "1.24.0"


def test_apt_candidate_none_package() -> None:
    assert scanner.apt_candidate(None) == ""


def test_apt_candidate_parses(monkeypatch) -> None:
    out = "nginx:\n  Installed: 1.18.0\n  Candidate: 1.24.0\n"
    monkeypatch.setattr(scanner, "run", lambda *a, **k: (0, out, ""))
    assert scanner.apt_candidate("nginx") == "1.24.0"


def test_apt_candidate_absent(monkeypatch) -> None:
    monkeypatch.setattr(scanner, "run", lambda *a, **k: (0, "Candidate: (none)", ""))
    assert scanner.apt_candidate("nginx") == ""
