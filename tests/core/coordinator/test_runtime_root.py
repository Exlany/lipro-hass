"""Tests for coordinator runtime-root behavior."""

from __future__ import annotations

from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro.core.api import LiproAuthError
from custom_components.lipro.core.coordinator.factory import (
    CoordinatorBootstrapArtifact,
)
from custom_components.lipro.core.coordinator.runtime_wiring import (
    CoordinatorServiceLayer,
    CoordinatorSupportServices,
)
from custom_components.lipro.core.coordinator.services import (
    CoordinatorAuthService,
    CoordinatorCommandService,
    CoordinatorDeviceRefreshService,
    CoordinatorMqttService,
    CoordinatorPollingService,
    CoordinatorProtocolService,
    CoordinatorScheduleService,
    CoordinatorSignalService,
    CoordinatorStateService,
    CoordinatorTelemetryService,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from tests.conftest_shared import (
    make_api_device,
    make_device_page,
    refresh_and_sync_devices,
)


class TestCoordinatorRuntimeRoot:
    """Test coordinator root callbacks and runtime ownership."""

    def test_coordinator_consumes_named_bootstrap_artifact(
        self,
        hass,
        mock_lipro_api_client,
        mock_auth_manager,
        config_entry,
        patch_anonymous_share_manager,
    ) -> None:
        """Coordinator should bind one explicit bootstrap artifact without drift."""
        from custom_components.lipro.core.coordinator import Coordinator

        state = MagicMock(name="state")
        runtimes = MagicMock(name="runtimes")
        update_cycle = MagicMock(name="update_cycle")
        service_layer = CoordinatorServiceLayer(
            command_service=cast("CoordinatorCommandService", MagicMock(name="command_service")),
            mqtt_service=cast("CoordinatorMqttService", MagicMock(name="mqtt_service")),
            state_service=cast("CoordinatorStateService", MagicMock(name="state_service")),
            polling_service=cast("CoordinatorPollingService", MagicMock(name="polling_service")),
            schedule_service=cast("CoordinatorScheduleService", MagicMock(name="schedule_service")),
            device_refresh_service=cast(
                "CoordinatorDeviceRefreshService",
                MagicMock(name="device_refresh_service"),
            ),
            telemetry_service=cast(
                "CoordinatorTelemetryService",
                MagicMock(name="telemetry_service"),
            ),
        )
        support_services = CoordinatorSupportServices(
            auth_service=cast("CoordinatorAuthService", MagicMock(name="auth_service")),
            protocol_service=cast(
                "CoordinatorProtocolService", MagicMock(name="protocol_service")
            ),
            signal_service=cast(
                "CoordinatorSignalService", MagicMock(name="signal_service")
            ),
        )
        artifact = CoordinatorBootstrapArtifact(
            state=state,
            runtimes=runtimes,
            support_services=support_services,
            service_layer=service_layer,
            update_cycle=update_cycle,
        )

        with patch(
            "custom_components.lipro.core.coordinator.coordinator.RuntimeOrchestrator.build_bootstrap_artifact",
            return_value=artifact,
        ) as build_bootstrap:
            coordinator = Coordinator(
                hass,
                mock_lipro_api_client,
                mock_auth_manager,
                config_entry,
            )

        assert build_bootstrap.call_count == 1
        assert "signal_service" not in build_bootstrap.call_args.kwargs
        assert "protocol_service" not in build_bootstrap.call_args.kwargs
        assert build_bootstrap.call_args.kwargs["polling_updater"] is coordinator
        assert coordinator._state is state
        assert coordinator._runtimes is runtimes
        assert coordinator.auth_service is support_services.auth_service
        assert coordinator.protocol_service is support_services.protocol_service
        assert coordinator.signal_service is support_services.signal_service
        assert coordinator.command_service is service_layer.command_service
        assert coordinator.mqtt_service is service_layer.mqtt_service
        assert coordinator.state_service is service_layer.state_service
        assert coordinator._polling_service is service_layer.polling_service
        assert coordinator.schedule_service is service_layer.schedule_service
        assert coordinator.device_refresh_service is service_layer.device_refresh_service
        assert coordinator.telemetry_service is service_layer.telemetry_service
        assert coordinator._update_cycle is update_cycle

    def test_coordinator_keeps_internal_runtime_registry(self, coordinator):
        """Coordinator should keep runtimes internal behind one registry."""
        assert hasattr(coordinator, "_runtimes")
        assert hasattr(coordinator._runtimes, "device")
        assert hasattr(coordinator._runtimes, "status")
        assert hasattr(coordinator._runtimes, "state")
        assert hasattr(coordinator._runtimes, "command")
        assert hasattr(coordinator._runtimes, "mqtt")

    def test_coordinator_has_service_layer(self, coordinator):
        """Coordinator exposes the formal service layer."""
        assert hasattr(coordinator, "auth_service")
        assert hasattr(coordinator, "device_refresh_service")
        assert hasattr(coordinator, "state_service")
        assert hasattr(coordinator, "command_service")
        assert hasattr(coordinator, "mqtt_service")
        assert hasattr(coordinator, "telemetry_service")
        assert hasattr(coordinator, "signal_service")
        assert hasattr(coordinator, "_polling_service")

    def test_group_reconciliation_callback_records_signal_and_requests_refresh(
        self, coordinator
    ) -> None:
        coordinator._runtimes.device.request_force_refresh = MagicMock()

        coordinator.signal_service.schedule_group_reconciliation("Group 1", 2.0)

        assert coordinator.telemetry_service.build_snapshot()["signals"] == {
            "connect_state_event_count": 0,
            "group_reconciliation_request_count": 1,
            "recent_connect_state_events": [],
            "recent_group_reconciliation_requests": [
                {"device_name": "Group 1", "timestamp": 2.0}
            ],
        }
        coordinator._runtimes.device.request_force_refresh.assert_called_once_with()

    def test_connect_state_callback_records_signal(self, coordinator) -> None:
        coordinator.signal_service.record_connect_state("dev1", 1.5, True)

        assert coordinator.telemetry_service.build_snapshot()["signals"] == {
            "connect_state_event_count": 1,
            "group_reconciliation_request_count": 0,
            "recent_connect_state_events": [
                {"device_serial": "dev1", "timestamp": 1.5, "is_online": True}
            ],
            "recent_group_reconciliation_requests": [],
        }

    @pytest.mark.asyncio
    async def test_async_shutdown_releases_runtime_resources(self, coordinator) -> None:
        """Coordinator shutdown should stop MQTT and clear owned resources."""
        coordinator._runtimes.mqtt.clear_disconnect_notification = AsyncMock()
        coordinator._runtimes.mqtt.disconnect = AsyncMock()
        coordinator._runtimes.mqtt.reset = MagicMock()
        coordinator._runtimes.device.reset = MagicMock()
        coordinator._state.background_task_manager.cancel_all = AsyncMock()
        coordinator.protocol.attach_mqtt_facade = MagicMock()
        coordinator._runtimes.mqtt.detach_transport = MagicMock()

        with (
            patch(
                "custom_components.lipro.core.coordinator.coordinator.CoordinatorCommandService.async_shutdown",
                new_callable=AsyncMock,
            ) as command_shutdown,
            patch(
                "custom_components.lipro.core.coordinator.coordinator.DataUpdateCoordinator.async_shutdown",
                new_callable=AsyncMock,
            ) as base_shutdown,
        ):
            await coordinator.async_shutdown()

        coordinator._runtimes.mqtt.clear_disconnect_notification.assert_awaited_once()
        command_shutdown.assert_awaited_once()
        coordinator._runtimes.mqtt.disconnect.assert_awaited_once()
        coordinator._state.background_task_manager.cancel_all.assert_awaited_once()
        coordinator._runtimes.mqtt.reset.assert_called_once()
        coordinator._runtimes.device.reset.assert_called_once()
        coordinator.protocol.attach_mqtt_facade.assert_called_once_with(None)
        coordinator._runtimes.mqtt.detach_transport.assert_called_once()
        base_shutdown.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_async_shutdown_continues_after_best_effort_failures(
        self, coordinator
    ) -> None:
        """Best-effort shutdown failures must not block final cleanup."""
        coordinator._runtimes.mqtt.clear_disconnect_notification = AsyncMock(
            side_effect=RuntimeError("notification boom")
        )
        coordinator._runtimes.mqtt.disconnect = AsyncMock(
            side_effect=RuntimeError("disconnect boom")
        )
        coordinator._runtimes.mqtt.reset = MagicMock()
        coordinator._runtimes.device.reset = MagicMock()
        coordinator._state.background_task_manager.cancel_all = AsyncMock(
            side_effect=RuntimeError("cancel boom")
        )
        coordinator.protocol.attach_mqtt_facade = MagicMock()
        coordinator._runtimes.mqtt.detach_transport = MagicMock()

        with (
            patch(
                "custom_components.lipro.core.coordinator.coordinator.CoordinatorCommandService.async_shutdown",
                new_callable=AsyncMock,
            ) as command_shutdown,
            patch(
                "custom_components.lipro.core.coordinator.coordinator.DataUpdateCoordinator.async_shutdown",
                new_callable=AsyncMock,
            ) as base_shutdown,
        ):
            command_shutdown.side_effect = RuntimeError("command boom")
            await coordinator.async_shutdown()

        command_shutdown.assert_awaited_once()
        coordinator._runtimes.mqtt.clear_disconnect_notification.assert_awaited_once()
        coordinator._runtimes.mqtt.disconnect.assert_awaited_once()
        coordinator._state.background_task_manager.cancel_all.assert_awaited_once()
        coordinator._runtimes.mqtt.reset.assert_called_once()
        coordinator._runtimes.device.reset.assert_called_once()
        coordinator.protocol.attach_mqtt_facade.assert_called_once_with(None)
        coordinator._runtimes.mqtt.detach_transport.assert_called_once()
        base_shutdown.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_public_entrypoints_follow_current_device_state(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Coordinator public entrypoints should reflect the current device cache."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial=serial)]
        )

        await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)

        assert device is not None
        assert coordinator.get_device_by_id(serial) is device

        await coordinator.async_apply_optimistic_state(device, {"powerState": "1"})
        assert device.properties["powerState"] == "1"

        coordinator.protocol.query_ota_info = AsyncMock(return_value=[])
        await coordinator.async_query_device_ota_info(
            device,
            allow_rich_v2_fallback=False,
        )
        coordinator.protocol.query_ota_info.assert_awaited_once_with(
            device_id=serial,
            device_type=device.device_type_hex,
            iot_name=device.iot_name or None,
            allow_rich_v2_fallback=False,
        )

    @pytest.mark.asyncio
    async def test_apply_properties_update_skips_stale_pending_values(
        self, coordinator
    ):
        """Stale MQTT payloads should be filtered before state writes."""
        device = MagicMock(serial="dev1")
        coordinator._runtimes.command.filter_pending_state_properties = MagicMock(
            return_value={}
        )
        coordinator._runtimes.command.observe_state_confirmation = MagicMock()
        coordinator._runtimes.state.apply_properties_update = AsyncMock(
            return_value=True
        )

        changed = await coordinator._apply_properties_update(
            device,
            {"powerState": "0"},
            "mqtt",
        )

        assert changed is False
        coordinator._runtimes.command.filter_pending_state_properties.assert_called_once_with(
            device_serial="dev1",
            properties={"powerState": "0"},
        )
        coordinator._runtimes.command.observe_state_confirmation.assert_not_called()
        coordinator._runtimes.state.apply_properties_update.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_apply_properties_update_observes_confirmation_before_state_write(
        self, coordinator
    ):
        """Confirmed state updates should teach command latency before write-through."""
        device = MagicMock(serial="dev1")
        coordinator._runtimes.command.filter_pending_state_properties = MagicMock(
            return_value={"powerState": "1"}
        )
        coordinator._runtimes.command.observe_state_confirmation = MagicMock(
            return_value=0.5
        )
        coordinator._runtimes.state.apply_properties_update = AsyncMock(
            return_value=True
        )

        changed = await coordinator._apply_properties_update(
            device,
            {"powerState": "1"},
            "mqtt",
        )

        assert changed is True
        coordinator._runtimes.command.observe_state_confirmation.assert_called_once_with(
            device_serial="dev1",
            properties={"powerState": "1"},
        )
        coordinator._runtimes.state.apply_properties_update.assert_awaited_once_with(
            device,
            {"powerState": "1"},
            source="mqtt",
        )

    @pytest.mark.asyncio
    async def test_async_send_command_surfaces_reauth_when_auth_expires(
        self,
        coordinator,
        mock_lipro_api_client,
        patch_anonymous_share_manager,
    ):
        """Public command dispatch should surface reauth when auth expires."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_devices.return_value = make_device_page(
            [make_api_device(serial=serial)]
        )
        mock_lipro_api_client.send_command.side_effect = LiproAuthError("Auth failed")

        await refresh_and_sync_devices(coordinator)

        device = coordinator.get_device(serial)
        assert device is not None

        with pytest.raises(ConfigEntryAuthFailed, match="auth_error"):
            await coordinator.async_send_command(device, "POWER_ON")
