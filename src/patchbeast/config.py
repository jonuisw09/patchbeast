"""Persistent configuration stored under ``~/.config/patchbeast/``."""

from __future__ import annotations

import json
import os
from typing import Any, TypedDict

__all__ = [
    "CONFIG_DIR",
    "CONFIG_FILE",
    "LOG_FILE",
    "CACHE_DIR",
    "DEFAULT_CONFIG",
    "ensure_dirs",
    "load",
    "save",
]

CONFIG_DIR: str = os.path.join(os.path.expanduser("~"), ".config", "patchbeast")
CONFIG_FILE: str = os.path.join(CONFIG_DIR, "config.json")
LOG_FILE: str = os.path.join(CONFIG_DIR, "patchbeast.log")
CACHE_DIR: str = os.path.join(CONFIG_DIR, "cache")


class Config(TypedDict, total=False):
    """Known configuration keys (all optional with defaults)."""

    schedule: str
    schedule_days: int
    auto_update: bool
    dry_run: bool
    components: list[str]


DEFAULT_CONFIG: Config = {
    "schedule": "manual",
    "schedule_days": 30,
    "auto_update": False,
    "dry_run": False,
    "components": [],
}


def ensure_dirs() -> None:
    """Create the config and cache directories if missing."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)


def load() -> Config:
    """Load config from disk, falling back to defaults on any error."""
    ensure_dirs()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding="utf-8") as fh:
                data: dict[str, Any] = json.load(fh)
            merged: Config = dict(DEFAULT_CONFIG)
            merged.update(data)  # type: ignore[typeddict-item]
            return merged
        except (OSError, ValueError):
            return dict(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def save(cfg: Config) -> None:
    """Persist *cfg* to disk as pretty-printed JSON."""
    ensure_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)
