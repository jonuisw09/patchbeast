"""PatchBeast: terminal patch manager for Linux servers."""

from .cli import headless_scan, main
from .scanner import apt_candidate, apt_installed_version, detect
from .updater import check_updates, list_upgradable

__version__ = "1.1.0"

__all__ = [
    "__version__",
    "main",
    "headless_scan",
    "detect",
    "check_updates",
    "list_upgradable",
    "apt_candidate",
    "apt_installed_version",
]
