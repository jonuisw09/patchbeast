"""Shared subprocess, version-parsing and logging helpers."""

from __future__ import annotations

import datetime
import os
import re
import subprocess

__all__ = ["run", "is_root", "sudo_prefix", "parse_version", "version_tuple", "log"]


def run(cmd: str, timeout: int = 120, capture: bool = True) -> tuple[int, str, str]:
    """Run *cmd* via the shell and return ``(returncode, stdout, stderr)``.

    Timeouts and unexpected errors are normalized to return code ``-1``
    instead of raising, because callers treat command failure as data.
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout or "", result.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as exc:  # noqa: BLE001 - normalized into the triple
        return -1, "", str(exc)


def is_root() -> bool:
    """Return True when the process runs with uid 0."""
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def sudo_prefix() -> str:
    """Return ``""`` as root, otherwise ``"sudo "`` for privileged commands."""
    return "" if is_root() else "sudo "


def parse_version(text: str) -> str:
    """Extract the first ``X.Y[.Z]`` version token from *text*."""
    match = re.search(r"(\d+\.\d+(?:\.\d+)?(?:[-+~][A-Za-z0-9.]+)?)", text)
    return match.group(1) if match else ""


def version_tuple(value: str) -> tuple[int, ...]:
    """Convert a version string into a comparable int tuple."""
    parts = re.findall(r"\d+", value)
    return tuple(int(x) for x in parts) if parts else (0,)


def log(msg: str, path: str | None = None) -> None:
    """Append *msg* with a timestamp to the PatchBeast log file."""
    if path is None:
        from .config import LOG_FILE

        path = LOG_FILE
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.datetime.now().isoformat()} {msg}\n")
    except OSError:
        pass
