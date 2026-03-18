"""Repository asset guard for the bundled firmware trust-root asset."""

from __future__ import annotations

import json

from custom_components.lipro import firmware_manifest
from custom_components.lipro.core.ota.manifest import (
    parse_verified_firmware_manifest_payload,
)


def test_repo_firmware_trust_root_asset_is_present_and_parseable() -> None:
    path = firmware_manifest.LOCAL_FIRMWARE_TRUST_ROOT_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    versions, versions_by_type = parse_verified_firmware_manifest_payload(payload)

    assert path.name == firmware_manifest.LOCAL_FIRMWARE_TRUST_ROOT_FILENAME
    assert versions
    assert versions_by_type


def test_repo_firmware_trust_root_keeps_certified_rows_well_formed() -> None:
    payload = json.loads(
        firmware_manifest.LOCAL_FIRMWARE_TRUST_ROOT_PATH.read_text(
            encoding="utf-8"
        )
    )
    rows = payload.get("firmware_list")

    assert isinstance(rows, list)
    certified_rows = [
        row for row in rows if isinstance(row, dict) and row.get("certified") is True
    ]
    assert certified_rows
    for row in certified_rows:
        assert row.get("firmwareVersion") or row.get("version")
        assert row.get("firmwareUrl")
        assert row.get("bleName") or row.get("iotName")
