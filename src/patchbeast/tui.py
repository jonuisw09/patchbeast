import curses
import os
import time

from .logo import LOGO
from . import config
from .scanner import detect, apt_candidate, apt_installed_version
from .updater import refresh_index, check_updates, update_package, list_upgradable, upgrade_system
from .scheduler import install, remove, status, cron_expression
from .utils import log, is_root


MENU = [
    "Scan System",
    "View Components",
    "Check Updates",
    "Apply Updates",
    "Schedule (Cron)",
    "View Logs",
    "Settings",
    "Exit",
]


def safe_addstr(win, y, x, text, attr=0):
    try:
        h, w = win.getmaxyx()
        if y < 0 or y >= h or x < 0 or x >= w:
            return
        if x + len(text) > w:
            text = text[: max(0, w - x - 1)]
        win.addstr(y, x, text, attr)
    except curses.error:
        pass


def draw_logo(win, start_y=0):
    lines = LOGO.strip("\n").split("\n")
    for i, line in enumerate(lines):
        safe_addstr(win, start_y + i, 2, line, curses.color_pair(2) | curses.A_BOLD)


def draw_box_title(win, title):
    h, w = win.getmaxyx()
    safe_addstr(win, 0, 2, title, curses.color_pair(1) | curses.A_BOLD)


def pause(win, msg="Press any key to continue"):
    h, w = win.getmaxyx()
    safe_addstr(win, h - 2, 2, msg, curses.color_pair(3))
    win.refresh()
    win.getch()


def main_menu(stdscr):
    curses.curs_set(0)
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    idx = 0
    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        draw_logo(stdscr, 1)
        logo_lines = len(LOGO.strip("\n").split("\n"))
        y = logo_lines + 3
        safe_addstr(stdscr, y, 2, "PatchBeast - Server Component Patch Manager", curses.color_pair(1) | curses.A_BOLD)
        y += 1
        safe_addstr(stdscr, y, 2, f"User: {'root' if is_root() else 'non-root (updates may require sudo)'}", curses.color_pair(3))
        y += 2
        for i, item in enumerate(MENU):
            attr = curses.A_REVERSE if i == idx else 0
            safe_addstr(stdscr, y + i, 4, f"  {item}  ", attr)
        safe_addstr(stdscr, h - 1, 2, "Up/Down navigate  Enter select  q quit", curses.color_pair(3))
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(MENU)
        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(MENU)
        elif key in (10, 13, curses.KEY_ENTER):
            if idx == 0:
                screen_scan(stdscr)
            elif idx == 1:
                screen_components(stdscr)
            elif idx == 2:
                screen_check(stdscr)
            elif idx == 3:
                screen_apply(stdscr)
            elif idx == 4:
                screen_schedule(stdscr)
            elif idx == 5:
                screen_logs(stdscr)
            elif idx == 6:
                screen_settings(stdscr)
            elif idx == 7:
                break
        elif key in (ord("q"), ord("Q")):
            break


def screen_scan(stdscr):
    stdscr.clear()
    draw_logo(stdscr, 1)
    logo_lines = len(LOGO.strip("\n").split("\n"))
    y = logo_lines + 3
    safe_addstr(stdscr, y, 2, "Scanning installed components...", curses.color_pair(1) | curses.A_BOLD)
    stdscr.refresh()
    comps = detect()
    h, w = stdscr.getmaxyx()
    y += 2
    for c in comps:
        status = "installed" if c["installed"] else "missing"
        color = curses.color_pair(2) if c["installed"] else curses.color_pair(4)
        safe_addstr(stdscr, y, 2, f"{c['name']:<16} {status:<10} {c['version']}", color)
        y += 1
        if y >= h - 3:
            break
    log(f"scan completed: {len([c for c in comps if c['installed']])} installed")
    pause(stdscr)


