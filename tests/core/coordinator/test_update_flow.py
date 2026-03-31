"""Tests for coordinator update-flow delegation and error mapping."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.api import LiproAuthError, LiproConnectionError
from custom_components.lipro.core.coordinator.runtime.device.snapshot import (
    RuntimeSnapshotRefreshRejectedError,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed
from tests.conftest_shared import make_api_device, make_device_page


class TestCoordinatorUpdateFlow:
    """Test coordinator update flow."""

    @pytest.mark.asyncio
    async def test_update_calls_auth_check(
        self, coordinator, mock_lipro_api_client, mock_auth_manager
    ):
        """Update flow should call authentication check first."""
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device()]
        )

        await coordinator._async_update_data()

        mock_auth_manager.async_ensure_authenticated.assert_awaited()

    @pytest.mark.asyncio
    async def test_update_data_delegates_to_update_cycle_collaborator(
        self, coordinator
    ) -> None:
        """Coordinator root should keep update-cycle orchestration delegated."""
        device = MagicMock()
        coordinator._update_cycle.async_update_data = AsyncMock(
            return_value={"dev1": device}
        )

        assert await coordinator._async_update_data() == {"dev1": device}

        coordinator._update_cycle.async_update_data.assert_awaited_once_with()

    @pytest.mark.asyncio
    async def test_auth_error_raises_config_entry_auth_failed(
        self, coordinator, mock_auth_manager
    ):
        """Auth errors should raise ConfigEntryAuthFailed."""
        mock_auth_manager.async_ensure_authenticated.side_effect = LiproAuthError(
            "Auth failed"
        )

        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

        telemetry = coordinator.telemetry_service.build_snapshot()
        assert telemetry["last_runtime_failure_stage"] == "auth"
        assert telemetry["failure_summary"]["error_type"] == "LiproAuthError"

    @pytest.mark.asyncio
    async def test_connection_error_raises_update_failed(
        self, coordinator, mock_auth_manager
    ):
        """Connection errors should raise UpdateFailed."""
        mock_auth_manager.async_ensure_authenticated.side_effect = LiproConnectionError(
            "Connection failed"
        )

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

        telemetry = coordinator.telemetry_service.build_snapshot()
        assert telemetry["last_runtime_failure_stage"] == "protocol"
        assert telemetry["failure_summary"]["error_type"] == "LiproConnectionError"

    @pytest.mark.asyncio
    async def test_timeout_error_raises_timeout_update_failed(
        self, coordinator, mock_auth_manager
    ):
        """Update timeout should surface as a timeout-specific failure."""
        mock_auth_manager.async_ensure_authenticated.side_effect = TimeoutError()

        with pytest.raises(UpdateFailed, match="Update timeout"):
            await coordinator._async_update_data()

        telemetry = coordinator.telemetry_service.build_snapshot()
        assert telemetry["last_runtime_failure_stage"] == "timeout"
        assert telemetry["failure_summary"]["error_type"] == "TimeoutError"

    @pytest.mark.asyncio
    async def test_unexpected_error_raises_generic_update_failed(
        self, coordinator, mock_auth_manager
    ):
        """Unexpected update errors should map to a stable failure."""
        mock_auth_manager.async_ensure_authenticated.side_effect = RuntimeError("boom")

        with pytest.raises(UpdateFailed, match="Unexpected update failure"):
            await coordinator._async_update_data()

        telemetry = coordinator.telemetry_service.build_snapshot()
        assert telemetry["last_runtime_failure_stage"] == "unexpected"
        assert telemetry["failure_summary"]["error_type"] == "RuntimeError"

    @pytest.mark.asyncio
    async def test_snapshot_rejection_raises_update_failed_and_records_runtime_failure(
        self, coordinator, mock_auth_manager
    ):
        """Structured snapshot rejection should use the runtime failure path."""
        mock_auth_manager.async_ensure_authenticated.return_value = None
        coordinator._runtimes.device.should_refresh_device_list = MagicMock(
            return_value=True
        )
        coordinator._runtimes.device.refresh_devices = AsyncMock(
            side_effect=RuntimeSnapshotRefreshRejectedError(
                stage="fetch_page",
                page=2,
                cause_type="Exception",
            )
        )

        with pytest.raises(UpdateFailed, match="stage=fetch_page"):
            await coordinator._async_update_data()

        telemetry = coordinator.telemetry_service.build_snapshot()
        assert telemetry["last_runtime_failure_stage"] == "runtime"
        assert telemetry["failure_summary"]["error_type"] == (
            "RuntimeSnapshotRefreshRejectedError"
        )
