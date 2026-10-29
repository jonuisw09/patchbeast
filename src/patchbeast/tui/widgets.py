"""Reusable curses drawing primitives for the PatchBeast TUI."""

from __future__ import annotations

import curses

from ..logo import LOGO

__all__ = ["safe_addstr", "draw_logo", "draw_box_title", "pause"]


def safe_addstr(win: curses.window, y: int, x: int, text: str, attr: int = 0) -> None:
    """Write *text* at ``(y, x)`` clipped to the window; never raises."""
    try:
        height, width = win.getmaxyx()
        if y < 0 or y >= height or x < 0 or x >= width:
            return
        if x + len(text) > width:
            text = text[: max(0, width - x - 1)]
        win.addstr(y, x, text, attr)
    except curses.error:
        pass


def draw_logo(win: curses.window, start_y: int = 0) -> None:
    """Draw the ASCII logo starting at row *start_y*."""
    for i, line in enumerate(LOGO.strip("\n").split("\n")):
        safe_addstr(win, start_y + i, 2, line, curses.color_pair(2) | curses.A_BOLD)


def draw_box_title(win: curses.window, title: str) -> None:
    """Draw a highlighted *title* at the top of *win*."""
    safe_addstr(win, 0, 2, title, curses.color_pair(1) | curses.A_BOLD)


def pause(win: curses.window, msg: str = "Press any key to continue") -> None:
    """Show *msg* at the bottom of *win* and wait for a keypress."""
    height, _ = win.getmaxyx()
    safe_addstr(win, height - 2, 2, msg, curses.color_pair(3))
    win.refresh()
    win.getch()
