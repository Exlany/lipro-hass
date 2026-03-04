"""Version metadata consistency checks."""

from __future__ import annotations

import json
from pathlib import Path
import re
import tomllib

_ROOT = Path(__file__).resolve().parents[1]
_PYPROJECT = _ROOT / "pyproject.toml"
_MANIFEST = _ROOT / "custom_components" / "lipro" / "manifest.json"
_HACS = _ROOT / "hacs.json"
_BASE_CONST = _ROOT / "custom_components" / "lipro" / "const" / "base.py"

_BASE_VERSION_RE = re.compile(r'^VERSION:\s+Final\s*=\s*"(?P<version>[^"]+)"\s*$')


def _read_base_version() -> str:
    for line in _BASE_CONST.read_text(encoding="utf-8").splitlines():
        if match := _BASE_VERSION_RE.match(line.strip()):
            return match.group("version")
    raise AssertionError("Could not find VERSION constant in const/base.py")


def test_integration_version_is_consistent() -> None:
    """pyproject.toml, manifest.json and const/base.py should agree on version."""
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))

    assert (
        manifest["version"] == pyproject["project"]["version"] == _read_base_version()
    )


def test_homeassistant_min_version_is_consistent() -> None:
    """Keep Home Assistant version pin consistent across repo metadata."""
    pyproject = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    hacs = json.loads(_HACS.read_text(encoding="utf-8"))

    dev_deps: list[str] = pyproject["project"]["optional-dependencies"]["dev"]
    ha_pin = next(dep for dep in dev_deps if dep.startswith("homeassistant=="))
    ha_version = ha_pin.split("==", 1)[1]

    assert manifest["homeassistant"] == hacs["homeassistant"] == ha_version
