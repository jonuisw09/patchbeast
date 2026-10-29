.PHONY: install test lint run scan dry-run clean

install:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m compileall -q src
	python3 -m pytest -q

lint:
	python3 -m ruff check src tests || true

run:
	PYTHONPATH=src python3 -m patchbeast

scan:
	PYTHONPATH=src python3 -m patchbeast --scan --dry-run

dry-run: scan

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
	rm -rf build dist *.egg-info src/*.egg-info
