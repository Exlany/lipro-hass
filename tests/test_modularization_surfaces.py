"""Compatibility checks for modularized service/API helpers."""

from __future__ import annotations


def test_service_contract_symbols_are_not_reexported() -> None:
    """`custom_components.lipro` should no longer expose legacy contract symbols."""
    from custom_components import lipro

    assert not hasattr(lipro, "SERVICE_SEND_COMMAND")
    assert not hasattr(lipro, "ATTR_DEVICE_ID")
    assert not hasattr(lipro, "SERVICE_SEND_COMMAND_SCHEMA")


def test_api_helpers_use_canonical_submodule_symbols() -> None:
    """`custom_components.lipro.core.api` should not expose legacy alias helpers."""
    from custom_components.lipro.core import api

    assert not hasattr(api, "_mask_sensitive_data")
    assert not hasattr(api, "_normalize_response_code")
    assert not hasattr(api, "_COMMAND_PACING_CACHE_MAX_SIZE")
