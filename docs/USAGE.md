# Usage

## Interactive TUI

```bash
patchbeast
```

| Keys | Action |
|---|---|
| `Up` / `Down` or `k` / `j` | Move selection |
| `Enter` | Open the selected screen |
| `q` | Back / quit |

Menu screens:

- **Scan System** — list installed / missing components with versions.
- **View Components** — versions plus mapped `apt` package and candidate.
- **Check Updates** — component updates + count of system-wide upgradable packages.
- **Apply Updates** — upgrade components (restarts mapped services), then
  optionally run a full `apt-get upgrade -y`.
- **Schedule (Cron)** — daily / weekly / monthly / custom interval / remove.
- **View Logs** — last 30 lines of `~/.config/patchbeast/patchbeast.log`.
- **Settings** — toggle `auto_update` and `dry_run`.

## Headless mode (cron & automation)

```bash
patchbeast --scan
patchbeast --scan --dry-run
patchbeast --scan --dry-run --report /tmp/report.json
patchbeast --scan --report ~/.config/patchbeast/last_report.json
```

Behavior:

- Always writes a JSON report with `components`, `component_updates`,
  `system_updates` and `dry_run` fields.
- Applies updates only when `auto_update: true` is set in the config
  **and** dry-run is off.
- Cron installs `patchbeast --scan`; combine with `auto_update` for
  fully automatic patching, or leave it off to only collect reports.

## Configuration

Location: `~/.config/patchbeast/config.json`

```json
{
  "schedule": "manual",
  "schedule_days": 30,
  "auto_update": false,
  "dry_run": false
}
```

Detection results are cached for 5 minutes under
`~/.config/patchbeast/cache/detection.json`, so TUI screens stay fast.
`Scan System` and headless `--scan` always refresh the cache live.

| Key | Meaning |
|---|---|
| `auto_update` | Apply updates automatically in `--scan` mode |
| `dry_run` | Plan only, never change the system |
| `schedule` / `schedule_days` | Informational; the real schedule lives in cron |

## Cron schedules

| Choice | Expression | Installed as |
|---|---|---|
| Daily | `0 2 * * *` | root → `/etc/cron.d/patchbeast`; user → `crontab` entry tagged `# patchbeast-managed` |
| Weekly | `0 2 * * 0` | same as above |
| Monthly | `0 2 1 * *` | same as above |
| Custom N days | `0 2 */N * *` | same as above |
| Manual | — | removes the job |

## Service restarts

After a successful component upgrade, the mapped service is restarted:

| Package | Service |
|---|---|
| `php` | `php-fpm` |
| `apache2` | `apache2` |
| `nginx` | `nginx` |
| `mariadb-server` | `mariadb` |
| `postgresql` | `postgresql` |
| `redis-server` | `redis-server` |

## Safety tips

- Run `--dry-run` first on production systems.
- Review `~/.config/patchbeast/patchbeast.log` after automated runs.
- Updates and service restarts need root or passwordless `sudo`.
