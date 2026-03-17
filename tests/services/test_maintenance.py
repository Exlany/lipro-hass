"""Tests for maintenance service helper edge branches."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.services.maintenance import (
    _iter_lipro_config_entry_ids_for_device,
    _iter_runtime_entry_coordinators,
    async_setup_device_registry_listener,
)


def test_iter_runtime_entry_coordinators_skips_entries_without_runtime_data() -> None:
    coordinator = MagicMock()
    hass = MagicMock()
    hass.config_entries.async_entries.return_value = [
        SimpleNamespace(entry_id="entry-1"),
        SimpleNamespace(entry_id="entry-2", runtime_data=coordinator, options={}),
    ]

    targets = _iter_runtime_entry_coordinators(
        hass,
        domain=DOMAIN,
        requested_entry_id=None,
    )

    assert targets == [("entry-2", coordinator)]


def test_iter_lipro_config_entry_ids_for_device_filters_invalid_entries() -> None:
    hass = MagicMock()
    hass.config_entries.async_get_entry.side_effect = lambda entry_id: {
        "foreign": SimpleNamespace(domain="other_domain"),
        "lipro-entry": SimpleNamespace(domain=DOMAIN),
    }.get(entry_id)
    device_entry = SimpleNamespace(
        config_entries=["", None, "missing", "foreign", "lipro-entry"]
    )

    entry_ids = _iter_lipro_config_entry_ids_for_device(
        hass,
        domain=DOMAIN,
        device_entry=device_entry,
    )

    assert entry_ids == ["lipro-entry"]


def test_device_registry_listener_ignores_invalid_device_id() -> None:
    hass = MagicMock()
    logger = MagicMock()
    reload_entry = AsyncMock()
    hass.bus.async_listen = MagicMock(return_value=MagicMock())

    async_setup_device_registry_listener(
        hass,
        domain=DOMAIN,
        logger=logger,
        reload_entry=reload_entry,
    )
    callback = hass.bus.async_listen.call_args.args[1]

    with patch("custom_components.lipro.services.maintenance.dr.async_get") as dr_get:
        callback(
            SimpleNamespace(
                data={
                    "action": "update",
                    "changes": {"disabled_by": None},
                    "device_id": "",
                }
            )
        )

    dr_get.assert_not_called()
    hass.async_create_task.assert_not_called()


def test_device_registry_listener_ignores_unchanged_disabled_state() -> None:
    hass = MagicMock()
    logger = MagicMock()
    reload_entry = AsyncMock()
    hass.bus.async_listen = MagicMock(return_value=MagicMock())

    async_setup_device_registry_listener(
        hass,
        domain=DOMAIN,
        logger=logger,
        reload_entry=reload_entry,
    )
    callback = hass.bus.async_listen.call_args.args[1]

    device_entry = SimpleNamespace(
        disabled_by=None,
        identifiers={(DOMAIN, "03ab5ccd7c123456")},
        config_entries=["lipro-entry"],
    )
    registry = MagicMock()
    registry.async_get.return_value = device_entry

    with patch(
        "custom_components.lipro.services.maintenance.dr.async_get",
        return_value=registry,
    ):
        callback(
            SimpleNamespace(
                data={
                    "action": "update",
                    "changes": {"disabled_by": None},
                    "device_id": "dev-id",
                }
            )
        )

    hass.async_create_task.assert_not_called()


def test_device_registry_listener_skips_entry_already_pending_reload() -> None:
    hass = MagicMock()
    logger = MagicMock()
    reload_entry = AsyncMock()
    hass.bus.async_listen = MagicMock(return_value=MagicMock())

    async_setup_device_registry_listener(
        hass,
        domain=DOMAIN,
        logger=logger,
        reload_entry=reload_entry,
    )
    callback = hass.bus.async_listen.call_args.args[1]

    device_entry = SimpleNamespace(
        disabled_by="user",
        identifiers={(DOMAIN, "03ab5ccd7c123456")},
        config_entries=["lipro-entry"],
    )
    registry = MagicMock()
    registry.async_get.return_value = device_entry
    hass.config_entries.async_get_entry.return_value = SimpleNamespace(domain=DOMAIN)

    scheduled: list[Coroutine[Any, Any, Any]] = []

    def _capture_task(coro: Coroutine[Any, Any, Any]) -> MagicMock:
        scheduled.append(coro)
        task = MagicMock()
        task.done.return_value = False
        task.add_done_callback.return_value = None
        return task

    hass.async_create_task = MagicMock(side_effect=_capture_task)

    with patch(
        "custom_components.lipro.services.maintenance.dr.async_get",
        return_value=registry,
    ):
        event = SimpleNamespace(
            data={
                "action": "update",
                "changes": {"disabled_by": None},
                "device_id": "dev-id",
            }
        )
        callback(event)
        callback(event)

    assert hass.async_create_task.call_count == 1
    for coro in scheduled:
        coro.close()


def test_device_registry_listener_cancels_pending_reload_tasks_on_unsubscribe() -> None:
    hass = MagicMock()
    logger = MagicMock()
    reload_entry = AsyncMock()
    unsubscribe = MagicMock()
    hass.bus.async_listen = MagicMock(return_value=unsubscribe)

    device_entry = SimpleNamespace(
        disabled_by="user",
        identifiers={(DOMAIN, "03ab5ccd7c123456")},
        config_entries=["lipro-entry"],
    )
    registry = MagicMock()
    registry.async_get.return_value = device_entry
    hass.config_entries.async_get_entry.return_value = SimpleNamespace(domain=DOMAIN)

    scheduled: list[Coroutine[Any, Any, Any]] = []
    task = MagicMock()
    task.done.return_value = False

    def _capture_task(coro: Coroutine[Any, Any, Any]) -> MagicMock:
        scheduled.append(coro)
        return task

    hass.async_create_task = MagicMock(side_effect=_capture_task)

    stop_listener = async_setup_device_registry_listener(
        hass,
        domain=DOMAIN,
        logger=logger,
        reload_entry=reload_entry,
    )
    callback = hass.bus.async_listen.call_args.args[1]

    with patch(
        "custom_components.lipro.services.maintenance.dr.async_get",
        return_value=registry,
    ):
        callback(
            SimpleNamespace(
                data={
                    "action": "update",
                    "changes": {"disabled_by": None},
                    "device_id": "dev-id",
                }
            )
        )

    stop_listener()

    unsubscribe.assert_called_once_with()
    task.cancel.assert_called_once_with()
    for coro in scheduled:
        coro.close()


def test_device_registry_listener_clears_failed_reload_tasks() -> None:
    hass = MagicMock()
    logger = MagicMock()
    reload_entry = AsyncMock()
    hass.bus.async_listen = MagicMock(return_value=MagicMock())

    device_entry = SimpleNamespace(
        disabled_by="user",
        identifiers={(DOMAIN, "03ab5ccd7c123456")},
        config_entries=["lipro-entry"],
    )
    registry = MagicMock()
    registry.async_get.return_value = device_entry
    hass.config_entries.async_get_entry.return_value = SimpleNamespace(domain=DOMAIN)

    done_callbacks: list[Callable[[Any], None]] = []
    scheduled: list[Coroutine[Any, Any, Any]] = []
    task = MagicMock()
    task.done.return_value = False
    task.cancelled.return_value = False
    task.result.side_effect = RuntimeError("boom")
    task.add_done_callback.side_effect = done_callbacks.append

    def _capture_task(coro: Coroutine[Any, Any, Any]) -> MagicMock:
        scheduled.append(coro)
        return task

    hass.async_create_task = MagicMock(side_effect=_capture_task)

    async_setup_device_registry_listener(
        hass,
        domain=DOMAIN,
        logger=logger,
        reload_entry=reload_entry,
    )
    callback = hass.bus.async_listen.call_args.args[1]

    with patch(
        "custom_components.lipro.services.maintenance.dr.async_get",
        return_value=registry,
    ):
        event = SimpleNamespace(
            data={
                "action": "update",
                "changes": {"disabled_by": None},
                "device_id": "dev-id",
            }
        )
        callback(event)
        done_callbacks[0](task)
        callback(event)

    assert hass.async_create_task.call_count == 2
    logger.warning.assert_called_once()
    for coro in scheduled:
        coro.close()
