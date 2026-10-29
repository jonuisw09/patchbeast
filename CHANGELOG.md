# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

- `tests/` suite (scanner, updater, scheduler, config, version parsing) with
  `pytest` configuration in `pyproject.toml`.
- `docs/ARCHITECTURE.md` and `docs/USAGE.md`.
- CI workflow (`.github/workflows/ci.yml`): compile check + pytest + ruff.
- `Makefile` with `install`, `test`, `lint`, `run`, `scan` targets.
- `CHANGELOG.md` and `CONTRIBUTING.md`.
- Ruff lint configuration.

### Changed

- Split the component registry out of the scanner into `components.py`
  (typed `Component` records).
- Split the 360-line `tui.py` monolith into the `tui/` package:
  `app.py` (menu loop), `screens.py` (one function per screen),
  `widgets.py` (curses primitives).
- Extracted CLI/headless logic from `__main__.py` into `cli.py`
  (`build_parser()`, `headless_scan()`, `main()`); `__main__.py` is now a
  thin entry point.
- Full type hints and docstrings across all modules; `__init__.py` now
  exposes `__version__` and the public API.

### Fixed

- Non-root cron installs no longer inject a stray `PATH=` line.
- `scheduler.install("manual")` correctly delegates to `remove()`.

## [1.0.0] - 2026-10-29

Initial release: curses TUI, ~90 component detection, apt update backend,
cron scheduling, headless `--scan` mode, JSON reports.
