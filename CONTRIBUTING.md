# Contributing

## Setup

```bash
git clone https://github.com/jonuisw09/patchbeast.git
cd patchbeast
make install
```

Requires Python 3.9+ on a Debian/Ubuntu-based system.

## Workflow

1. Create a feature branch from `main`.
2. Keep changes small and focused; no commented-out code.
3. Add or update tests under `tests/` for logic changes
   (TUI drawing code is excluded from coverage requirements).
4. New detectable components go in `src/patchbeast/components.py` only.
5. Core modules (`scanner`, `updater`, `scheduler`, `config`, `utils`, `cli`)
   must stay UI-free — never import `curses` or `tui` from them.

## Checks

```bash
make test   # compileall + pytest
make lint   # ruff
```

Manual verification:

```bash
make run    # interactive TUI
make scan   # headless dry-run
```

## Pull requests

- Describe what changed and how it was verified.
- Update `CHANGELOG.md` under an `Unreleased` section.
- Update `docs/` if behavior or the menu changes.
