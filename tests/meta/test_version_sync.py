"""Version metadata consistency checks."""

from __future__ import annotations

import json
from pathlib import Path
import re
import tomllib
from typing import Any

import yaml

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_PYPROJECT = _ROOT / "pyproject.toml"
_MANIFEST = _ROOT / "custom_components" / "lipro" / "manifest.json"
_HACS = _ROOT / "hacs.json"
_BASE_CONST = _ROOT / "custom_components" / "lipro" / "const" / "base.py"
_BUG_TEMPLATE = _ROOT / ".github" / "ISSUE_TEMPLATE" / "bug.yml"

_BASE_VERSION_RE = re.compile(r'^VERSION:\s+Final\s*=\s*"(?P<version>[^"]+)"\s*$')


def _read_base_version() -> str:
    for line in _BASE_CONST.read_text(encoding="utf-8").splitlines():
        if match := _BASE_VERSION_RE.match(line.strip()):
            return match.group("version")
    raise AssertionError("Could not find VERSION constant in const/base.py")


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _read_homeassistant_version() -> str:
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    dev_deps: list[str] = pyproject["project"]["optional-dependencies"]["dev"]
    ha_pin = next(dep for dep in dev_deps if dep.startswith("homeassistant=="))
    return ha_pin.split("==", 1)[1]


def test_integration_version_is_consistent() -> None:
    """pyproject.toml, manifest.json and const/base.py should agree on version."""
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))

    assert (
        manifest["version"] == pyproject["project"]["version"] == _read_base_version()
    )


def test_homeassistant_min_version_is_consistent() -> None:
    """Keep Home Assistant version pin consistent across repo metadata."""
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    hacs = json.loads(_HACS.read_text(encoding="utf-8"))
    ha_version = _read_homeassistant_version()

    assert "homeassistant" not in manifest
    assert hacs["homeassistant"] == ha_version


def test_bug_report_template_tracks_homeassistant_min_version() -> None:
    """Bug report template should show the canonical minimum supported HA version."""
    template = _load_yaml(_BUG_TEMPLATE)
    body = template["body"]
    ha_field = next(item for item in body if item.get("id") == "ha-version")
    attributes = ha_field["attributes"]
    ha_version = _read_homeassistant_version()

    assert ha_version in attributes["description"]
    assert ha_version in attributes["placeholder"]
