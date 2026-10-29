"""Detect installed components and query ``apt`` for version info."""

from __future__ import annotations

import shutil
from typing import TypedDict

from .components import COMPONENTS
from .utils import parse_version, run

__all__ = ["detect", "apt_candidate", "apt_installed_version"]


class DetectedComponent(TypedDict):
    """Result of probing a single component."""

    name: str
    command: str
    installed: bool
    version: str
    path: str
    package: str | None


def detect() -> list[DetectedComponent]:
    """Probe every registered component and return its install status.

    A component counts as installed when its binary is on ``PATH`` and its
    version command yields either exit code 0 or a parseable version string.
    """
    results: list[DetectedComponent] = []
    for comp in COMPONENTS:
        path = shutil.which(comp["command"])
        installed = path is not None
        version = ""
        if installed:
            assert path is not None
            code, out, err = run(f"{comp['command']} {comp['args']} 2>&1", timeout=30)
            version = parse_version(f"{out} {err}".strip())
            if code != 0 and not version:
                installed = False
        results.append(
            DetectedComponent(
                name=comp["name"],
                command=comp["command"],
                installed=installed,
                version=version,
                path=path or "",
                package=comp["package"],
            )
        )
    return results


def apt_candidate(package: str | None) -> str:
    """Return the ``apt`` candidate version for *package*, or ``""``."""
    if not package:
        return ""
    code, out, err = run(f"LC_ALL=C apt-cache policy {package} 2>/dev/null", timeout=60)
    del code, err
    for line in out.splitlines():
        stripped = line.strip()
        if stripped.startswith("Candidate:"):
            value = stripped.split(":", 1)[1].strip()
            if value and value != "(none)":
                return value
    return ""


def apt_installed_version(package: str | None) -> str:
    """Return the installed ``dpkg`` version for *package*, or ``""``."""
    if not package:
        return ""
    code, out, _ = run(f"LC_ALL=C dpkg-query -W -f='${{Version}}' {package} 2>/dev/null", timeout=30)
    return out.strip() if code == 0 else ""
