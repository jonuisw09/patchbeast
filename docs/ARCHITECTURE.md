# Architecture

PatchBeast follows a layered design. The interactive TUI and the headless
`--scan` mode share the same core: `scanner` finds what's installed,
`updater` compares against `apt` and applies patches, `scheduler` owns the
cron job.

```text
                ┌─────────────┐
                │  patchbeast │
                │   __init__  │  __version__, public re-exports
                └──────┬──────┘
                       │
            ┌──────────┴──────────┐
            │         cli         │  argparse + headless_scan()
            │  (--scan / TUI run) │
            └──────┬──────┬───────┘
                   │      │
        ┌──────────┘      └──────────┐
        ▼                            ▼
┌───────────────┐            ┌────────────────┐
│      tui      │            │  core modules  │
│ app (menu)    │            │  scanner       │
│ screens (*)   │───────────▶│  updater       │
│ widgets (ui)  │  uses      │  scheduler     │
└───────────────┘            │  config/utils  │
                             └────────────────┘
```

## Modules

| Module | Responsibility | Must stay UI-free |
|---|---|---|
| `components.py` | Static registry (~90 components: binary, args, apt package) | yes |
| `scanner.py` | `detect()`, `apt_candidate()`, `apt_installed_version()` | yes |
| `updater.py` | `check_updates()`, `update_package()`, `list_upgradable()`, `upgrade_system()`, `SERVICE_MAP` | yes |
| `scheduler.py` | `install()`, `remove()`, `status()`, `cron_expression()` | yes |
| `config.py` | JSON config under `~/.config/patchbeast/` | yes |
| `utils.py` | `run()`, `parse_version()`, `is_root()`, `sudo_prefix()`, `log()` | yes |
| `cli.py` | Argument parsing, `headless_scan()` report + auto-update flow | yes |
| `tui/app.py` | `main_menu()` loop, `run_tui()` | no (curses) |
| `tui/screens.py` | One function per menu entry (`screen_scan`, `screen_check`, …) | no (curses) |
| `tui/widgets.py` | `safe_addstr()`, `draw_logo()`, `pause()` | no (curses) |

## Key flows

**Headless scan** (`patchbeast --scan` → `cli.headless_scan`):

1. `config.ensure_dirs()` + `config.load()`
2. `scanner.detect()` → installed components + versions
3. `updater.check_updates()` (installed vs. `apt-cache policy` candidate) and
   `updater.list_upgradable()` (`apt-get -s upgrade`)
4. Write JSON report (`~/.config/patchbeast/last_report.json` by default)
5. If `auto_update` and not dry-run: `update_all()` + `upgrade_system()`;
   otherwise log what *would* change

**Apply from TUI** (`tui/screens.screen_apply`):

1. Confirm with the user (skipped in dry-run)
2. `updater.refresh_index()` (`apt-get update`)
3. Per-component `updater.update_package()` (`apt-get install -y --only-upgrade`),
   restarting the `SERVICE_MAP` service on success
4. Optional full `updater.upgrade_system()`

## Conventions

- Core modules never import `curses` or anything under `tui/`.
- All subprocess calls go through `utils.run()`, which normalizes
  timeouts/errors to `(-1, "", msg)` instead of raising.
- `tui/` only calls the public functions above; screens contain no
  `apt`/`dpkg` command strings.
- New components are added in `components.py` only — no logic changes needed.