def screen_components(stdscr):
    stdscr.clear()
    draw_logo(stdscr, 1)
    logo_lines = len(LOGO.strip("\n").split("\n"))
    y = logo_lines + 3
    safe_addstr(stdscr, y, 2, "Installed Components", curses.color_pair(1) | curses.A_BOLD)
    y += 2
    comps = detect()
    h, w = stdscr.getmaxyx()
    for c in comps:
        cand = ""
        if c["installed"] and c["package"]:
            cand = apt_candidate(c["package"])
        line = f"{c['name']:<16} ver={c['version']:<16} pkg={c['package'] or '-'} candidate={cand}"
        safe_addstr(stdscr, y, 2, line)
        y += 1
        if y >= h - 3:
            break
    pause(stdscr)


def screen_check(stdscr):
    stdscr.clear()
    draw_logo(stdscr, 1)
    logo_lines = len(LOGO.strip("\n").split("\n"))
    y = logo_lines + 3
    safe_addstr(stdscr, y, 2, "Checking for updates...", curses.color_pair(1) | curses.A_BOLD)
    stdscr.refresh()
    comps = detect()
    refresh_index()
    updates = check_updates(comps)
    y += 2
    h, w = stdscr.getmaxyx()
    if not updates:
        safe_addstr(stdscr, y, 2, "All components are up to date.", curses.color_pair(2))
        y += 1
    else:
        for u in updates:
            safe_addstr(stdscr, y, 2, f"{u['name']}: {u['installed']} -> {u['candidate']}", curses.color_pair(3))
            y += 1
            if y >= h - 3:
                break
    upg = list_upgradable()
    safe_addstr(stdscr, y, 2, f"System upgradable packages: {len(upg)}", curses.color_pair(1) | curses.A_BOLD)
    y += 1
    for p in upg[:10]:
        safe_addstr(stdscr, y, 2, f"  {p}")
        y += 1
        if y >= h - 3:
            break
    pause(stdscr)


def screen_apply(stdscr):
    stdscr.clear()
    draw_logo(stdscr, 1)
    logo_lines = len(LOGO.strip("\n").split("\n"))
    y = logo_lines + 3
    cfg = config.load()
    dry_run = cfg.get("dry_run", False)
    if dry_run:
        safe_addstr(stdscr, y, 2, "Dry-run mode: no changes will be applied", curses.color_pair(3))
        y += 2
    else:
        safe_addstr(stdscr, y, 2, "Apply updates? (y/n)", curses.color_pair(1) | curses.A_BOLD)
        stdscr.refresh()
        key = stdscr.getch()
        if key not in (ord("y"), ord("Y")):
            return
        y += 2
    safe_addstr(stdscr, y, 2, "Refreshing package index...", curses.color_pair(3))
    stdscr.refresh()
    refresh_index()
    y += 1
    comps = detect()
    updates = check_updates(comps)
    h, w = stdscr.getmaxyx()
    if not updates:
        safe_addstr(stdscr, y, 2, "No component updates.", curses.color_pair(2))
        y += 1
    for u in updates:
        safe_addstr(stdscr, y, 2, f"Updating {u['name']} ({u['package']})...", curses.color_pair(3))
        stdscr.refresh()
        if dry_run:
            safe_addstr(stdscr, y + 1, 2, "PLANNED", curses.color_pair(3))
            y += 2
        else:
            ok, text = update_package(u["package"])
            y += 1
            color = curses.color_pair(2) if ok else curses.color_pair(4)
            safe_addstr(stdscr, y, 2, "OK" if ok else "FAILED", color)
            y += 1
        if y >= h - 3:
            break
    if not dry_run:
        stdscr.clear()
        draw_logo(stdscr, 1)
        ly = logo_lines + 3
        safe_addstr(stdscr, ly, 2, "Upgrade all system packages? (y/n)", curses.color_pair(1) | curses.A_BOLD)
        stdscr.refresh()
        key = stdscr.getch()
        if key in (ord("y"), ord("Y")):
            safe_addstr(stdscr, ly + 2, 2, "Upgrading system packages...", curses.color_pair(3))
            stdscr.refresh()
            ok, text = upgrade_system()
            color = curses.color_pair(2) if ok else curses.color_pair(4)
            safe_addstr(stdscr, ly + 3, 2, "OK" if ok else "FAILED", color)
            stdscr.refresh()
            time.sleep(1)
    pause(stdscr)


