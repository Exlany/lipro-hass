"""Shared OTA payload normalization helpers.

This package exposes a small, stable surface for OTA parsing/normalization used
by the update platform while keeping the implementation in focused modules.
"""

from __future__ import annotations

from .manifest import (
    DEFAULT_OTA_VERSION_KEYS,
    MANIFEST_TYPE_KEY_PRIORITY,
    append_unique_normalized,
    build_manifest_type_candidates,
    coerce_command_properties,
    extract_install_command,
    extract_ota_versions,
    extract_version_set,
    first_bool,
    first_text,
    load_verified_firmware_manifest_file,
    matches_certified_versions,
    matches_manifest_certification,
    normalize_command_properties,
    normalize_version_list,
    normalize_versions_by_type,
    parse_install_command_payload,
    parse_ota_boollike,
    parse_verified_firmware_manifest_payload,
)

__all__ = [
    "DEFAULT_OTA_VERSION_KEYS",
    "MANIFEST_TYPE_KEY_PRIORITY",
    "append_unique_normalized",
    "build_manifest_type_candidates",
    "coerce_command_properties",
    "extract_install_command",
    "extract_ota_versions",
    "extract_version_set",
    "first_bool",
    "first_text",
    "load_verified_firmware_manifest_file",
    "matches_certified_versions",
    "matches_manifest_certification",
    "normalize_command_properties",
    "normalize_version_list",
    "normalize_versions_by_type",
    "parse_install_command_payload",
    "parse_ota_boollike",
    "parse_verified_firmware_manifest_payload",
]
