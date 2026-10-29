"""Main menu loop and TUI entry point."""

from __future__ import annotations

import curses

from ..logo import LOGO
from ..utils import is_root
from . import screens
from .widgets import draw_logo, safe_addstr

__all__ = ["MENU", "main_menu", "run_tui"]

MENU: list[str] = [
    "Scan System",
    "View Components",
    "Check Updates",
    "Apply Updates",
    "Schedule (Cron)",
    "View Logs",
    "Settings",
    "Exit",
]


def _menu_top() -> int:
    """Return the first free row below the ASCII logo."""
    return len(LOGO.strip("\n").split("\n")) + 3


def main_menu(stdscr: curses.window) -> None:
    """Render the main menu and dispatch to the selected screen."""
    curses.curs_set(0)
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    idx = 0
    handlers = [
        screens.screen_scan,
        screens.screen_components,
        screens.screen_check,
        screens.screen_apply,
        screens.screen_schedule,
        screens.screen_logs,
        screens.screen_settings,
    ]
    while True:
        stdscr.clear()
        height, _ = stdscr.getmaxyx()
        draw_logo(stdscr, 1)
        base = _menu_top()
        safe_addstr(stdscr, base, 2, "PatchBeast - Server Component Patch Manager", curses.color_pair(1) | curses.A_BOLD)
        user = "root" if is_root() else "non-root (updates may require sudo)"
        safe_addstr(stdscr, base + 1, 2, f"User: {user}", curses.color_pair(3))
        row = base + 3
        for i, item in enumerate(MENU):
            safe_addstr(stdscr, row + i, 4, f"  {item}  ", curses.A_REVERSE if i == idx else 0)
        safe_addstr(stdscr, height - 1, 2, "Up/Down navigate  Enter select  q quit", curses.color_pair(3))
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(MENU)
        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(MENU)
        elif key in (10, 13, curses.KEY_ENTER):
            if idx == len(MENU) - 1:
                break
            handlers[idx](stdscr)
        elif key in (ord("q"), ord("Q")):
            break


def run_tui() -> None:
    """Ensure config dirs exist and start the curses main menu."""
    from .. import config

    config.ensure_dirs()
    curses.wrapper(main_menu)
