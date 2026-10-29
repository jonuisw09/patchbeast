"""Full-screen views reachable from the PatchBeast main menu."""

from __future__ import annotations

import curses
import os
import time

from .. import config
from ..logo import LOGO
from ..scanner import apt_candidate, detect
from ..scheduler import install as install_cron
from ..scheduler import remove as remove_cron
from ..scheduler import status as cron_status
from ..updater import (
    check_updates,
    list_upgradable,
    refresh_index,
    update_package,
    upgrade_system,
)
from ..utils import is_root, log
from .widgets import draw_logo, pause, safe_addstr

__all__ = [
    "screen_scan",
    "screen_components",
    "screen_check",
    "screen_apply",
    "screen_schedule",
    "screen_logs",
    "screen_settings",
]


def _logo_bottom() -> int:
    """Return the first free row below the ASCII logo."""
    return len(LOGO.strip("\n").split("\n")) + 3


def screen_scan(stdscr: curses.window) -> None:
    """List every known component with its installed/missing status."""
    stdscr.clear()
    draw_logo(stdscr, 1)
    top = _logo_bottom()
    safe_addstr(stdscr, top, 2, "Scanning installed components...", curses.color_pair(1) | curses.A_BOLD)
    stdscr.refresh()
    comps = detect()
    height, _ = stdscr.getmaxyx()
    row = top + 2
    for comp in comps:
        state = "installed" if comp["installed"] else "missing"
        color = curses.color_pair(2) if comp["installed"] else curses.color_pair(4)
        safe_addstr(stdscr, row, 2, f"{comp['name']:<16} {state:<10} {comp['version']}", color)
        row += 1
        if row >= height - 3:
            break
    log(f"scan completed: {len([c for c in comps if c['installed']])} installed")
    pause(stdscr)


def screen_components(stdscr: curses.window) -> None:
    """Show installed versions alongside their apt package and candidate."""
    stdscr.clear()
    draw_logo(stdscr, 1)
    top = _logo_bottom()
    safe_addstr(stdscr, top, 2, "Installed Components", curses.color_pair(1) | curses.A_BOLD)
    row = top + 2
    comps = detect()
    height, _ = stdscr.getmaxyx()
    for comp in comps:
        candidate = ""
        if comp["installed"] and comp["package"]:
            candidate = apt_candidate(comp["package"])
        line = f"{comp['name']:<16} ver={comp['version']:<16} pkg={comp['package'] or '-'} candidate={candidate}"
        safe_addstr(stdscr, row, 2, line)
        row += 1
        if row >= height - 3:
            break
    pause(stdscr)


def screen_check(stdscr: curses.window) -> None:
    """Refresh the apt index and report component + system updates."""
    stdscr.clear()
    draw_logo(stdscr, 1)
    top = _logo_bottom()
    safe_addstr(stdscr, top, 2, "Checking for updates...", curses.color_pair(1) | curses.A_BOLD)
    stdscr.refresh()
    comps = detect()
    refresh_index()
    updates = check_updates(comps)
    row = top + 2
    height, _ = stdscr.getmaxyx()
    if not updates:
        safe_addstr(stdscr, row, 2, "All components are up to date.", curses.color_pair(2))
        row += 1
    else:
        for item in updates:
            safe_addstr(stdscr, row, 2, f"{item['name']}: {item['installed']} -> {item['candidate']}", curses.color_pair(3))
            row += 1
            if row >= height - 3:
                break
    upgradable = list_upgradable()
    safe_addstr(stdscr, row, 2, f"System upgradable packages: {len(upgradable)}", curses.color_pair(1) | curses.A_BOLD)
    row += 1
    for pkg in upgradable[:10]:
        safe_addstr(stdscr, row, 2, f"  {pkg}")
        row += 1
        if row >= height - 3:
            break
    pause(stdscr)


def screen_apply(stdscr: curses.window) -> None:
    """Interactively apply component updates, then optionally upgrade all."""
    stdscr.clear()
    draw_logo(stdscr, 1)
    top = _logo_bottom()
    cfg = config.load()
    dry_run = cfg.get("dry_run", False)
    row = top
    if dry_run:
        safe_addstr(stdscr, row, 2, "Dry-run mode: no changes will be applied", curses.color_pair(3))
        row += 2
    else:
        safe_addstr(stdscr, row, 2, "Apply updates? (y/n)", curses.color_pair(1) | curses.A_BOLD)
        stdscr.refresh()
        if stdscr.getch() not in (ord("y"), ord("Y")):
            return
        row += 2
    safe_addstr(stdscr, row, 2, "Refreshing package index...", curses.color_pair(3))
    stdscr.refresh()
    refresh_index()
    row += 1
    updates = check_updates(detect())
    height, _ = stdscr.getmaxyx()
    if not updates:
        safe_addstr(stdscr, row, 2, "No component updates.", curses.color_pair(2))
        row += 1
    for item in updates:
        safe_addstr(stdscr, row, 2, f"Updating {item['name']} ({item['package']})...", curses.color_pair(3))
        stdscr.refresh()
        if dry_run:
            safe_addstr(stdscr, row + 1, 2, "PLANNED", curses.color_pair(3))
            row += 2
        else:
            ok, _ = update_package(item["package"])
            row += 1
            safe_addstr(stdscr, row, 2, "OK" if ok else "FAILED", curses.color_pair(2) if ok else curses.color_pair(4))
            row += 1
        if row >= height - 3:
            break
    if not dry_run:
        stdscr.clear()
        draw_logo(stdscr, 1)
        line = _logo_bottom()
        safe_addstr(stdscr, line, 2, "Upgrade all system packages? (y/n)", curses.color_pair(1) | curses.A_BOLD)
        stdscr.refresh()
        if stdscr.getch() in (ord("y"), ord("Y")):
            safe_addstr(stdscr, line + 2, 2, "Upgrading system packages...", curses.color_pair(3))
            stdscr.refresh()
            ok, _ = upgrade_system()
            safe_addstr(stdscr, line + 3, 2, "OK" if ok else "FAILED", curses.color_pair(2) if ok else curses.color_pair(4))
            stdscr.refresh()
            time.sleep(1)
    pause(stdscr)


