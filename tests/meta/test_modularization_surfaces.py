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


def test_coordinator_runtime_home_is_localized_to_coordinator_entry() -> None:
    """`Coordinator` should remain at the HA runtime home, not `core` root."""
    from custom_components.lipro import coordinator_entry, core
    from custom_components.lipro.core import coordinator

    assert not hasattr(core, "Coordinator")
    assert hasattr(coordinator_entry, "Coordinator")
    assert hasattr(coordinator, "Coordinator")
    assert not hasattr(core, "LiproDataUpdateCoordinator")
    assert not hasattr(coordinator, "LiproDataUpdateCoordinator")


def test_phase_53_support_modules_are_not_promoted_to_public_packages() -> None:
    """Support-only seams introduced in Phase 53 must stay internal."""
    from custom_components.lipro import control
    from custom_components.lipro.core import coordinator

    assert not hasattr(control, "EntryLifecycleSupport")
    assert not hasattr(control, "build_entry_lifecycle_controller_kwargs")
    assert not hasattr(coordinator, "CoordinatorServiceLayer")

