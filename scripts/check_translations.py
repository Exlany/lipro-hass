#!/usr/bin/env python3
"""Check translation keys consistency.

This script ensures all translation_key used in code are defined in translation files.
Run this in CI to catch missing translations early.

Usage:
    uv run python scripts/check_translations.py
"""
# ruff: noqa: T201

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


def find_translation_keys_in_code(src_dir: Path) -> set[str]:
    """Find all _attr_translation_key values in Python code."""
    keys: set[str] = set()
    pattern = re.compile(r'_attr_translation_key\s*=\s*["\'](\w+)["\']')

    for py_file in src_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        matches = pattern.findall(content)
        keys.update(matches)

    return keys


def get_translation_keys_from_file(json_path: Path) -> dict[str, set[str]]:
    """Extract entity translation keys from a translation JSON file.

    Returns:
        Dict mapping platform (e.g., "switch", "sensor") to set of keys.
    """
    if not json_path.exists():
        return {}

    with json_path.open(encoding="utf-8") as f:
        data = json.load(f)

    entity_data = data.get("entity", {})
    result: dict[str, set[str]] = {}

    for platform, entities in entity_data.items():
        if isinstance(entities, dict):
            result[platform] = set(entities.keys())

    return result


def flatten_translation_keys(keys_by_platform: dict[str, set[str]]) -> set[str]:
    """Flatten platform-grouped keys into a single set."""
    all_keys: set[str] = set()
    for keys in keys_by_platform.values():
        all_keys.update(keys)
    return all_keys


def main() -> int:
    """Main entry point."""
    # Paths
    root = Path(__file__).parent.parent
    src_dir = root / "custom_components" / "lipro"
    translations_dir = src_dir / "translations"
    en_json = translations_dir / "en.json"

    # Find keys in code
    code_keys = find_translation_keys_in_code(src_dir)
    print(f"Found {len(code_keys)} translation keys in code:")
    for key in sorted(code_keys):
        print(f"  - {key}")
    print()

    # Check each translation file
    errors: list[str] = []

    if not en_json.exists():
        errors.append(f"Missing translation file: {en_json}")

    translation_paths = sorted(translations_dir.glob("*.json"))
    if not translation_paths:
        errors.append(f"No translations found in: {translations_dir}")

    for json_path in translation_paths:
        if not json_path.exists():
            errors.append(f"Missing translation file: {json_path}")
            continue

        keys_by_platform = get_translation_keys_from_file(json_path)
        file_keys = flatten_translation_keys(keys_by_platform)

        missing = code_keys - file_keys
        if missing:
            errors.append(
                f"{json_path.name}: Missing keys: {', '.join(sorted(missing))}"
            )
        else:
            print(f"✓ {json_path.name}: All keys present")

    # Check key consistency between translations (using en.json as baseline)
    if en_json.exists():
        base_keys = flatten_translation_keys(get_translation_keys_from_file(en_json))
        for json_path in translation_paths:
            file_keys = flatten_translation_keys(
                get_translation_keys_from_file(json_path)
            )
            if file_keys != base_keys:
                diff = file_keys.symmetric_difference(base_keys)
                errors.append(f"{json_path.name} keys differ from en.json: {diff}")

    # Report results
    print()
    if errors:
        print("❌ Translation check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("✅ All translation checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
