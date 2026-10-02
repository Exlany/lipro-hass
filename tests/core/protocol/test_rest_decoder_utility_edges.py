"""Boundary helpers reject malformed cloud rows and keep telemetry shape-only."""

import pytest

from custom_components.lipro.core.protocol.boundary import (
    rest_decoder_utility as decoder,
)


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ([], "list[empty]"),
        ([{"secret": "value"}], "list[dict[secret]]"),
        (["secret"], "list[str]"),
        (None, "NoneType"),
        ({"data": {"secret": "value"}}, "dict[data]::data[secret]"),
        ({"devices": []}, "dict[devices]::devices[empty-list]"),
        ({"data": [{"secret": "value"}]}, "dict[data]::data[dict[secret]]"),
        ({"data": ["secret"]}, "dict[data]::data[str]"),
        ({"secret": "value"}, "dict[secret]"),
    ],
)
def test_fingerprints_do_not_include_values(payload, expected):
    assert decoder._build_payload_fingerprint(payload) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, True),
        (0, False),
        (2, True),
        (" YES ", True),
        ("false", False),
        (None, False),
    ],
)
def test_cloud_boolean_shapes(value, expected):
    assert decoder._coerce_bool(value) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [(True, None), (3, 3), (" 42 ", 42), ("bad", None), (None, None)],
)
def test_total_rejects_boolean_and_non_numeric(value, expected):
    assert decoder._coerce_total(value) == expected


def test_malformed_rows_are_ignored_without_inventing_identities():
    assert decoder._normalize_string(" ") is None
    assert decoder._normalize_device_catalog_row({"name": "no id"}) is None
    assert decoder._normalize_mesh_group_members(None) == []
    assert decoder._normalize_mesh_group_members(
        [None, {}, {"id": "one"}, {"id": "one"}]
    ) == [{"deviceId": "one"}]
    assert decoder._normalize_properties_payload(
        [None, {}, {"key": "temperature", "value": 21}]
    ) == {"temperature": 21}
    assert decoder._normalize_properties_payload(None) == {}
    assert decoder._extract_list_payload([None, {"id": 1}]) == [{"id": 1}]
    assert decoder._extract_list_payload({"data": [None, {"id": 1}]}) == [{"id": 1}]
    assert decoder._extract_list_payload({"data": "bad"}) == []
    assert decoder._resolve_device_catalog_number({"deviceId": " one "}) == "one"
    assert decoder._extract_schedule_json_source({"payload": "source"}) == "source"


@pytest.mark.parametrize("key", [None, "", "customId", "name"])
def test_metadata_never_becomes_fallback_property(key):
    assert not decoder._should_include_fallback_property(
        key, "value", excluded_keys=set()
    )
