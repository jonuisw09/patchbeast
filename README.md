# PatchBeast

PatchBeast is a terminal user interface (TUI) tool for Linux servers. It scans installed software components, compares installed versions against available updates, applies patched versions safely, restarts affected services, and can schedule recurring scans with cron.

No external dependencies. Standard library + `curses` only.

## Screenshots

### Main menu

![PatchBeast main menu](docs/screenshots/main-menu.png)

### Scan system

![PatchBeast scan](docs/screenshots/scan.png)

### Check updates

![PatchBeast check updates](docs/screenshots/check-updates.png)

### Cron schedule

![PatchBeast schedule](docs/screenshots/schedule.png)

## Features

- Detects 90+ server components: runtimes, web servers, databases, mail, security, monitoring, containers, IaC tools, control panels
- Compares installed versions against `apt` candidates
- Lists system-wide upgradable packages via simulated `apt-get upgrade`
- Applies updates with `apt-get install -y --only-upgrade`
- Restarts affected services after successful updates
- Dry-run mode to plan without changing anything
- JSON scan reports
- Cron scheduling: daily, weekly, monthly, custom interval
- Headless `--scan` mode for cron and automation
- English interface, `curses` based TUI
- Config and logs under `~/.config/patchbeast/`

## How it works

1. **Detect**
   Each component has a `command` + `args` pair. PatchBeast checks `shutil.which()`, runs the version command, and parses the version with a regex.

2. **Check**
   For components mapped to an `apt` package:
   - Installed version: `dpkg-query -W`
   - Candidate version: `apt-cache policy`
   - If they differ, an update is reported.
   - System packages: `apt-get -s upgrade` output lines starting with `Inst`.

3. **Apply**
   - `apt-get update` refreshes the index
   - `apt-get install -y --only-upgrade <package>` installs the patched version
   - `systemctl restart <service>` restarts the mapped service on success
   - Every step is logged

4. **Schedule**
   - Root: writes `/etc/cron.d/patchbeast`
   - Non-root: installs a user `crontab` entry
   - Command run by cron: `patchbeast --scan`

Service restart map:

| Package | Service |
|---|---|
| php | php-fpm |
| apache2 | apache2 |
| nginx | nginx |
| mariadb-server | mariadb |
| postgresql | postgresql |
| redis-server | redis-server |

## Supported components

Web servers and proxies:

Apache, Nginx, Lighttpd, Caddy, Traefik, HAProxy, Varnish

Databases and caches:

MySQL Client, MariaDB, PostgreSQL, MongoDB, SQLite, ClickHouse, TimescaleDB, InfluxDB, CouchDB, Cassandra, Neo4j, Redis, KeyDB, Dragonfly, Memcached

Runtimes and languages:

PHP, Python, Node.js, npm, Java, Go, Ruby, Perl, Rust, Deno, Bun, Elixir, Erlang, Composer

Mail:

Postfix, Dovecot, Exim, SpamAssassin, Amavis

Security:

OpenSSL, Fail2ban, UFW, ClamAV

Monitoring and observability:

Grafana, Prometheus, Zabbix Agent, Nagios, Netdata, Uptime Kuma

Message queues and search:

Elasticsearch, RabbitMQ, Kafka

Containers and orchestration:

Docker, Podman, containerd, k3s, kubectl, Helm, Portainer

CI and automation:

Jenkins, GitLab Runner, Gitea, Drone, Ansible, Terraform, Packer, Vagrant, Puppet, Chef, Salt, Supervisor

Control panels:

Plesk, cPanel, DirectAdmin, Webmin, aaPanel, CyberPanel, Virtualmin, HestiaCP, Froxlor, ISPConfig, CWP

Infrastructure:

etcd, Consul, Vault, MinIO, Keepalived, Git, curl

Components without an `apt` package mapping are detected and version-checked, but not auto-updated. Missing binaries are shown as `missing`.

## Requirements

- Linux with `apt` (Debian / Ubuntu and derivatives)
- Python 3.9+
- `sudo` or root for update and cron operations
- Terminal with `curses` support

## Installation

From source:

```bash
git clone https://github.com/jonuisw09/patchbeast.git
cd patchbeast
./install.sh
patchbeast
```

With pip:

```bash
python3 -m pip install .
patchbeast
```

Run without installing:

```bash
PYTHONPATH=src python3 -m patchbeast
```

## Usage

Interactive TUI:

```bash
patchbeast
```

Navigation:

- `Up` / `Down` or `k` / `j`: move
- `Enter`: select
- `q`: back / quit

Menu:

- `Scan System`: list installed / missing components
- `View Components`: versions, apt package, candidate
- `Check Updates`: component updates + system upgradable count
- `Apply Updates`: update components, optionally upgrade system
- `Schedule (Cron)`: daily / weekly / monthly / custom / remove
- `View Logs`: last 30 log lines
- `Settings`: toggle auto-update and dry-run
- `Exit`

Headless mode:

```bash
patchbeast --scan
patchbeast --scan --dry-run
patchbeast --scan --dry-run --report /tmp/report.json
patchbeast --scan --report ~/.config/patchbeast/last_report.json
```

## Configuration

Location:

```text
~/.config/patchbeast/config.json
~/.config/patchbeast/patchbeast.log
~/.config/patchbeast/last_report.json
~/.config/patchbeast/cache/
```

Example `config.json`:

```json
{
  "schedule": "manual",
  "schedule_days": 30,
  "auto_update": false,
  "dry_run": false,
  "components": []
}
```

Fields:

- `auto_update`: apply updates automatically in `--scan` mode
- `dry_run`: plan only, never change the system
- `schedule`, `schedule_days`: informational, cron itself holds the schedule

## Cron scheduling

From the TUI:

- `Daily`: `0 2 * * *`
- `Weekly`: `0 2 * * 0`
- `Monthly`: `0 2 1 * *`
- `Custom days N`: `0 2 */N * *`
- `Manual`: removes the job

Root installs `/etc/cron.d/patchbeast`, otherwise a user crontab entry with the `# patchbeast-managed` marker.

## Reports

`--report` writes JSON:

```json
{
  "components": [],
  "component_updates": [],
  "system_updates": [],
  "dry_run": true
}
```

Default path when omitted: `~/.config/patchbeast/last_report.json`.

## Project structure

```text
src/patchbeast/
  __init__.py
  __main__.py
  tui.py
  scanner.py
  updater.py
  scheduler.py
  config.py
  utils.py
  logo.py
docs/screenshots/
install.sh
pyproject.toml
```

## Limitations

- Update backend is `apt` only
- Components installed via `pip`, `npm -g`, `composer global`, binary installers, Docker images, or panel-specific updaters are detected but not auto-updated
- `apt-get update`, upgrades, service restarts, and system cron require root or passwordless `sudo`
- Package names follow Debian / Ubuntu conventions and may differ on other distros

## Contributing

1. Fork the repository
2. Create a feature branch
3. Keep changes small and without commented-out code
4. Verify with `python3 -m compileall -q src`
5. Test TUI with `patchbeast` and headless with `patchbeast --scan --dry-run`
6. Open a pull request

## Security

Do not run untrusted cron commands as root. Review `~/.config/patchbeast/patchbeast.log` after automated runs. Use dry-run first on production systems.

## License

MIT. See `LICENSE`.
