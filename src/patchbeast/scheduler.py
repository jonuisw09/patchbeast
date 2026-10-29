import os
import shutil
import subprocess
from .utils import run, is_root, log

MARKER = "# patchbeast-managed"


def cron_expression(schedule, days):
    if schedule == "daily":
        return "0 2 * * *"
    if schedule == "weekly":
        return "0 2 * * 0"
    if schedule == "monthly":
        return "0 2 1 * *"
    if schedule == "custom":
        n = max(1, int(days))
        return f"0 2 */{n} * *"
    return None


def _cron_command():
    exe = shutil.which("patchbeast")
    if exe:
        return f"{exe} --scan"
    return "/usr/bin/python3 -m patchbeast --scan"


def install(schedule, days=30):
    expr = cron_expression(schedule, days)
    if not expr:
        remove()
        return True, "Cron removed"
    line = f"{expr} {MARKER} {_cron_command()}"
    if is_root():
        path = "/etc/cron.d/patchbeast"
        content = "PATH=/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n" + line + "\n"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            os.chmod(path, 0o644)
            log(f"cron installed {expr}")
            return True, f"Cron installed: {expr}"
        except Exception as e:
            log(f"cron install failed {e}")
            return False, str(e)
    else:
        code, out, err = run("crontab -l 2>/dev/null", timeout=30)
        existing = out if code == 0 else ""
        lines = [l for l in existing.splitlines() if MARKER not in l]
        if not any(l.strip().startswith("PATH=") for l in lines):
            lines.insert(0, "PATH=/root/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")
        lines.append(line)
        new = "\n".join(lines) + "\n"
        p = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        p.communicate(new)
        if p.returncode != 0:
            return False, "crontab update failed"
        log(f"cron installed {expr}")
        return True, f"Cron installed: {expr}"


def remove():
    if is_root():
        path = "/etc/cron.d/patchbeast"
        try:
            if os.path.exists(path):
                os.remove(path)
            log("cron removed")
            return True, "Cron removed"
        except Exception as e:
            return False, str(e)
    else:
        code, out, err = run("crontab -l 2>/dev/null", timeout=30)
        existing = out if code == 0 else ""
        lines = [l for l in existing.splitlines() if MARKER not in l]
        new = "\n".join(lines) + ("\n" if lines else "")
        p = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
        p.communicate(new)
        log("cron removed")
        return True, "Cron removed"


def status():
    if is_root():
        path = "/etc/cron.d/patchbeast"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return "No cron job installed"
    code, out, err = run("crontab -l 2>/dev/null", timeout=30)
    for line in (out or "").splitlines():
        if MARKER in line:
            return line.strip()
    return "No cron job installed"