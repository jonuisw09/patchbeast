"""Headless scan mode and ``argparse`` entry point (``patchbeast --scan``)."""

from __future__ import annotations

import argparse
import json
import os

from . import config
from .scanner import detect
from .updater import check_updates, list_upgradable, update_all, upgrade_system
from .utils import log

__all__ = ["headless_scan", "main", "build_parser"]


def headless_scan(dry_run: bool = False, report_path: str | None = None) -> None:
    """Run a non-interactive scan, optionally auto-applying updates.

    Always writes a JSON report (default ``~/.config/patchbeast/last_report.json``).
    Updates are applied only when ``auto_update`` is set and dry-run is off.
    """
    config.ensure_dirs()
    cfg = config.load()
    if dry_run:
        cfg["dry_run"] = True
    comps = detect()
    updates = check_updates(comps)
    upgradable = list_upgradable()
    log(f"scan found {len(updates)} component updates and {len(upgradable)} system updates")
    report = {
        "components": comps,
        "component_updates": updates,
        "system_updates": upgradable,
        "dry_run": dry_run or cfg.get("dry_run", False),
    }
    target = report_path or os.path.join(config.CONFIG_DIR, "last_report.json")
    try:
        with open(target, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
    except OSError:
        pass
    auto = cfg.get("auto_update", False) and not (dry_run or cfg.get("dry_run", False))
    if auto:
        update_all(comps)
        upgrade_system()
        log("auto update completed")
        return
    for item in updates:
        log(f"update available {item['name']} {item['installed']} -> {item['candidate']}")
    for pkg in upgradable:
        log(f"system update available {pkg}")
    if dry_run or cfg.get("dry_run", False):
        log("dry run: no changes applied")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="patchbeast",
        description="Scan and patch server components (interactive TUI or headless --scan).",
    )
    parser.add_argument("--scan", action="store_true", help="Run a headless scan")
    parser.add_argument("--dry-run", action="store_true", help="Plan updates without applying")
    parser.add_argument("--report", help="Write JSON report to path")
    return parser


def main(argv: list[str] | None = None) -> None:
    """CLI entry point: ``--scan`` runs headless, otherwise starts the TUI."""
    args = build_parser().parse_args(argv)
    if args.scan:
        headless_scan(dry_run=args.dry_run, report_path=args.report)
        return
    from .tui import run_tui

    run_tui()
