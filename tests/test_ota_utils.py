"""Tests for OTA utility helpers."""

from __future__ import annotations

import json

import pytest

from custom_components.lipro.core.ota_utils import (
    extract_ota_versions,
    load_verified_firmware_manifest_file,
    normalize_versions_by_type,
    parse_ota_boollike,
    parse_verified_firmware_manifest_payload,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        ("yes", True),
        ("failed", False),
        ("unknown", None),
        (2, None),
    ],
)
def test_parse_ota_boollike(value, expected) -> None:
    assert parse_ota_boollike(value) is expected


def test_normalize_versions_by_type_filters_invalid_rows() -> None:
    result = normalize_versions_by_type(
        {
            " lipro_a ": ["1.0.0", " ", "1.0.1"],
            "": ["2.0.0"],
            123: ["3.0.0"],
            "lipro_b": "not_list",
        }
    )
    assert result == {"lipro_a": frozenset({"1.0.0", "1.0.1"})}


def test_parse_verified_firmware_manifest_payload_with_dict_fields() -> None:
    versions, by_type = parse_verified_firmware_manifest_payload(
        {
            "verified_versions": ["1.0.0", "1.0.1", ""],
            "verified_versions_by_type": {
                "type_a": ["1.0.0"],
                "type_b": ["1.0.1", " "],
            },
        }
    )
    assert versions == frozenset({"1.0.0", "1.0.1"})
    assert by_type == {
        "type_a": frozenset({"1.0.0"}),
        "type_b": frozenset({"1.0.1"}),
    }


def test_extract_ota_versions_ignores_invalid_rows() -> None:
    versions = extract_ota_versions(
        [
            {"latestVersion": "1.0.0"},
            {"upgradeVersion": "1.0.1"},
            {"latestVersion": ""},
            [],
            "bad",
            {"other": "ignored"},
        ]
    )
    assert versions == {"1.0.0", "1.0.1"}


def test_load_verified_firmware_manifest_file_handles_decode_error(tmp_path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{invalid", encoding="utf-8")

    errors: list[tuple[str, str]] = []

    def _on_error(path, err) -> None:
        errors.append((path.name, type(err).__name__))

    versions, by_type = load_verified_firmware_manifest_file(
        manifest,
        on_error=_on_error,
    )

    assert versions == frozenset()
    assert by_type == {}
    assert errors == [("manifest.json", "JSONDecodeError")]


def test_load_verified_firmware_manifest_file_parses_payload(tmp_path) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "verified_versions": ["2.0.0"],
                "verified_versions_by_type": {"type_a": ["2.0.0"]},
            }
        ),
        encoding="utf-8",
    )

    versions, by_type = load_verified_firmware_manifest_file(
        manifest,
        on_error=lambda *_: None,
    )

    assert versions == frozenset({"2.0.0"})
    assert by_type == {"type_a": frozenset({"2.0.0"})}
