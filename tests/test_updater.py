"""Tests for update planning (no real apt calls)."""

from patchbeast import updater


def test_check_updates_detects_newer(sample_components, monkeypatch) -> None:
    monkeypatch.setattr(updater, "apt_candidate", lambda pkg: "1.24.0" if pkg == "nginx" else "")
    monkeypatch.setattr(updater, "apt_installed_version", lambda pkg: "1.18.0")
    updates = updater.check_updates(sample_components)
    assert len(updates) == 1
    assert updates[0]["package"] == "nginx"
    assert updates[0]["candidate"] == "1.24.0"


def test_check_updates_skips_detect_only(sample_components, monkeypatch) -> None:
    monkeypatch.setattr(updater, "apt_candidate", lambda pkg: "9.9.9")
    monkeypatch.setattr(updater, "apt_installed_version", lambda pkg: "1.0.0")
    updates = updater.check_updates(sample_components)
    assert all(u["package"] is not None for u in updates)
    assert "caddy" not in [u["name"].lower() for u in updates]


def test_check_updates_equal_versions(sample_components, monkeypatch) -> None:
    monkeypatch.setattr(updater, "apt_candidate", lambda pkg: "1.18.0")
    monkeypatch.setattr(updater, "apt_installed_version", lambda pkg: "1.18.0")
    assert updater.check_updates(sample_components) == []


def test_list_upgradable_parses(monkeypatch) -> None:
    out = "Inst nginx [1.18.0] (1.24.0)\nInst curl [7.81.0] (8.0.0)\n"
    monkeypatch.setattr(updater, "run", lambda *a, **k: (0, out, ""))
    assert updater.list_upgradable() == ["nginx", "curl"]


def test_service_map_covers_restarted_packages() -> None:
    assert updater.SERVICE_MAP["nginx"] == "nginx"
    assert updater.SERVICE_MAP["php"] == "php-fpm"
