"""Tests for coordinator polling and snapshot refresh behavior."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro.core.coordinator.runtime.device.snapshot import \
    RuntimeSnapshotRefreshRejectedError
from tests.conftest_shared import (
    make_api_device,
    make_device_page,
    refresh_and_sync_devices,
)


class TestCoordinatorRuntimePolling:
    """Test coordinator polling wrappers and refresh projections."""

    @pytest.mark.asyncio
    async def test_async_refresh_devices_syncs_snapshot_and_notifies_listeners(
        self, coordinator
    ):
        """Force refresh should sync snapshot, MQTT subscriptions, and listeners."""
        device = MagicMock()
        snapshot = MagicMock(devices={"dev1": device})
        coordinator._runtimes.device.refresh_devices = AsyncMock(return_value=snapshot)
        coordinator._runtimes.mqtt.bind_transport(MagicMock())
        coordinator.async_set_updated_data = MagicMock()

        with patch.object(
            type(coordinator.mqtt_service),
            "async_sync_subscriptions",
            new_callable=AsyncMock,
        ) as sync_subscriptions:
            result = await coordinator.async_refresh_devices()

        coordinator._runtimes.device.refresh_devices.assert_awaited_once_with(
            force=True
        )
        sync_subscriptions.assert_awaited_once()
        coordinator.async_set_updated_data.assert_called_once_with(coordinator.devices)
        assert result == {"dev1": device}
        assert coordinator.devices == {"dev1": device}

    @pytest.mark.asyncio
    async def test_async_refresh_devices_rejects_partial_snapshot_and_keeps_state(
        self, coordinator
    ):
        """Rejected refresh must not publish a shrunken device map."""
        existing_device = MagicMock()
        coordinator._state.devices["existing"] = existing_device
        coordinator._runtimes.device.refresh_devices = AsyncMock(
            side_effect=RuntimeSnapshotRefreshRejectedError(
                stage="fetch_page",
                page=2,
                cause_type="Exception",
                kept_last_known_good=True,
            )
        )
        coordinator.async_set_updated_data = MagicMock()

        with pytest.raises(RuntimeSnapshotRefreshRejectedError, match="page=2"):
            await coordinator.async_refresh_devices()

        coordinator.async_set_updated_data.assert_not_called()
        assert coordinator.devices == {"existing": existing_device}

    @pytest.mark.asyncio
    async def test_polling_wrappers_delegate_to_internal_polling_service(
        self, coordinator
    ) -> None:
        """Polling entrypoints should stay thin coordinator wrappers."""
        device = MagicMock()

        with (
            patch.object(
                type(coordinator._polling_service),
                "async_refresh_devices",
                new_callable=AsyncMock,
            ) as refresh_devices,
            patch.object(
                type(coordinator._polling_service),
                "get_outlet_ids_for_power_polling",
                return_value=["outlet-1"],
            ) as outlet_ids,
            patch.object(
                type(coordinator._polling_service),
                "async_run_outlet_power_polling",
                new_callable=AsyncMock,
            ) as outlet_power_polling,
            patch.object(
                type(coordinator._polling_service),
                "async_refresh_device_snapshot",
                new_callable=AsyncMock,
            ) as refresh_snapshot,
            patch.object(
                type(coordinator._polling_service),
                "async_run_status_polling",
                new_callable=AsyncMock,
            ) as status_polling,
        ):
            refresh_devices.return_value = {"dev1": device}

            assert await coordinator.async_refresh_devices() == {"dev1": device}
            assert coordinator._get_outlet_ids_for_power_polling() == ["outlet-1"]
            await coordinator._async_run_outlet_power_polling()
            await coordinator._async_refresh_device_snapshot(
                force=True,
                mqtt_timeout_seconds=5,
            )
            await coordinator._async_run_status_polling()

        refresh_devices.assert_awaited_once_with()
        outlet_ids.assert_called_once_with()
        outlet_power_polling.assert_awaited_once_with()
        refresh_snapshot.assert_awaited_once_with(
            force=True,
            mqtt_timeout_seconds=5,
        )
        status_polling.assert_awaited_once_with()

    @pytest.mark.asyncio
    async def test_status_runtime_updates_device_through_coordinator_callbacks(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Status polling should update coordinator-managed device state."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial=serial)]
        )
        coordinator.protocol.query_device_status = MagicMock(return_value=None)

        await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)
        assert device is not None
        coordinator.protocol.query_device_status = AsyncMock(
            return_value=[
                {"iotId": serial, "powerState": "1"},
                {"ignored": True},
            ]
        )

        result = await coordinator._runtimes.status.execute_status_query(
            [serial, "skip"]
        )

        assert result["updated_count"] == 1
        assert result["error"] is None
        assert device.properties["powerState"] == "1"

    @pytest.mark.asyncio
    async def test_status_runtime_respects_pending_state_filter(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ) -> None:
        """REST status polling should still honor confirmation filtering."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial=serial)]
        )
        coordinator.protocol.query_device_status = MagicMock(return_value=None)

        await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)
        assert device is not None
        coordinator.protocol.query_device_status = AsyncMock(
            return_value=[{"iotId": serial, "powerState": "1"}]
        )
        coordinator._runtimes.command.filter_pending_state_properties = MagicMock(
            return_value={}
        )
        coordinator._runtimes.command.observe_state_confirmation = MagicMock()

        result = await coordinator._runtimes.status.execute_status_query([serial])

        assert result["updated_count"] == 0
        assert result["error"] is None
        assert device.properties.get("powerState") != "1"
        coordinator._runtimes.command.filter_pending_state_properties.assert_called_once_with(
            device_serial=serial,
            properties={"powerState": "1"},
        )
        coordinator._runtimes.command.observe_state_confirmation.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_run_status_polling_refreshes_due_outlet_power(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ) -> None:
        """Outlet power polling should run on the coordinator main status path."""
        serial = "03ab5ccd7c000006"
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [
                make_api_device(
                    serial=serial,
                    device_type=6,
                    iot_name="lipro_outlet",
                    physical_model="outlet",
                )
            ]
        )
        mock_lipro_api_client.fetch_outlet_power_info = AsyncMock(
            return_value={"nowPower": 12.5}
        )

        await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)
        assert device is not None
        coordinator._runtimes.status.filter_query_candidates = MagicMock(
            return_value=[]
        )
        coordinator._runtimes.status.should_query_power = MagicMock(return_value=True)
        coordinator._runtimes.status.get_outlet_power_query_slice = MagicMock(
            return_value=[serial]
        )
        coordinator._runtimes.status.mark_power_query_complete = MagicMock()
        coordinator._runtimes.status.advance_outlet_power_cycle = MagicMock()

        await coordinator._async_run_status_polling()

        assert device.outlet_power_info is not None
        assert device.outlet_power_info["nowPower"] == 12.5
        assert "power_info" not in device.extra_data
        mock_lipro_api_client.fetch_outlet_power_info.assert_awaited_once_with(serial)
        coordinator._runtimes.status.mark_power_query_complete.assert_called_once_with()
        coordinator._runtimes.status.advance_outlet_power_cycle.assert_called_once_with(
            [serial]
        )
