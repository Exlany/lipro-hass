"""Tests for OTA utility helpers."""

from __future__ import annotations

import json
from typing import Any, cast

import pytest

from custom_components.lipro.core.ota.manifest import (
    coerce_command_properties,
    extract_install_command,
    extract_ota_versions,
    extract_version_set,
    first_bool,
    first_text,
    load_verified_firmware_manifest_file,
    matches_certified_versions,
    normalize_command_properties,
    normalize_versions_by_type,
    parse_install_command_payload,
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


def test_first_text_returns_none_for_non_dict_payload() -> None:
    assert first_text(None, ("key",)) is None


def test_first_bool_returns_none_for_non_dict_payload() -> None:
    assert first_bool(cast(dict[str, Any] | None, "invalid"), ("key",)) is None


def test_normalize_versions_by_type_returns_empty_for_non_dict_payload() -> None:
    assert normalize_versions_by_type(["not", "a", "dict"]) == {}


def test_parse_verified_firmware_manifest_payload_accepts_list_payload() -> None:
    versions, by_type = parse_verified_firmware_manifest_payload(["1.0.0", " ", 2])
    assert versions == frozenset({"1.0.0", "2"})
    assert by_type == {}


def test_parse_verified_firmware_manifest_payload_non_mapping_returns_empty() -> None:
    versions, by_type = parse_verified_firmware_manifest_payload("invalid")
    assert versions == frozenset()
    assert by_type == {}


def test_parse_verified_firmware_manifest_payload_firmware_list_skips_invalid_rows() -> (
    None
):
    versions, by_type = parse_verified_firmware_manifest_payload(
        {
            "firmware_list": [
                "not-a-dict",
                {"certified": True, "iotName": "type_a"},
                {
                    "certified": True,
                    "latestVersion": "1.2.3",
                    "bleName": "CTRL",
                },
            ],
        }
    )
    assert versions == frozenset({"1.2.3"})
    assert by_type == {"ctrl": frozenset({"1.2.3"})}


def test_extract_version_set_returns_empty_for_non_dict_payload() -> None:
    assert extract_version_set(None, ("key",)) == set()


def test_matches_certified_versions_requires_installed_version_for_relaxed_match() -> (
    None
):
    def _version_is_newer(_: str, __: str) -> bool:  # pragma: no cover
        raise AssertionError("is_version_newer should not be called")

    assert (
        matches_certified_versions(
            {"2.0.0"},
            installed=None,
            latest=None,
            is_version_newer=_version_is_newer,
        )
        is False
    )


def test_command_property_normalization_handles_invalid_payloads() -> None:
    assert coerce_command_properties(None) is None
    assert coerce_command_properties("invalid") is None
    assert coerce_command_properties({None: "x", "a": None, "b": 1}) == [
        {"key": "b", "value": "1"}
    ]
    assert coerce_command_properties(["invalid", {"key": "a", "value": "b"}]) == [
        {"key": "a", "value": "b"}
    ]

    assert (
        normalize_command_properties(
            {"props": "invalid"},
            properties_keys=("props",),
        )
        is None
    )


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ("  install  ", ("install", None)),
        ("  ", None),
    ],
)
def test_parse_install_command_payload_accepts_text(payload, expected) -> None:
    assert (
        parse_install_command_payload(
            payload,
            command_keys=("command",),
            properties_keys=("properties",),
        )
        == expected
    )


def test_extract_install_command_returns_none_for_non_dict_rows() -> None:
    assert (
        extract_install_command(
            cast(dict[str, Any] | None, "invalid"),
            container_keys=("container",),
            command_keys=("command",),
            properties_keys=("properties",),
        )
        is None
    )


def test_extract_ota_versions_returns_empty_for_non_list_payload() -> None:
    assert extract_ota_versions("invalid") == set()
