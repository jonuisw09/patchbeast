"""Detect installed components and query ``apt`` for version info."""

from __future__ import annotations

import json
import os
import shutil
import time
from typing import TypedDict

from . import config
from .components import COMPONENTS
from .utils import parse_version, run

__all__ = [
    "detect",
    "cached_detect",
    "save_detection",
    "load_detection",
    "apt_candidate",
    "apt_installed_version",
]

#: Default freshness window (seconds) for the on-disk detection cache.
DEFAULT_CACHE_MAX_AGE = 300

_CACHE_FILENAME = "detection.json"


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


def _cache_path() -> str:
    config.ensure_dirs()
    return os.path.join(config.CACHE_DIR, _CACHE_FILENAME)


def save_detection(components: list[DetectedComponent]) -> None:
    """Persist *components* to the on-disk detection cache."""
    try:
        with open(_cache_path(), "w", encoding="utf-8") as fh:
            json.dump({"timestamp": time.time(), "components": components}, fh)
    except OSError:
        pass


def load_detection(max_age_seconds: int = DEFAULT_CACHE_MAX_AGE) -> list[DetectedComponent] | None:
    """Return the cached detection if fresher than *max_age_seconds*.

    Returns ``None`` when the cache is missing, corrupt, or stale.
    """
    try:
        with open(_cache_path(), encoding="utf-8") as fh:
            payload = json.load(fh)
        timestamp = float(payload.get("timestamp", 0))
        if time.time() - timestamp > max_age_seconds:
            return None
        components = payload.get("components", [])
        return components if isinstance(components, list) else None
    except (OSError, ValueError, AttributeError):
        return None


def cached_detect(max_age_seconds: int = DEFAULT_CACHE_MAX_AGE) -> list[DetectedComponent]:
    """Return cached detection when fresh, otherwise run live ``detect()``.

    Live results are saved to the cache before returning.
    """
    cached = load_detection(max_age_seconds)
    if cached is not None:
        return cached
    components = detect()
    save_detection(components)
    return components


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