def screen_schedule(stdscr):
    options = ["Manual (remove cron)", "Daily", "Weekly", "Monthly", "Custom days", "Back"]
    idx = 0
    while True:
        stdscr.clear()
        draw_logo(stdscr, 1)
        logo_lines = len(LOGO.strip("\n").split("\n"))
        y = logo_lines + 3
        safe_addstr(stdscr, y, 2, "Cron Schedule", curses.color_pair(1) | curses.A_BOLD)
        y += 1
        safe_addstr(stdscr, y, 2, f"Current: {status()}", curses.color_pair(3))
        y += 2
        for i, opt in enumerate(options):
            attr = curses.A_REVERSE if i == idx else 0
            safe_addstr(stdscr, y + i, 4, f"  {opt}  ", attr)
        h, w = stdscr.getmaxyx()
        safe_addstr(stdscr, h - 1, 2, "Up/Down navigate  Enter select  q back", curses.color_pair(3))
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(options)
        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(options)
        elif key in (10, 13, curses.KEY_ENTER):
            if idx == 0:
                ok, msg = remove()
            elif idx == 1:
                ok, msg = install("daily")
            elif idx == 2:
                ok, msg = install("weekly")
            elif idx == 3:
                ok, msg = install("monthly")
            elif idx == 4:
                stdscr.clear()
                draw_logo(stdscr, 1)
                ly = logo_lines + 3
                safe_addstr(stdscr, ly, 2, "Enter days interval:", curses.color_pair(1) | curses.A_BOLD)
                stdscr.refresh()
                curses.echo()
                curses.curs_set(1)
                try:
                    s = stdscr.getstr(ly + 2, 2, 10).decode("utf-8", errors="ignore").strip()
                except Exception:
                    s = "30"
                curses.noecho()
                curses.curs_set(0)
                try:
                    days = int(s)
                except ValueError:
                    days = 30
                ok, msg = install("custom", days)
            elif idx == 5:
                break
            if idx != 5:
                safe_addstr(stdscr, h - 3, 2, msg, curses.color_pair(2 if ok else 4))
                stdscr.refresh()
                time.sleep(1.5)
        elif key in (ord("q"), ord("Q")):
            break


def screen_logs(stdscr):
    stdscr.clear()
    draw_logo(stdscr, 1)
    logo_lines = len(LOGO.strip("\n").split("\n"))
    y = logo_lines + 3
    safe_addstr(stdscr, y, 2, "Recent Logs", curses.color_pair(1) | curses.A_BOLD)
    y += 2
    path = config.LOG_FILE
    lines = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()[-30:]
    h, w = stdscr.getmaxyx()
    for line in lines:
        safe_addstr(stdscr, y, 2, line.rstrip("\n"))
        y += 1
        if y >= h - 3:
            break
    if not lines:
        safe_addstr(stdscr, y, 2, "No logs yet.")
    pause(stdscr)


def screen_settings(stdscr):
    cfg = config.load()
    idx = 0
    options = ["Toggle auto-update", "Toggle dry-run", "Back"]
    while True:
        stdscr.clear()
        draw_logo(stdscr, 1)
        logo_lines = len(LOGO.strip("\n").split("\n"))
        y = logo_lines + 3
        safe_addstr(stdscr, y, 2, "Settings", curses.color_pair(1) | curses.A_BOLD)
        y += 1
        safe_addstr(stdscr, y, 2, f"Auto-update: {cfg.get('auto_update', False)}", curses.color_pair(3))
        y += 1
        safe_addstr(stdscr, y, 2, f"Dry-run: {cfg.get('dry_run', False)}", curses.color_pair(3))
        y += 2
        for i, opt in enumerate(options):
            attr = curses.A_REVERSE if i == idx else 0
            safe_addstr(stdscr, y + i, 4, f"  {opt}  ", attr)
        h, w = stdscr.getmaxyx()
        safe_addstr(stdscr, h - 1, 2, "Up/Down navigate  Enter select  q back", curses.color_pair(3))
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
            elif idx == 2:
                break
        elif key in (ord("q"), ord("Q")):
            break


def run_tui():
    config.ensure_dirs()
    curses.wrapper(main_menu)