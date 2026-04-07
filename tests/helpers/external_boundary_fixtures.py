"""Helpers for external-boundary fixture families."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from custom_components.lipro.const.base import VERSION
from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_FIXTURE_ROOT = _ROOT / "tests" / "fixtures" / "external_boundaries"
_PLACEHOLDERS = {
    "__INTEGRATION_VERSION__": VERSION,
}


def _replace_placeholders(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _replace_placeholders(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_replace_placeholders(item) for item in value]
    if isinstance(value, str):
        return _PLACEHOLDERS.get(value, value)
    return value


def load_external_boundary_fixture(*parts: str) -> Any:
    """Load one JSON fixture from `tests/fixtures/external_boundaries`."""
    path = _FIXTURE_ROOT.joinpath(*parts)
    return _replace_placeholders(json.loads(path.read_text(encoding="utf-8")))
