"""Formal control-plane lifecycle owner for Lipro config entries."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, cast

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..const.config import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .entry_lifecycle_failures import (
    DEGRADABLE_UNLOAD_EXCEPTIONS,
    RELOAD_FAILURE_EXCEPTIONS,
    SETUP_FAILURE_EXCEPTIONS,
    LifecycleFailureContract,
    SetupLifecycleFailure,
    classify_reload_failure,
    classify_setup_failure,
    classify_unload_failure,
)
from .entry_lifecycle_support import (
    CoordinatorRuntimeLike,
    EntryLifecycleSupport,
    EntryLike,
    EntrySetupArtifacts,
)
from .entry_root_wiring import EntryLifecycleControllerDependencies


class EntryLifecycleController:
    """Own integration setup/unload/reload orchestration."""

    def __init__(
        self,
        *,
        dependencies: EntryLifecycleControllerDependencies,
    ) -> None:
        """Initialize the control-plane owner with explicit collaborators."""
        self._logger = dependencies.logger
        self._platforms = dependencies.platforms
        self._get_entry_int_option = dependencies.get_entry_int_option
        self._async_reload_entry_if_options_changed = (
            dependencies.async_reload_entry_if_options_changed
        )
        self._support = EntryLifecycleSupport(dependencies=dependencies)

    def _build_reload_options_listener(
        self,
    ) -> Callable[[HomeAssistant, ConfigEntry[Any]], Coroutine[Any, Any, None]]:
        """Build the stable update-listener bridge for options reloads."""

        async def _reload_options_bridge(
            bridge_hass: HomeAssistant,
            bridge_entry: ConfigEntry[Any],
        ) -> None:
            await self._async_reload_entry_if_options_changed(
                bridge_hass,
                cast(EntryLike, bridge_entry),
            )

        return _reload_options_bridge

    def _resolve_scan_interval(self, entry: EntryLike) -> int:
        """Resolve one entry scan interval through the shared option coercion path."""
        return self._get_entry_int_option(
            entry,
            option_name=CONF_SCAN_INTERVAL,
            default=DEFAULT_SCAN_INTERVAL,
            min_value=MIN_SCAN_INTERVAL,
            max_value=MAX_SCAN_INTERVAL,
            logger=self._logger,
        )

    async def _async_prepare_entry_setup(
        self,
        hass: HomeAssistant,
        entry: EntryLike,
    ) -> EntrySetupArtifacts:
        """Prepare one entry until a coordinator is ready for activation."""
        return await self._support.async_prepare_entry_setup(
            hass,
            entry,
            resolve_scan_interval=self._resolve_scan_interval,
        )

    async def _async_run_entry_activation(
        self,
        *,
        hass: HomeAssistant,
        entry: EntryLike,
        setup_artifacts: EntrySetupArtifacts,
    ) -> None:
        """Run prepared setup activation with typed contracts and guaranteed cleanup."""
        activation_completed = False
        lifecycle_failure: SetupLifecycleFailure | None = None

        try:
            await self._support.async_activate_entry_setup(
                hass,
                entry,
                setup_artifacts,
                reload_listener=self._build_reload_options_listener(),
            )
            activation_completed = True
        except asyncio.CancelledError:
            raise
        except SETUP_FAILURE_EXCEPTIONS as err:
            lifecycle_failure = err
            raise
        finally:
            if not activation_completed:
                if lifecycle_failure is not None:
                    self._log_lifecycle_contract(
                        classify_setup_failure(lifecycle_failure)
                    )
                await self._support.async_abort_setup(
                    hass,
                    entry,
                    setup_artifacts.coordinator,
                )

    def _log_lifecycle_contract(
        self,
        contract: LifecycleFailureContract,
        *,
        warning: bool = False,
    ) -> None:
        """Log one named lifecycle arbitration contract at the intended level."""
        log = self._logger.warning if warning else self._logger.debug
        log(
            "Lifecycle %s contract %s -> %s (%s)",
            contract.stage,
            contract.contract_name,
            contract.handling_policy,
            contract.error_type,
        )

    async def _async_shutdown_on_unload(
        self,
        coordinator: CoordinatorRuntimeLike,
    ) -> None:
        """Shutdown runtime data during unload while preserving cancel semantics."""
        try:
            await coordinator.async_shutdown()
        except asyncio.CancelledError:
            raise
        except DEGRADABLE_UNLOAD_EXCEPTIONS as err:
            self._log_lifecycle_contract(
                classify_unload_failure(err),
                warning=True,
            )

    async def async_setup_component(self, hass: HomeAssistant, config: object) -> bool:
        """Set up shared runtime infrastructure for the integration."""
        del config
        await self._support.async_ensure_runtime_infra_ready(hass)
        return True

    async def async_setup_entry(self, hass: HomeAssistant, entry: EntryLike) -> bool:
        """Set up one Lipro config entry."""
        try:
            setup_artifacts = await self._async_prepare_entry_setup(hass, entry)
        except asyncio.CancelledError:
            raise
        except SETUP_FAILURE_EXCEPTIONS as err:
            self._log_lifecycle_contract(classify_setup_failure(err))
            raise

        await self._async_run_entry_activation(
            hass=hass,
            entry=entry,
            setup_artifacts=setup_artifacts,
        )
        return True

    async def async_unload_entry(self, hass: HomeAssistant, entry: EntryLike) -> bool:
        """Unload one Lipro config entry."""
        result = await hass.config_entries.async_unload_platforms(
            entry, self._platforms
        )
        if not result:
            return False

        await self._support.async_cleanup_unloaded_entry(
            hass,
            entry,
            shutdown_on_unload=self._async_shutdown_on_unload,
        )
        await self._support.async_sync_services_after_unload(hass, entry.entry_id)
        return True

    async def async_reload_entry(self, hass: HomeAssistant, entry: EntryLike) -> None:
        """Reload one config entry."""
        try:
            await hass.config_entries.async_reload(entry.entry_id)
        except asyncio.CancelledError:
            raise
        except RELOAD_FAILURE_EXCEPTIONS as err:
            self._log_lifecycle_contract(classify_reload_failure(err))
            raise
