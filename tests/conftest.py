"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from patchbeast.scanner import DetectedComponent


@pytest.fixture
def sample_components() -> list[DetectedComponent]:
    """Two apt-backed components with known versions."""
    return [
        DetectedComponent(
            name="Nginx",
            command="nginx",
            installed=True,
            version="1.18.0",
            path="/usr/sbin/nginx",
            package="nginx",
        ),
        DetectedComponent(
            name="Caddy",
            command="caddy",
            installed=True,
            version="2.7.0",
            path="/usr/bin/caddy",
            package=None,
        ),
    ]
