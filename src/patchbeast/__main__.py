import argparse
import os
import sys

from . import config
from .scanner import detect
from .updater import refresh_index, check_updates, update_all, list_upgradable, upgrade_system
from .utils import log


def headless_scan(dry_run=False, report_path=None):
    config.ensure_dirs()
    cfg = config.load()
    if dry_run:
        cfg["dry_run"] = True
    comps = detect()
    refresh_index()
    updates = check_updates(comps)
    upg = list_upgradable()
    log(f"scan found {len(updates)} component updates and {len(upg)} system updates")
    report = {
        "components": comps,
        "component_updates": updates,
        "system_updates": upg,
        "dry_run": dry_run or cfg.get("dry_run", False),
    }
    if report_path is None:
        report_path = os.path.join(config.CONFIG_DIR, "last_report.json")
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            import json
            json.dump(report, f, indent=2)
    except Exception:
        pass
    auto = cfg.get("auto_update", False) and not (dry_run or cfg.get("dry_run", False))
    if auto:
        update_all(comps)
        upgrade_system()
        log("auto update completed")
    else:
        for u in updates:
            log(f"update available {u['name']} {u['installed']} -> {u['candidate']}")
        for p in upg:
            log(f"system update available {p}")
        if dry_run or cfg.get("dry_run", False):
            log("dry run: no changes applied")


def main():
    parser = argparse.ArgumentParser(prog="patchbeast")
    parser.add_argument("--scan", action="store_true", help="Run a headless scan")
    parser.add_argument("--dry-run", action="store_true", help="Plan updates without applying")
    parser.add_argument("--report", help="Write JSON report to path")
    args = parser.parse_args()
    if args.scan:
        headless_scan(dry_run=args.dry_run, report_path=args.report)
        return
    from .tui import run_tui
    run_tui()


if __name__ == "__main__":
    main()