import json
import os

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "patchbeast")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LOG_FILE = os.path.join(CONFIG_DIR, "patchbeast.log")
CACHE_DIR = os.path.join(CONFIG_DIR, "cache")

DEFAULT_CONFIG = {
    "schedule": "manual",
    "schedule_days": 30,
    "auto_update": False,
    "dry_run": False,
    "components": [],
}


def ensure_dirs():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)


def load():
    ensure_dirs()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = dict(DEFAULT_CONFIG)
            merged.update(data)
            return merged
        except Exception:
            return dict(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def save(cfg):
    ensure_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)