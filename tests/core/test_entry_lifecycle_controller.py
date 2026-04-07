"""Focused tests for the entry lifecycle controller."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.control.entry_lifecycle_controller import (
    EntryLifecycleController,
)
from custom_components.lipro.control.entry_root_wiring import (
    EntryLifecycleControllerDependencies,
    build_entry_lifecycle_controller_dependencies,
)
from homeassistant.const import Platform


def _make_dependencies() -> EntryLifecycleControllerDependencies:
    service_registry = MagicMock()
    service_registry.async_sync = AsyncMock()
    service_registry.async_sync_with_lock = AsyncMock()
    service_registry.remove_all = MagicMock()
    return build_entry_lifecycle_controller_dependencies(
        logger=logging.getLogger(__name__),
        platforms=[Platform.LIGHT],
        protocol_factory=MagicMock(name="protocol_factory"),
        auth_manager_factory=MagicMock(name="auth_manager_factory"),
        coordinator_factory=MagicMock(name="coordinator_factory"),
        get_client_session=MagicMock(name="get_client_session"),
        build_entry_auth_context=MagicMock(name="build_entry_auth_context"),
        async_authenticate_entry=AsyncMock(name="async_authenticate_entry"),
        clear_entry_runtime_data=MagicMock(name="clear_entry_runtime_data"),
        get_entry_int_option=MagicMock(name="get_entry_int_option", return_value=30),
        persist_entry_tokens_if_changed=MagicMock(name="persist_entry_tokens_if_changed"),
        store_entry_options_snapshot=MagicMock(name="store_entry_options_snapshot"),
        remove_entry_options_snapshot=MagicMock(name="remove_entry_options_snapshot"),
        async_reload_entry_if_options_changed=AsyncMock(
            name="async_reload_entry_if_options_changed"
        ),
        async_ensure_runtime_infra=AsyncMock(name="async_ensure_runtime_infra"),
        setup_device_registry_listener=MagicMock(name="setup_device_registry_listener"),
        remove_device_registry_listener=MagicMock(name="remove_device_registry_listener"),
        has_other_runtime_entries=MagicMock(name="has_other_runtime_entries"),
        service_registry=service_registry,
    )


def test_controller_builds_support_from_named_dependencies() -> None:
    dependencies = _make_dependencies()

    with patch(
        "custom_components.lipro.control.entry_lifecycle_controller.EntryLifecycleSupport"
    ) as support_cls:
        controller = EntryLifecycleController(dependencies=dependencies)

    support_cls.assert_called_once_with(dependencies=dependencies)
    assert controller._support is support_cls.return_value


@pytest.mark.asyncio
async def test_async_setup_component_delegates_to_support_runtime_infra(hass) -> None:
    dependencies = _make_dependencies()

    with patch(
        "custom_components.lipro.control.entry_lifecycle_controller.EntryLifecycleSupport"
    ) as support_cls:
        support = support_cls.return_value
        support.async_ensure_runtime_infra_ready = AsyncMock()
        controller = EntryLifecycleController(dependencies=dependencies)

    assert await controller.async_setup_component(hass, {}) is True
    support.async_ensure_runtime_infra_ready.assert_awaited_once_with(hass)


@pytest.mark.asyncio
async def test_async_unload_entry_runs_support_cleanup_and_sync(hass) -> None:
    dependencies = _make_dependencies()
    entry = MockConfigEntry(domain=DOMAIN)

    with patch(
        "custom_components.lipro.control.entry_lifecycle_controller.EntryLifecycleSupport"
    ) as support_cls:
        support = support_cls.return_value
        support.async_cleanup_unloaded_entry = AsyncMock()
        support.async_sync_services_after_unload = AsyncMock()
        controller = EntryLifecycleController(dependencies=dependencies)

    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    assert await controller.async_unload_entry(hass, entry) is True
    support.async_cleanup_unloaded_entry.assert_awaited_once()
    support.async_sync_services_after_unload.assert_awaited_once_with(hass, entry.entry_id)
