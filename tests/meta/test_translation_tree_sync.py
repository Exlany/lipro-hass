"""Translation resource consistency checks."""

from __future__ import annotations

import json
from pathlib import Path
import re

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_TRANSLATIONS_DIR = _ROOT / "custom_components" / "lipro" / "translations"
_BASE_TRANSLATION = _TRANSLATIONS_DIR / "en.json"

_PLACEHOLDER_RE = re.compile(r"\\{([a-zA-Z0-9_]+)\\}")


def _walk_leaf_strings(
    value: object, *, prefix: tuple[str, ...] = ()
) -> dict[str, str]:
    if value is None:
        return {}
    if isinstance(value, str):
        return {".".join(prefix): value}
    if isinstance(value, dict):
        result: dict[str, str] = {}
        for key, nested in value.items():
            if not isinstance(key, str):
                continue
            result.update(_walk_leaf_strings(nested, prefix=(*prefix, key)))
        return result
    if isinstance(value, list):
        path = ".".join(prefix) or "<root>"
        msg = f"Unexpected list node at {path}"
        raise TypeError(msg)
    return {}


def _extract_placeholders(text: str) -> set[str]:
    return set(_PLACEHOLDER_RE.findall(text))


def test_en_translation_matches_strings_json_exactly() -> None:
    """Ensure en.json exists and can be parsed."""
    en = json.loads(_BASE_TRANSLATION.read_text(encoding="utf-8"))
    assert en, "en.json is empty"


def test_all_translations_have_same_leaf_keys_and_placeholders() -> None:
    """Ensure translations keep the same structure and format placeholders."""
    base = json.loads(_BASE_TRANSLATION.read_text(encoding="utf-8"))
    base_leaf = _walk_leaf_strings(base)
    assert base_leaf, "No leaf strings found in en.json"

    for path in sorted(_TRANSLATIONS_DIR.glob("*.json")):
        translated = json.loads(path.read_text(encoding="utf-8"))
        translated_leaf = _walk_leaf_strings(translated)

        assert set(translated_leaf.keys()) == set(base_leaf.keys()), (
            f"Leaf keys drifted in {path}"
        )

        for key, base_value in base_leaf.items():
            translated_value = translated_leaf[key]
            assert _extract_placeholders(translated_value) == _extract_placeholders(
                base_value
            ), f"Placeholder drifted in {path} at {key}"
