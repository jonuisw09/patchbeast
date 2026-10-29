"""Apply ``apt`` updates and restart affected services."""

from __future__ import annotations

import shutil
from typing import TypedDict

from . import config
from .scanner import DetectedComponent, apt_candidate, apt_installed_version
from .utils import log, run, sudo_prefix

__all__ = [
    "SERVICE_MAP",
    "restart_service",
    "refresh_index",
    "check_updates",
    "update_package",
    "list_upgradable",
    "upgrade_system",
    "update_all",
]


SERVICE_MAP: dict[str, str] = {
    "php": "php-fpm",
    "apache2": "apache2",
    "nginx": "nginx",
    "mariadb-server": "mariadb",
    "postgresql": "postgresql",
    "redis-server": "redis-server",
}


class ComponentUpdate(TypedDict):
    """A pending component upgrade from installed to candidate version."""

    name: str
    package: str
    installed: str
    candidate: str


class UpdateResult(TypedDict):
    """Outcome of updating a single package."""

    package: str
    success: bool
    output: str


def restart_service(service: str) -> tuple[bool, str]:
    """Restart a systemd *service*; returns ``(ok, output)``."""
    if not service:
        return True, "no service"
    if not shutil.which("systemctl"):
        return False, "systemctl not available"
    code, out, err = run(f"{sudo_prefix()}systemctl restart {service}", timeout=120)
    text = (out + "\n" + err).strip()
    log(f"restart {service} rc={code}")
    return code == 0, text


def refresh_index() -> tuple[bool, str]:
    """Run ``apt-get update`` and return ``(ok, output)``."""
    code, out, err = run(f"{sudo_prefix()}apt-get update", timeout=300)
    log(f"apt-get update rc={code}")
    return code == 0, (out + err).strip()


def check_updates(components: list[DetectedComponent]) -> list[ComponentUpdate]:
    """Compare installed vs. candidate versions for apt-backed components."""
    updates: list[ComponentUpdate] = []
    for comp in components:
        pkg = comp.get("package")
        if not pkg or not comp.get("installed"):
            continue
        candidate = apt_candidate(pkg)
        installed = apt_installed_version(pkg) or comp.get("version", "")
        if candidate and candidate != installed:
            updates.append(
                ComponentUpdate(
                    name=comp["name"],
                    package=pkg,
                    installed=installed,
                    candidate=candidate,
                )
            )
    return updates


def update_package(package: str) -> tuple[bool, str]:
    """Upgrade *package* via ``apt-get install --only-upgrade``.

    Restarts the mapped service (see :data:`SERVICE_MAP`) on success.
    """
    config.ensure_dirs()
    code, out, err = run(
        f"{sudo_prefix()}apt-get install -y --only-upgrade {package}",
        timeout=600,
    )
    text = (out + "\n" + err).strip()
    if code == 0:
        service = SERVICE_MAP.get(package)
        if service:
            _, restart_text = restart_service(service)
            text = f"{text}\n{restart_text}"
    log(f"update {package} rc={code}")
    return code == 0, text


def list_upgradable() -> list[str]:
    """List system-wide upgradable packages via simulated ``apt-get upgrade``."""
    code, out, _ = run("LC_ALL=C apt-get -s upgrade", timeout=300)
    del code
    packages: list[str] = []
    for line in (out or "").splitlines():
        if line.startswith("Inst "):
            parts = line.split()
            if len(parts) > 1:
                packages.append(parts[1])
    return packages


def upgrade_system() -> tuple[bool, str]:
    """Run a full ``apt-get upgrade -y`` and return ``(ok, output)``."""
    code, out, err = run(f"{sudo_prefix()}apt-get upgrade -y", timeout=1800)
    text = (out + "\n" + err).strip()
    log(f"system upgrade rc={code}")
    return code == 0, text


def update_all(components: list[DetectedComponent]) -> list[UpdateResult]:
    """Upgrade every component that has a newer candidate version."""
    results: list[UpdateResult] = []
    for comp in components:
        pkg = comp.get("package")
        if not pkg or not comp.get("installed"):
            continue
        candidate = apt_candidate(pkg)
        installed = apt_installed_version(pkg) or comp.get("version", "")
        if candidate and candidate != installed:
            ok, text = update_package(pkg)
            results.append(UpdateResult(package=pkg, success=ok, output=text))
    return results
