import subprocess
import os
import re


def run(cmd, timeout=120, capture=True):
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
    except Exception as e:
        return -1, "", str(e)


def is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def sudo_prefix():
    return "" if is_root() else "sudo "


def parse_version(text):
    m = re.search(r"(\d+\.\d+(?:\.\d+)?(?:[-+~][A-Za-z0-9.]+)?)", text)
    return m.group(1) if m else ""


def version_tuple(v):
    parts = re.findall(r"\d+", v)
    return tuple(int(x) for x in parts) if parts else (0,)


def log(msg, path=None):
    import datetime
    if path is None:
        from .config import LOG_FILE
        path = LOG_FILE
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat()} {msg}\n")
    except Exception:
        pass