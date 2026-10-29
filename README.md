# PatchBeast

PatchBeast is a terminal user interface (TUI) tool that scans installed software components on a server, checks whether they are up to date, downloads patched versions, and applies them safely. It can also install a cron job to run scans on a schedule.

## Features

- Detects installed components such as PHP, Python, Node.js, Apache, Nginx, and databases
- Compares installed versions against available updates
- Downloads and installs patched versions through the system package manager
- Restarts affected services after successful updates
- Dry-run mode to plan updates without applying them
- Exports scan reports in JSON format
- Schedules recurring scans with cron
- English language interface

## Installation

```bash
python3 -m pip install .
```

Or run directly:

```bash
python3 -m patchbeast
```

## Usage

```bash
patchbeast
```

Inside the TUI use the arrow keys and Enter to navigate.

## License

MIT