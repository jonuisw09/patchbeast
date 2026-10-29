"""Install, remove and inspect the recurring ``patchbeast --scan`` cron job."""

from __future__ import annotations

import os
import shutil
import subprocess

from .utils import is_root, log, run

__all__ = ["MARKER", "cron_expression", "install", "remove", "status"]

MARKER = "# patchbeast-managed"


def cron_expression(schedule: str, days: int) -> str | None:
    """Translate a friendly *schedule* name into a cron expression."""
    if schedule == "daily":
        return "0 2 * * *"
    if schedule == "weekly":
        return "0 2 * * 0"
    if schedule == "monthly":
        return "0 2 1 * *"
    if schedule == "custom":
        interval = max(1, int(days))
        return f"0 2 */{interval} * *"
    return None


def _cron_command() -> str:
    exe = shutil.which("patchbeast")
    if exe:
        return f"{exe} --scan"
    return "python3 -m patchbeast --scan"


def install(schedule: str, days: int = 30) -> tuple[bool, str]:
    """Install the cron job for *schedule*; ``manual`` removes it instead."""
    expr = cron_expression(schedule, days)
    if not expr:
        return remove()
    line = f"{expr} {MARKER} {_cron_command()}"
    if is_root():
        path = "/etc/cron.d/patchbeast"
        content = (
            "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n"
            + line
            + "\n"
        )
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            os.chmod(path, 0o644)
            log(f"cron installed {expr}")
            return True, f"Cron installed: {expr}"
        except OSError as exc:
            log(f"cron install failed {exc}")
            return False, str(exc)
    code, out, _ = run("crontab -l 2>/dev/null", timeout=30)
    existing = out if code == 0 else ""
    lines = [ln for ln in existing.splitlines() if MARKER not in ln]
    lines.append(line)
    new = "\n".join(lines) + "\n"
    proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
    proc.communicate(new)
    if proc.returncode != 0:
        return False, "crontab update failed"
    log(f"cron installed {expr}")
    return True, f"Cron installed: {expr}"


def remove() -> tuple[bool, str]:
    """Remove the managed cron job, if present."""
    if is_root():
        path = "/etc/cron.d/patchbeast"
        try:
            if os.path.exists(path):
                os.remove(path)
            log("cron removed")
            return True, "Cron removed"
        except OSError as exc:
            return False, str(exc)
    code, out, _ = run("crontab -l 2>/dev/null", timeout=30)
    existing = out if code == 0 else ""
    lines = [ln for ln in existing.splitlines() if MARKER not in ln]
    new = "\n".join(lines) + ("\n" if lines else "")
    proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
    proc.communicate(new)
    log("cron removed")
    return True, "Cron removed"


def status() -> str:
    """Return the current managed cron line, or a not-installed message."""
    if is_root():
        path = "/etc/cron.d/patchbeast"
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                return fh.read().strip()
        return "No cron job installed"
    code, out, _ = run("crontab -l 2>/dev/null", timeout=30)
    del code
    for line in (out or "").splitlines():
        if MARKER in line:
            return line.strip()
    return "No cron job installed"
