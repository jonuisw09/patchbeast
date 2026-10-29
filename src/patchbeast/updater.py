import os
import shutil
from . import config
from .utils import run, sudo_prefix, log
from .scanner import apt_candidate, apt_installed_version


SERVICE_MAP = {
    "php": "php-fpm",
    "apache2": "apache2",
    "nginx": "nginx",
    "mariadb-server": "mariadb",
    "postgresql": "postgresql",
    "redis-server": "redis-server",
}


def restart_service(service):
    if not service:
        return True, "no service"
    if not shutil.which("systemctl"):
        return False, "systemctl not available"
    code, out, err = run(f"{sudo_prefix()}systemctl restart {service}", timeout=120)
    text = (out + "\n" + err).strip()
    log(f"restart {service} rc={code}")
    return code == 0, text


def refresh_index():
    code, out, err = run(f"{sudo_prefix()}apt-get update", timeout=300)
    log(f"apt-get update rc={code}")
    return code == 0, (out + err).strip()


def check_updates(components):
    updates = []
    for comp in components:
        pkg = comp.get("package")
        if not pkg or not comp.get("installed"):
            continue
        candidate = apt_candidate(pkg)
        installed = apt_installed_version(pkg) or comp.get("version", "")
        if candidate and candidate != installed:
            updates.append({
                "name": comp["name"],
                "package": pkg,
                "installed": installed,
                "candidate": candidate,
            })
    return updates


def update_package(package):
    config.ensure_dirs()
    code, out, err = run(
        f"{sudo_prefix()}apt-get install -y --only-upgrade {package}",
        timeout=600,
    )
    text = (out + "\n" + err).strip()
    if code == 0:
        service = SERVICE_MAP.get(package)
        if service:
            rok, rtext = restart_service(service)
            text = text + "\n" + rtext
    log(f"update {package} rc={code}")
    return code == 0, text


def list_upgradable():
    code, out, err = run("LC_ALL=C apt-get -s upgrade", timeout=300)
    pkgs = []
    for line in (out or "").splitlines():
        if line.startswith("Inst "):
            parts = line.split()
            if len(parts) > 1:
                pkgs.append(parts[1])
    return pkgs


def upgrade_system():
    code, out, err = run(f"{sudo_prefix()}apt-get upgrade -y", timeout=1800)
    text = (out + "\n" + err).strip()
    log(f"system upgrade rc={code}")
    return code == 0, text


def update_all(components):
    results = []
    for comp in components:
        pkg = comp.get("package")
        if not pkg or not comp.get("installed"):
            continue
        candidate = apt_candidate(pkg)
        installed = apt_installed_version(pkg) or comp.get("version", "")
        if candidate and candidate != installed:
            ok, text = update_package(pkg)
            results.append({"package": pkg, "success": ok, "output": text})
    return results