"""Sync checks between services.yaml and translation resources."""

from __future__ import annotations

import json
from pathlib import Path
import re

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_SERVICES_YAML_PATH = _ROOT / "custom_components" / "lipro" / "services.yaml"
_TRANSLATIONS_DIR = _ROOT / "custom_components" / "lipro" / "translations"

_SERVICE_KEY_RE = re.compile(r"^([a-z0-9_]+):\s*$")
_FIELDS_BLOCK_RE = re.compile(r"^  fields:\s*$")
_FIELD_KEY_RE = re.compile(r"^    ([a-z0-9_]+):\s*$")


def _parse_services_yaml(text: str) -> dict[str, set[str]]:
    """Return {service_name: {field_name, ...}, ...} from services.yaml.

    We intentionally avoid adding a YAML dependency in the dev environment.
    This parser is strict enough for our services.yaml layout.
    """
    services: dict[str, set[str]] = {}
    current: str | None = None
    in_fields = False

    for line in text.splitlines():
        if match := _SERVICE_KEY_RE.match(line):
            current = match.group(1)
            services[current] = set()
            in_fields = False
            continue

        if current is None:
            continue

        if _FIELDS_BLOCK_RE.match(line):
            in_fields = True
            continue

        if not in_fields:
            continue

        if match := _FIELD_KEY_RE.match(line):
            services[current].add(match.group(1))
        elif line.startswith("  ") and not line.startswith("    ") and line.strip():
            # Leaving `fields:` block (e.g. `target:` section).
            in_fields = False

    return services


def _load_translation_services(path: Path) -> dict[str, set[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    services = payload.get("services") or {}

    result: dict[str, set[str]] = {}
    for key, value in services.items():
        fields = (value or {}).get("fields") or {}
        result[key] = set(fields.keys())
    return result


def test_services_translations_match_services_yaml() -> None:
    """Prevent drift between services.yaml and services translation keys."""
    yaml_services = _parse_services_yaml(
        _SERVICES_YAML_PATH.read_text(encoding="utf-8")
    )
    yaml_keys = set(yaml_services.keys())

    assert yaml_keys, "No services found in services.yaml"

    translation_paths = sorted(_TRANSLATIONS_DIR.glob("*.json"))
    assert translation_paths, "No translation files found"

    for translation_path in translation_paths:
        translated = _load_translation_services(translation_path)
        assert set(translated.keys()) == yaml_keys, (
            f"Service keys drifted in {translation_path}"
        )
        for service, fields in yaml_services.items():
            assert translated.get(service, set()) == fields, (
                f"Service fields drifted in {translation_path} for {service}"
            )
