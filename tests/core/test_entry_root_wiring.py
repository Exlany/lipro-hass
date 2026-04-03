"""Focused tests for entry root wiring helpers."""

from __future__ import annotations

import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from custom_components.lipro.control.entry_root_wiring import (
    build_entry_lifecycle_controller,
    build_entry_lifecycle_controller_dependencies,
    build_service_registry,
)
from homeassistant.const import Platform


def _make_service_registry() -> MagicMock:
    registry = MagicMock()
    registry.async_sync = AsyncMock()
    registry.async_sync_with_lock = AsyncMock()
    registry.remove_all = MagicMock()
    return registry


def test_build_entry_lifecycle_controller_dependencies_returns_typed_bundle() -> None:
    logger = logging.getLogger(__name__)
    service_registry = _make_service_registry()

    dependencies = build_entry_lifecycle_controller_dependencies(
        logger=logger,
        platforms=[Platform.LIGHT, Platform.SENSOR],
        protocol_factory=MagicMock(name="protocol_factory"),
        auth_manager_factory=MagicMock(name="auth_manager_factory"),
        coordinator_factory=MagicMock(name="coordinator_factory"),
        get_client_session=MagicMock(name="get_client_session"),
        build_entry_auth_context=MagicMock(name="build_entry_auth_context"),
        async_authenticate_entry=AsyncMock(name="async_authenticate_entry"),
        clear_entry_runtime_data=MagicMock(name="clear_entry_runtime_data"),
        get_entry_int_option=MagicMock(name="get_entry_int_option"),
        persist_entry_tokens_if_changed=MagicMock(
            name="persist_entry_tokens_if_changed"
        ),
        store_entry_options_snapshot=MagicMock(name="store_entry_options_snapshot"),
        remove_entry_options_snapshot=MagicMock(name="remove_entry_options_snapshot"),
        async_reload_entry_if_options_changed=AsyncMock(
            name="async_reload_entry_if_options_changed"
        ),
        async_ensure_runtime_infra=AsyncMock(name="async_ensure_runtime_infra"),
        setup_device_registry_listener=MagicMock(name="setup_device_registry_listener"),
        remove_device_registry_listener=MagicMock(
            name="remove_device_registry_listener"
        ),
        has_other_runtime_entries=MagicMock(name="has_other_runtime_entries"),
        service_registry=service_registry,
    )

    assert dependencies.logger is logger
    assert dependencies.platforms == (Platform.LIGHT, Platform.SENSOR)
    assert dependencies.service_registry is service_registry


def test_build_entry_lifecycle_controller_passes_named_dependencies() -> None:
    controller = MagicMock(name="controller")
    controller_factory = MagicMock(return_value=controller)
    dependencies = build_entry_lifecycle_controller_dependencies(
        logger=logging.getLogger(__name__),
        platforms=[Platform.LIGHT],
        protocol_factory=MagicMock(),
        auth_manager_factory=MagicMock(),
        coordinator_factory=MagicMock(),
        get_client_session=MagicMock(),
        build_entry_auth_context=MagicMock(),
        async_authenticate_entry=AsyncMock(),
        clear_entry_runtime_data=MagicMock(),
        get_entry_int_option=MagicMock(),
        persist_entry_tokens_if_changed=MagicMock(),
        store_entry_options_snapshot=MagicMock(),
        remove_entry_options_snapshot=MagicMock(),
        async_reload_entry_if_options_changed=AsyncMock(),
        async_ensure_runtime_infra=AsyncMock(),
        setup_device_registry_listener=MagicMock(),
        remove_device_registry_listener=MagicMock(),
        has_other_runtime_entries=MagicMock(),
        service_registry=_make_service_registry(),
    )

    built = build_entry_lifecycle_controller(
        controller_factory=controller_factory,
        controller_dependencies=dependencies,
    )

    controller_factory.assert_called_once_with(dependencies=dependencies)
    assert built is controller


async def test_build_service_registry_keeps_public_and_developer_tables_separate() -> (
    None
):
    async_setup_services = AsyncMock()
    remove_services = MagicMock()
    registrations = SimpleNamespace(
        PUBLIC_SERVICE_REGISTRATIONS=("public",),
        DEVELOPER_SERVICE_REGISTRATIONS=("developer",),
        SERVICE_REGISTRATIONS=("public", "developer"),
        has_debug_mode_runtime_entry=MagicMock(return_value=False),
    )
    registry = build_service_registry(
        domain="lipro",
        registrations=registrations,
        async_setup_services=async_setup_services,
        remove_services=remove_services,
        get_runtime_infra_lock=MagicMock(return_value=None),
    )

    await registry.async_sync(MagicMock())

    async_setup_services.assert_awaited_once()
    remove_services.assert_called_once()