def screen_schedule(stdscr: curses.window) -> None:
    """Install or remove the recurring ``patchbeast --scan`` cron job."""
    options = ["Manual (remove cron)", "Daily", "Weekly", "Monthly", "Custom days", "Back"]
    idx = 0
    while True:
        stdscr.clear()
        draw_logo(stdscr, 1)
        top = _logo_bottom()
        safe_addstr(stdscr, top, 2, "Cron Schedule", curses.color_pair(1) | curses.A_BOLD)
        safe_addstr(stdscr, top + 1, 2, f"Current: {cron_status()}", curses.color_pair(3))
        row = top + 3
        for i, opt in enumerate(options):
            safe_addstr(stdscr, row + i, 4, f"  {opt}  ", curses.A_REVERSE if i == idx else 0)
        height, _ = stdscr.getmaxyx()
        safe_addstr(stdscr, height - 1, 2, "Up/Down navigate  Enter select  q back", curses.color_pair(3))
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(options)
        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(options)
        elif key in (10, 13, curses.KEY_ENTER):
            if idx == 5:
                break
            if idx == 0:
                ok, msg = remove_cron()
            elif idx == 1:
                ok, msg = install_cron("daily")
            elif idx == 2:
                ok, msg = install_cron("weekly")
            elif idx == 3:
                ok, msg = install_cron("monthly")
            else:
                days = _prompt_days(stdscr)
                ok, msg = install_cron("custom", days)
            safe_addstr(stdscr, height - 3, 2, msg, curses.color_pair(2) if ok else curses.color_pair(4))
            stdscr.refresh()
            time.sleep(1.5)
        elif key in (ord("q"), ord("Q")):
            break


def _prompt_days(stdscr: curses.window) -> int:
    """Ask for a custom day interval and return it (default 30)."""
    stdscr.clear()
    draw_logo(stdscr, 1)
    line = _logo_bottom()
    safe_addstr(stdscr, line, 2, "Enter days interval:", curses.color_pair(1) | curses.A_BOLD)
    stdscr.refresh()
    curses.echo()
    curses.curs_set(1)
    try:
        raw = stdscr.getstr(line + 2, 2, 10).decode("utf-8", errors="ignore").strip()
    except Exception:
        raw = "30"
    curses.noecho()
    curses.curs_set(0)
    try:
        return int(raw)
    except ValueError:
        return 30


def screen_logs(stdscr: curses.window) -> None:
    """Show the last 30 log lines."""
    stdscr.clear()
    draw_logo(stdscr, 1)
    top = _logo_bottom()
    safe_addstr(stdscr, top, 2, "Recent Logs", curses.color_pair(1) | curses.A_BOLD)
    row = top + 2
    lines: list[str] = []
    if os.path.exists(config.LOG_FILE):
        with open(config.LOG_FILE, encoding="utf-8", errors="ignore") as fh:
            lines = fh.readlines()[-30:]
    height, _ = stdscr.getmaxyx()
    for line in lines:
        safe_addstr(stdscr, row, 2, line.rstrip("\n"))
        row += 1
        if row >= height - 3:
            break
    if not lines:
        safe_addstr(stdscr, row, 2, "No logs yet.")
    pause(stdscr)


def screen_settings(stdscr: curses.window) -> None:
    """Toggle the ``auto_update`` and ``dry_run`` settings."""
    cfg = config.load()
    idx = 0
    options = ["Toggle auto-update", "Toggle dry-run", "Back"]
    while True:
        stdscr.clear()
        draw_logo(stdscr, 1)
        top = _logo_bottom()
        safe_addstr(stdscr, top, 2, "Settings", curses.color_pair(1) | curses.A_BOLD)
        safe_addstr(stdscr, top + 1, 2, f"Auto-update: {cfg.get('auto_update', False)}", curses.color_pair(3))
        safe_addstr(stdscr, top + 2, 2, f"Dry-run: {cfg.get('dry_run', False)}", curses.color_pair(3))
        row = top + 4
        for i, opt in enumerate(options):
            safe_addstr(stdscr, row + i, 4, f"  {opt}  ", curses.A_REVERSE if i == idx else 0)
        height, _ = stdscr.getmaxyx()
        safe_addstr(stdscr, height - 1, 2, "Up/Down navigate  Enter select  q back", curses.color_pair(3))
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(options)
        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(options)
        elif key in (10, 13, curses.KEY_ENTER):
            if idx == 0:
                cfg["auto_update"] = not cfg.get("auto_update", False)
                config.save(cfg)
            elif idx == 1:
                cfg["dry_run"] = not cfg.get("dry_run", False)
                config.save(cfg)
            else:
                break
        elif key in (ord("q"), ord("Q")):
            break


def screen_footer_user() -> str:
    """Return the privilege label shown under the main menu title."""
    return f"User: {'root' if is_root() else 'non-root (updates may require sudo)'}"
