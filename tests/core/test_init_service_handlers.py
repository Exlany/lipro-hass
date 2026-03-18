"""Service-handler focused tests extracted from Lipro integration init coverage."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import CONF_DEBUG_MODE
from custom_components.lipro.control.service_router import (
    _get_device_and_coordinator,
    async_handle_add_schedule,
    async_handle_delete_schedules,
    async_handle_fetch_body_sensor_history,
    async_handle_fetch_door_sensor_history,
    async_handle_get_anonymous_share_report,
    async_handle_get_city,
    async_handle_get_developer_report,
    async_handle_get_schedules,
    async_handle_query_command_result,
    async_handle_query_user_cloud,
    async_handle_send_command,
    async_handle_submit_anonymous_share,
    async_handle_submit_developer_feedback,
)
from custom_components.lipro.core import LiproApiError
from custom_components.lipro.core.device import LiproDevice
from custom_components.lipro.services.contracts import (
    ATTR_COMMAND,
    ATTR_DAYS,
    ATTR_DEVICE_ID,
    ATTR_ENTRY_ID,
    ATTR_EVENTS,
    ATTR_MESH_TYPE,
    ATTR_MSG_SN,
    ATTR_PROPERTIES,
    ATTR_SCHEDULE_IDS,
    ATTR_SENSOR_DEVICE_ID,
    ATTR_TIMES,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_registry as er
from tests.helpers.service_call import service_call

_TEST_LOGGER = logging.getLogger(__name__)

class TestInitServiceHandlers:
    """Tests for __init__.py service handlers and device targeting."""

    @staticmethod
    def _create_device(serial: str = "03ab5ccd7c111111") -> LiproDevice:
        """Create a minimal LiproDevice for runtime tests."""
        return LiproDevice(
            device_number=1,
            serial=serial,
            name="Test Device",
            device_type=1,
            iot_name="lipro_led",
            physical_model="light",
        )

    @staticmethod
    def _attach_auth_service(coordinator: MagicMock) -> MagicMock:
        """Attach the formal async auth and protocol surfaces expected by services."""
        coordinator.auth_service = MagicMock(
            async_ensure_authenticated=AsyncMock(),
            async_trigger_reauth=AsyncMock(),
        )
        coordinator.protocol_service = MagicMock()
        return coordinator

    async def test_get_device_from_entity_target(self, hass) -> None:
        """Resolve target entity unique_id to device serial."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_id = (
            er.async_get(hass)
            .async_get_or_create(
                "light",
                DOMAIN,
                f"lipro_{device.serial}_light",
                suggested_object_id="lipro_test_device",
            )
            .entity_id
        )

        call = service_call(hass, {ATTR_ENTITY_ID: [entity_id]})
        got_device, got_coordinator = await _get_device_and_coordinator(hass, call)

        assert got_device is device
        assert got_coordinator is coordinator

    async def test_get_device_from_target_entity_id(self, hass) -> None:
        """Resolve device via ServiceCall.target.entity_id."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_id = (
            er.async_get(hass)
            .async_get_or_create(
                "light",
                DOMAIN,
                f"lipro_{device.serial}_light",
                suggested_object_id="lipro_target_test_device",
            )
            .entity_id
        )

        call = service_call(hass, {}, target_entity_ids=[entity_id])
        got_device, got_coordinator = await _get_device_and_coordinator(hass, call)

        assert got_device is device
        assert got_coordinator is coordinator

    async def test_get_device_from_multiple_entity_targets_same_device_resolves(
        self, hass
    ) -> None:
        """Multiple entities that map to one device should resolve successfully."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_registry = er.async_get(hass)
        entity_1 = entity_registry.async_get_or_create(
            "light",
            DOMAIN,
            f"lipro_{device.serial}_light",
            suggested_object_id="lipro_test_device_1",
        ).entity_id
        entity_2 = entity_registry.async_get_or_create(
            "switch",
            DOMAIN,
            f"lipro_{device.serial}_switch",
            suggested_object_id="lipro_test_device_2",
        ).entity_id

        got_device, got_coordinator = await _get_device_and_coordinator(
            hass,
            service_call(hass, {ATTR_ENTITY_ID: [entity_1, entity_2]}),
        )

        assert got_device is device
        assert got_coordinator is coordinator

    async def test_get_device_from_multiple_entity_targets_different_devices_raises(
        self, hass
    ) -> None:
        """Multiple entities from different devices should still be rejected."""
        first_device = self._create_device(serial="03ab5ccd7c123456")
        second_device = self._create_device(serial="03ab5ccd7c654321")
        coordinator = MagicMock()
        coordinator.get_device.side_effect = [first_device, second_device]

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_registry = er.async_get(hass)
        first_entity = entity_registry.async_get_or_create(
            "light",
            DOMAIN,
            f"lipro_{first_device.serial}_light",
            suggested_object_id="lipro_device_first",
        ).entity_id
        second_entity = entity_registry.async_get_or_create(
            "switch",
            DOMAIN,
            f"lipro_{second_device.serial}_switch",
            suggested_object_id="lipro_device_second",
        ).entity_id

        with pytest.raises(ServiceValidationError):
            await _get_device_and_coordinator(
                hass,
                service_call(hass, {ATTR_ENTITY_ID: [first_entity, second_entity]}),
            )

    async def test_get_device_falls_back_to_get_device_by_id(self, hass) -> None:
        """Fallback to coordinator alias lookup when serial lookup misses."""
        device = self._create_device(serial="mesh_group_10001")
        coordinator = MagicMock()
        coordinator.get_device.return_value = None
        coordinator.get_device_by_id.return_value = device

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        call = service_call(hass, {ATTR_DEVICE_ID: "03AB5CCD7C716177"})
        got_device, got_coordinator = await _get_device_and_coordinator(hass, call)

        assert got_device is device
        assert got_coordinator is coordinator
        coordinator.get_device.assert_called_once_with("03AB5CCD7C716177")
        coordinator.get_device_by_id.assert_called_once_with("03AB5CCD7C716177")

    async def test_get_device_without_id_or_entity_raises(self, hass) -> None:
        """Missing device_id and entity target should raise validation error."""
        with pytest.raises(ServiceValidationError):
            await _get_device_and_coordinator(hass, service_call(hass, {}))

    async def test_add_schedule_times_events_mismatch_raises(self, hass) -> None:
        """Mismatched lengths in add_schedule should fail validation."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        call = service_call(
            hass,
            {
                ATTR_DEVICE_ID: device.serial,
                ATTR_DAYS: [1, 2],
                ATTR_TIMES: [3600],
                ATTR_EVENTS: [1, 0],
            },
        )

        with pytest.raises(ServiceValidationError):
            await async_handle_add_schedule(hass, call)

    async def test_submit_anonymous_share_disabled_raises(self, hass) -> None:
        """submit_anonymous_share validates opt-in flag."""
        share_manager = MagicMock()
        share_manager.is_enabled = False

        with (
            patch(
                "custom_components.lipro.control.service_router.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            pytest.raises(ServiceValidationError),
        ):
            await async_handle_submit_anonymous_share(hass, service_call(hass, {}))

    async def test_get_anonymous_share_report_returns_data(self, hass) -> None:
        """get_anonymous_share_report exposes pending report summary."""
        report = {
            "device_count": 1,
            "error_count": 2,
            "devices": ["a"],
            "errors": ["b"],
        }
        share_manager = MagicMock()
        share_manager.get_pending_report.return_value = report

        with patch(
            "custom_components.lipro.control.service_router.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            result = await async_handle_get_anonymous_share_report(
                hass, service_call(hass, {})
            )

        assert result == {
            "has_data": True,
            "device_count": 1,
            "error_count": 2,
            "devices": ["a"],
            "errors": ["b"],
        }

    async def test_submit_anonymous_share_forwards_entry_id(self, hass) -> None:
        """submit_anonymous_share targets one scoped manager when entry_id is provided."""
        share_manager = MagicMock()
        share_manager.is_enabled = True
        share_manager.pending_count = (1, 0)
        share_manager.submit_report = AsyncMock(return_value=True)

        with patch(
            "custom_components.lipro.control.service_router.get_anonymous_share_manager",
            return_value=share_manager,
        ) as get_share_manager:
            result = await async_handle_submit_anonymous_share(
                hass,
                service_call(hass, {ATTR_ENTRY_ID: "entry-2"}),
            )

        get_share_manager.assert_called_once_with(hass, entry_id="entry-2")
        assert result == {
            "success": True,
            "devices": 1,
            "errors": 0,
            "requested_entry_id": "entry-2",
        }

    async def test_get_anonymous_share_report_forwards_entry_id(self, hass) -> None:
        """get_anonymous_share_report targets one scoped manager when entry_id is provided."""
        share_manager = MagicMock()
        share_manager.get_pending_report.return_value = {
            "device_count": 1,
            "error_count": 0,
            "devices": ["a"],
            "errors": [],
        }

        with patch(
            "custom_components.lipro.control.service_router.get_anonymous_share_manager",
            return_value=share_manager,
        ) as get_share_manager:
            result = await async_handle_get_anonymous_share_report(
                hass,
                service_call(hass, {ATTR_ENTRY_ID: "entry-3"}),
            )

        get_share_manager.assert_called_once_with(hass, entry_id="entry-3")
        assert result == {
            "has_data": True,
            "device_count": 1,
            "error_count": 0,
            "devices": ["a"],
            "errors": [],
            "requested_entry_id": "entry-3",
        }

    async def test_get_developer_report_returns_entry_reports(self, hass) -> None:
        """get_developer_report returns exporter-backed diagnostics per config entry."""
        coordinator = MagicMock()

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with patch(
            "custom_components.lipro.control.telemetry_surface.get_entry_telemetry_view",
            return_value={"debug_mode": True},
        ):
            result = await async_handle_get_developer_report(hass, service_call(hass, {}))

        assert result == {
            "entry_count": 1,
            "reports": [{"debug_mode": True}],
        }

    async def test_get_developer_report_filters_by_entry_id(self, hass) -> None:
        """get_developer_report scopes diagnostics to one requested config entry."""
        first = MagicMock()
        second = MagicMock()

        entry_1 = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry_1.add_to_hass(hass)
        entry_1.runtime_data = first

        entry_2 = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry_2.add_to_hass(hass)
        entry_2.runtime_data = second

        def _telemetry_view(entry, sink):
            assert sink == "developer"
            return {"debug_mode": entry.entry_id == entry_1.entry_id}

        with patch(
            "custom_components.lipro.control.telemetry_surface.get_entry_telemetry_view",
            side_effect=lambda entry, sink: {"debug_mode": entry.entry_id == entry_1.entry_id},
        ):
            result = await async_handle_get_developer_report(
                hass,
                service_call(hass, {ATTR_ENTRY_ID: entry_2.entry_id}),
            )

        assert result == {
            "entry_count": 1,
            "reports": [{"debug_mode": False}],
            "requested_entry_id": entry_2.entry_id,
        }

    async def test_get_developer_report_rejects_non_debug_entry(self, hass) -> None:
        """Scoped developer report should reject entries without debug opt-in."""
        coordinator = MagicMock()
        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(ServiceValidationError):
            await async_handle_get_developer_report(
                hass,
                service_call(hass, {ATTR_ENTRY_ID: entry.entry_id}),
            )

    async def test_get_developer_report_skips_broken_entry(self, hass) -> None:
        """get_developer_report should skip one broken exporter lookup."""
        broken = MagicMock()
        healthy = MagicMock()

        entry_1 = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry_1.add_to_hass(hass)
        entry_1.runtime_data = broken

        entry_2 = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry_2.add_to_hass(hass)
        entry_2.runtime_data = healthy

        with patch(
            "custom_components.lipro.control.telemetry_surface.get_entry_telemetry_view",
            side_effect=[RuntimeError("boom"), {"debug_mode": False}],
        ):
            result = await async_handle_get_developer_report(hass, service_call(hass, {}))

        assert result == {
            "entry_count": 1,
            "reports": [{"debug_mode": False}],
        }

    async def test_query_command_result_service(self, hass) -> None:
        """query_command_result service should return one confirmed diagnostic result."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol_service.async_query_command_result = AsyncMock(
            return_value={"success": True}
        )

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_query_command_result(
            hass,
            service_call(
                hass,
                {ATTR_DEVICE_ID: device.serial, ATTR_MSG_SN: "682550445474"},
            ),
        )

        assert result["serial"] == "mesh_group_49155"
        assert result["msg_sn"] == "682550445474"
        assert result["max_attempts"] == 6
        assert result["time_budget_seconds"] == 3.0
        assert result["state"] == "confirmed"
        assert result["attempts"] == 1
        assert result["attempt_limit"] == 5
        assert result["retry_delays_seconds"] == pytest.approx((0.35, 0.7, 1.4, 0.55))
        assert result["result"] == {"success": True}
        coordinator.protocol_service.async_query_command_result.assert_awaited_once_with(
            msg_sn="682550445474",
            device_id="mesh_group_49155",
            device_type=device.device_type_hex,
        )

    async def test_query_command_result_service_requires_debug_mode(self, hass) -> None:
        """query_command_result should reject entries without debug opt-in."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol_service.async_query_command_result = AsyncMock(
            return_value={"success": True}
        )

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(ServiceValidationError):
            await async_handle_query_command_result(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_MSG_SN: "682550445474"},
                ),
            )

        coordinator.protocol_service.async_query_command_result.assert_not_awaited()

    async def test_query_command_result_service_polls_until_confirmed(
        self, hass
    ) -> None:
        """query_command_result service should keep polling pending states within budget."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol_service.async_query_command_result = AsyncMock(
            side_effect=[
                {"code": "140006", "message": "设备未响应", "success": False},
                {"code": "100000", "message": "服务异常", "success": False},
                {"code": "0000", "message": "success", "success": True},
            ]
        )

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        sleep_mock = AsyncMock()
        with patch(
            "custom_components.lipro.core.command.result.asyncio.sleep",
            new=sleep_mock,
        ):
            result = await async_handle_query_command_result(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_MSG_SN: "682550445474"},
                ),
            )

        assert result["state"] == "confirmed"
        assert result["attempts"] == 3
        assert result["attempt_limit"] == 5
        assert result["result"] == {
            "code": "0000",
            "message": "success",
            "success": True,
        }
        assert result["retry_delays_seconds"] == pytest.approx((0.35, 0.7, 1.4, 0.55))
        assert sleep_mock.await_args_list == [call(0.35), call(0.7)]
        assert coordinator.protocol_service.async_query_command_result.await_count == 3

    async def test_get_city_service(self, hass) -> None:
        """get_city service should return first coordinator city result."""
        coordinator = MagicMock()
        coordinator.protocol_service.async_get_city = AsyncMock(
            return_value={"province": "广东省", "city": "江门市"}
        )

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_get_city(hass, service_call(hass, {}))
        assert result == {"result": {"province": "广东省", "city": "江门市"}}

    async def test_get_city_service_returns_empty_without_debug_mode(
        self, hass
    ) -> None:
        """get_city should ignore non-debug runtime entries when filtering coordinators."""
        coordinator = MagicMock()
        coordinator.protocol_service.async_get_city = AsyncMock(
            return_value={"province": "广东省", "city": "江门市"}
        )

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_get_city(hass, service_call(hass, {}))

        assert result == {"result": {}}
        coordinator.protocol_service.async_get_city.assert_not_awaited()

    async def test_query_user_cloud_service(self, hass) -> None:
        """query_user_cloud service should return first coordinator result."""
        coordinator = MagicMock()
        coordinator.protocol_service.async_query_user_cloud = AsyncMock(return_value={"data": []})

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_query_user_cloud(hass, service_call(hass, {}))
        assert result == {"result": {"data": []}}

    async def test_get_city_service_falls_back_to_next_coordinator(self, hass) -> None:
        """get_city should continue to next coordinator when one fails."""
        first = MagicMock()
        first.protocol_service.async_get_city = AsyncMock(
            side_effect=LiproApiError("temporary failure", code=500)
        )
        second = MagicMock()
        second.protocol_service.async_get_city = AsyncMock(
            return_value={"province": "广东省", "city": "深圳市"}
        )

        entry_1 = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry_1.add_to_hass(hass)
        entry_1.runtime_data = first

        entry_2 = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry_2.add_to_hass(hass)
        entry_2.runtime_data = second

        result = await async_handle_get_city(hass, service_call(hass, {}))
        assert result == {"result": {"province": "广东省", "city": "深圳市"}}

    async def test_get_city_service_skips_unexpected_error(self, hass) -> None:
        """get_city should skip unexpected coordinator errors and continue."""
        first = MagicMock()
        first.protocol_service.async_get_city = AsyncMock(side_effect=RuntimeError("boom"))
        second = MagicMock()
        second.protocol_service.async_get_city = AsyncMock(
            return_value={"province": "浙江省", "city": "杭州市"}
        )

        entry_1 = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry_1.add_to_hass(hass)
        entry_1.runtime_data = first

        entry_2 = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry_2.add_to_hass(hass)
        entry_2.runtime_data = second

        result = await async_handle_get_city(hass, service_call(hass, {}))
        assert result == {"result": {"province": "浙江省", "city": "杭州市"}}

    async def test_query_user_cloud_service_falls_back_to_next_coordinator(
        self, hass
    ) -> None:
        """query_user_cloud should continue to next coordinator when one fails."""
        first = MagicMock()
        first.protocol_service.async_query_user_cloud = AsyncMock(
            side_effect=LiproApiError("temporary failure", code=500)
        )
        second = MagicMock()
        second.protocol_service.async_query_user_cloud = AsyncMock(return_value={"data": [1, 2]})

        entry_1 = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry_1.add_to_hass(hass)
        entry_1.runtime_data = first

        entry_2 = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry_2.add_to_hass(hass)
        entry_2.runtime_data = second

        result = await async_handle_query_user_cloud(hass, service_call(hass, {}))
        assert result == {"result": {"data": [1, 2]}}

    async def test_query_user_cloud_service_skips_unexpected_error(self, hass) -> None:
        """query_user_cloud should skip unexpected coordinator errors and continue."""
        first = MagicMock()
        first.protocol_service.async_query_user_cloud = AsyncMock(side_effect=RuntimeError("boom"))
        second = MagicMock()
        second.protocol_service.async_query_user_cloud = AsyncMock(return_value={"data": []})

        entry_1 = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry_1.add_to_hass(hass)
        entry_1.runtime_data = first

        entry_2 = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry_2.add_to_hass(hass)
        entry_2.runtime_data = second

        result = await async_handle_query_user_cloud(hass, service_call(hass, {}))
        assert result == {"result": {"data": []}}

    async def test_fetch_body_sensor_history_service(self, hass) -> None:
        """fetch_body_sensor_history should pass sensor payload to client."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol_service.async_fetch_body_sensor_history = AsyncMock(
            return_value={"humanSensorStateList": []}
        )

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_fetch_body_sensor_history(
            hass,
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_SENSOR_DEVICE_ID: "03ab5ccd7c7167d8",
                    ATTR_MESH_TYPE: "2",
                },
            ),
        )

        assert result["serial"] == "mesh_group_49155"
        coordinator.protocol_service.async_fetch_body_sensor_history.assert_awaited_once_with(
            device_id="mesh_group_49155",
            device_type=device.device_type,
            sensor_device_id="03ab5ccd7c7167d8",
            mesh_type="2",
        )

    async def test_fetch_body_sensor_history_service_requires_debug_mode(
        self, hass
    ) -> None:
        """fetch_body_sensor_history should reject entries without debug opt-in."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol_service.async_fetch_body_sensor_history = AsyncMock(
            return_value={"humanSensorStateList": []}
        )

        entry = MockConfigEntry(domain=DOMAIN, data={"phone": "13800000000"})
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(ServiceValidationError):
            await async_handle_fetch_body_sensor_history(
                hass,
                service_call(
                    hass,
                    {
                        ATTR_DEVICE_ID: device.serial,
                        ATTR_SENSOR_DEVICE_ID: "03ab5ccd7c7167d8",
                        ATTR_MESH_TYPE: "2",
                    },
                ),
            )

        coordinator.protocol_service.async_fetch_body_sensor_history.assert_not_awaited()

    async def test_fetch_door_sensor_history_service(self, hass) -> None:
        """fetch_door_sensor_history should pass sensor payload to client."""
        device = self._create_device(serial="mesh_group_49155")
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol_service.async_fetch_door_sensor_history = AsyncMock(
            return_value={"doorStateList": []}
        )

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_fetch_door_sensor_history(
            hass,
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_SENSOR_DEVICE_ID: "03ab5ccd7c7167d8",
                    ATTR_MESH_TYPE: "2",
                },
            ),
        )

        assert result["serial"] == "mesh_group_49155"
        coordinator.protocol_service.async_fetch_door_sensor_history.assert_awaited_once_with(
            device_id="mesh_group_49155",
            device_type=device.device_type,
            sensor_device_id="03ab5ccd7c7167d8",
            mesh_type="2",
        )

    async def test_submit_developer_feedback_success(self, hass) -> None:
        """submit_developer_feedback uploads one scoped report when entry_id is provided."""
        coordinator = MagicMock()

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        share_manager = MagicMock()
        share_manager.submit_developer_feedback = AsyncMock(return_value=True)

        with (
            patch(
                "custom_components.lipro.control.service_router.get_anonymous_share_manager",
                return_value=share_manager,
            ) as get_share_manager,
            patch(
                "custom_components.lipro.control.service_router.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.control.telemetry_surface.get_entry_telemetry_view",
                return_value={"runtime": {"ok": True}},
            ),
        ):
            result = await async_handle_submit_developer_feedback(
                hass,
                service_call(
                    hass,
                    {ATTR_ENTRY_ID: entry.entry_id, "note": "manual validation run"},
                ),
            )

        assert result == {
            "success": True,
            "submitted_entries": 1,
            "requested_entry_id": entry.entry_id,
        }
        get_share_manager.assert_called_once_with(hass, entry_id=entry.entry_id)
        share_manager.submit_developer_feedback.assert_awaited_once()

    async def test_submit_developer_feedback_failure_raises(self, hass) -> None:
        """submit_developer_feedback raises when upload fails."""
        coordinator = MagicMock()

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        share_manager = MagicMock()
        share_manager.submit_developer_feedback = AsyncMock(return_value=False)

        with (
            patch(
                "custom_components.lipro.control.service_router.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            patch(
                "custom_components.lipro.control.service_router.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.control.telemetry_surface.get_entry_telemetry_view",
                return_value={"runtime": {"ok": True}},
            ),
            pytest.raises(HomeAssistantError),
        ):
            await async_handle_submit_developer_feedback(hass, service_call(hass, {}))

    async def test_send_command_handler_success(self, hass) -> None:
        """send_command returns success payload on coordinator success."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(return_value=True)
        coordinator.command_service = command_service

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_send_command(
            hass,
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_COMMAND: "POWER_ON",
                    ATTR_PROPERTIES: [{"key": "powerState", "value": "1"}],
                },
            ),
        )
        assert result == {"success": True, "serial": device.serial}
        command_service.async_send_command.assert_awaited_once_with(
            device,
            "POWER_ON",
            [{"key": "powerState", "value": "1"}],
            fallback_device_id=device.serial,
        )

    async def test_send_command_handler_alias_resolution_metadata(self, hass) -> None:
        """send_command response includes alias-resolution metadata when remapped."""
        requested_id = "03ab0000000000f1"
        group_device = self._create_device(serial="mesh_group_10001")
        group_device.is_group = True

        coordinator = MagicMock()
        coordinator.get_device.return_value = None
        coordinator.get_device_by_id.return_value = group_device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(return_value=True)
        coordinator.command_service = command_service

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_send_command(
            hass,
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: requested_id,
                    ATTR_COMMAND: "POWER_ON",
                },
            ),
        )

        assert result == {
            "success": True,
            "serial": "mesh_group_10001",
            "requested_device_id": requested_id,
            "resolved_device_id": "mesh_group_10001",
        }
        coordinator.get_device.assert_called_once_with(requested_id)
        coordinator.get_device_by_id.assert_called_once_with(requested_id)
        command_service.async_send_command.assert_awaited_once_with(
            group_device,
            "POWER_ON",
            None,
            fallback_device_id=requested_id,
        )

    async def test_send_command_handler_failure_raises(self, hass) -> None:
        """send_command raises HomeAssistantError when coordinator reports failure."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(return_value=False)
        coordinator.command_service = command_service
        command_service.last_failure = None

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError):
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )

    async def test_send_command_handler_push_failed_maps_translation(
        self, hass
    ) -> None:
        """pushSuccess=false style failures should use push_failed translation key."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(return_value=False)
        coordinator.command_service = command_service
        command_service.last_failure = {
            "reason": "push_failed",
            "code": "push_failed",
        }

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )
        assert exc.value.translation_key == "command_push_failed"

    async def test_send_command_handler_offline_code_maps_translation(
        self, hass
    ) -> None:
        """140004 failures should use device-not-connected translation key."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(return_value=False)
        coordinator.command_service = command_service
        command_service.last_failure = {"reason": "api_error", "code": "140004"}

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )
        assert exc.value.translation_key == "command_device_not_connected"

    async def test_send_command_handler_busy_code_maps_translation(self, hass) -> None:
        """250001 failures should use device-busy translation key."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(return_value=False)
        coordinator.command_service = command_service
        command_service.last_failure = {"reason": "api_error", "code": "250001"}

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )
        assert exc.value.translation_key == "command_device_busy"

    async def test_send_command_handler_api_error_raises(self, hass) -> None:
        """send_command maps API errors to HomeAssistantError."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(
            side_effect=LiproApiError("boom")
        )
        coordinator.command_service = command_service

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError):
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )

    async def test_send_command_handler_api_error_code_maps_translation(
        self, hass
    ) -> None:
        """API error 140003 should map to device-offline translation key."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(
            side_effect=LiproApiError("offline", "140003")
        )
        coordinator.command_service = command_service

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )
        assert exc.value.translation_key == "command_device_offline"

    async def test_send_command_handler_api_busy_error_maps_translation(
        self, hass
    ) -> None:
        """API error 250001 should map to device-busy translation key."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(
            side_effect=LiproApiError("busy", "250001")
        )
        coordinator.command_service = command_service

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )
        assert exc.value.translation_key == "command_device_busy"

    async def test_send_command_handler_not_found_code_maps_offline_translation(
        self, hass
    ) -> None:
        """API error 140013 should map to device-offline translation key."""
        device = self._create_device()
        coordinator = MagicMock()
        coordinator.get_device.return_value = device
        command_service = MagicMock()
        command_service.async_send_command = AsyncMock(
            side_effect=LiproApiError("not found", "140013")
        )
        coordinator.command_service = command_service

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        with pytest.raises(HomeAssistantError) as exc:
            await async_handle_send_command(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_COMMAND: "POWER_ON"},
                ),
            )
        assert exc.value.translation_key == "command_device_offline"

    async def test_get_schedules_formats_response(self, hass) -> None:
        """get_schedules returns normalized response payload."""
        device = self._create_device()
        client = MagicMock()
        client.get_device_schedules = AsyncMock(
            return_value=[
                {
                    "id": 5,
                    "active": True,
                    "schedule": {"days": [1], "time": [3600, 3661], "evt": [1, 0]},
                }
            ]
        )
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_get_schedules(
            hass, service_call(hass, {ATTR_DEVICE_ID: device.serial})
        )

        assert result == {
            "serial": device.serial,
            "schedules": [
                {
                    "id": 5,
                    "active": True,
                    "days": [1],
                    "times": ["01:00", "01:01"],
                    "events": [1, 0],
                }
            ],
        }

    async def test_get_schedules_resolves_device_from_entity_target(self, hass) -> None:
        """get_schedules should resolve target entity when device_id is omitted."""
        device = self._create_device()
        client = MagicMock()
        client.get_device_schedules = AsyncMock(return_value=[])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_id = (
            er.async_get(hass)
            .async_get_or_create(
                "light",
                DOMAIN,
                f"lipro_{device.serial}_light",
                suggested_object_id="lipro_test_device",
            )
            .entity_id
        )

        result = await async_handle_get_schedules(
            hass, service_call(hass, {ATTR_ENTITY_ID: entity_id})
        )

        assert result == {"serial": device.serial, "schedules": []}
        coordinator.get_device.assert_called_once_with(device.serial)
        client.get_device_schedules.assert_awaited_once_with(
            device.iot_device_id,
            device.device_type_hex,
            mesh_gateway_id="",
            mesh_member_ids=[],
        )

    async def test_get_schedules_ignores_malformed_schedule_rows(self, hass) -> None:
        """Malformed schedule rows should be ignored instead of raising."""
        device = self._create_device()
        client = MagicMock()
        client.get_device_schedules = AsyncMock(
            return_value=[
                "invalid-row",
                {
                    "id": 9,
                    "active": True,
                    "schedule": {
                        "days": ["1", "x"],
                        "time": [3600, -1, 90000, "bad"],
                        "evt": [1, "0", "bad"],
                    },
                },
            ]
        )
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_get_schedules(
            hass, service_call(hass, {ATTR_DEVICE_ID: device.serial})
        )

        assert result == {
            "serial": device.serial,
            "schedules": [
                {
                    "id": 9,
                    "active": True,
                    "days": [1],
                    "times": ["01:00"],
                    "events": [1],
                }
            ],
        }

    async def test_get_schedules_passes_mesh_context(self, hass) -> None:
        """get_schedules should pass mesh gateway/member context to client."""
        device = self._create_device(serial="mesh_group_10001")
        device.extra_data["gateway_device_id"] = "03ab0000000000a1"
        device.extra_data["group_member_ids"] = ["03ab0000000000a2"]

        client = MagicMock()
        client.get_device_schedules = AsyncMock(return_value=[])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        await async_handle_get_schedules(
            hass, service_call(hass, {ATTR_DEVICE_ID: device.serial})
        )

        client.get_device_schedules.assert_awaited_once_with(
            device.iot_device_id,
            device.device_type_hex,
            mesh_gateway_id="03ab0000000000a1",
            mesh_member_ids=["03ab0000000000a2"],
        )

    async def test_add_schedule_passes_mesh_context(self, hass) -> None:
        """add_schedule should pass mesh gateway/member context to client."""
        device = self._create_device(serial="mesh_group_10001")
        device.extra_data["gateway_device_id"] = "03ab0000000000a1"
        device.extra_data["group_member_ids"] = ["03ab0000000000a2"]

        client = MagicMock()
        client.add_device_schedule = AsyncMock(return_value=[{"id": 1}])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_add_schedule(
            hass,
            service_call(
                hass,
                {
                    ATTR_DEVICE_ID: device.serial,
                    ATTR_DAYS: [1, 2, 3],
                    ATTR_TIMES: [3600],
                    ATTR_EVENTS: [0],
                },
            ),
        )

        assert result["schedule_count"] == 1
        client.add_device_schedule.assert_awaited_once_with(
            device.iot_device_id,
            device.device_type_hex,
            [1, 2, 3],
            [3600],
            [0],
            mesh_gateway_id="03ab0000000000a1",
            mesh_member_ids=["03ab0000000000a2"],
        )

    async def test_add_schedule_resolves_device_from_entity_target(self, hass) -> None:
        """add_schedule should resolve target entity when device_id is omitted."""
        device = self._create_device()
        client = MagicMock()
        client.add_device_schedule = AsyncMock(return_value=[{"id": 1}])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_id = (
            er.async_get(hass)
            .async_get_or_create(
                "light",
                DOMAIN,
                f"lipro_{device.serial}_light",
                suggested_object_id="lipro_test_device",
            )
            .entity_id
        )

        result = await async_handle_add_schedule(
            hass,
            service_call(
                hass,
                {
                    ATTR_ENTITY_ID: [entity_id],
                    ATTR_DAYS: [1],
                    ATTR_TIMES: [3600],
                    ATTR_EVENTS: [1],
                },
            ),
        )

        assert result == {
            "success": True,
            "serial": device.serial,
            "schedule_count": 1,
        }
        coordinator.get_device.assert_called_once_with(device.serial)
        client.add_device_schedule.assert_awaited_once_with(
            device.iot_device_id,
            device.device_type_hex,
            [1],
            [3600],
            [1],
            mesh_gateway_id="",
            mesh_member_ids=[],
        )

    async def test_delete_schedules_returns_summary(self, hass) -> None:
        """delete_schedules returns remaining count on success."""
        device = self._create_device()
        client = MagicMock()
        client.delete_device_schedules = AsyncMock(return_value=[{"id": 2}, {"id": 3}])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        result = await async_handle_delete_schedules(
            hass,
            service_call(
                hass,
                {ATTR_DEVICE_ID: device.serial, ATTR_SCHEDULE_IDS: [1]},
            ),
        )
        assert result == {
            "success": True,
            "serial": device.serial,
            "remaining_count": 2,
        }

    async def test_delete_schedules_passes_mesh_context(self, hass) -> None:
        """delete_schedules should pass mesh gateway/member context to client."""
        device = self._create_device(serial="mesh_group_10001")
        device.extra_data["gateway_device_id"] = "03ab0000000000a1"
        device.extra_data["group_member_ids"] = ["03ab0000000000a2"]

        client = MagicMock()
        client.delete_device_schedules = AsyncMock(return_value=[])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        await async_handle_delete_schedules(
            hass,
            service_call(
                hass,
                {ATTR_DEVICE_ID: device.serial, ATTR_SCHEDULE_IDS: [1, 2]},
            ),
        )

        client.delete_device_schedules.assert_awaited_once_with(
            device.iot_device_id,
            device.device_type_hex,
            [1, 2],
            mesh_gateway_id="03ab0000000000a1",
            mesh_member_ids=["03ab0000000000a2"],
        )

    async def test_delete_schedules_resolves_device_from_entity_target(
        self, hass
    ) -> None:
        """delete_schedules should resolve target entity when device_id is omitted."""
        device = self._create_device()
        client = MagicMock()
        client.delete_device_schedules = AsyncMock(return_value=[])
        coordinator = self._attach_auth_service(MagicMock())
        coordinator.get_device.return_value = device
        coordinator.protocol = client
        coordinator.protocol_service.async_get_device_schedules = client.get_device_schedules
        coordinator.protocol_service.async_add_device_schedule = client.add_device_schedule
        coordinator.protocol_service.async_delete_device_schedules = client.delete_device_schedules

        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = coordinator

        entity_id = (
            er.async_get(hass)
            .async_get_or_create(
                "light",
                DOMAIN,
                f"lipro_{device.serial}_light",
                suggested_object_id="lipro_test_device",
            )
            .entity_id
        )

        result = await async_handle_delete_schedules(
            hass,
            service_call(
                hass,
                {ATTR_ENTITY_ID: entity_id, ATTR_SCHEDULE_IDS: [1, 2]},
            ),
        )

        assert result == {
            "success": True,
            "serial": device.serial,
            "remaining_count": 0,
        }
        coordinator.get_device.assert_called_once_with(device.serial)
        client.delete_device_schedules.assert_awaited_once_with(
            device.iot_device_id,
            device.device_type_hex,
            [1, 2],
            mesh_gateway_id="",
            mesh_member_ids=[],
        )

    async def test_submit_anonymous_share_no_data_returns_noop(self, hass) -> None:
        """submit_anonymous_share returns no-op when nothing pending."""
        share_manager = MagicMock()
        share_manager.is_enabled = True
        share_manager.pending_count = (0, 0)

        with patch(
            "custom_components.lipro.control.service_router.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            result = await async_handle_submit_anonymous_share(
                hass, service_call(hass, {})
            )

        assert result == {
            "success": True,
            "message": "No data to submit",
            "devices": 0,
            "errors": 0,
        }

    async def test_submit_anonymous_share_submit_failed_raises(self, hass) -> None:
        """submit_anonymous_share raises when upload fails."""
        share_manager = MagicMock()
        share_manager.is_enabled = True
        share_manager.pending_count = (1, 1)
        share_manager.submit_report = AsyncMock(return_value=False)

        with (
            patch(
                "custom_components.lipro.control.service_router.get_anonymous_share_manager",
                return_value=share_manager,
            ),
            pytest.raises(HomeAssistantError),
        ):
            await async_handle_submit_anonymous_share(hass, service_call(hass, {}))

    async def test_get_anonymous_share_report_returns_empty(self, hass) -> None:
        """get_anonymous_share_report returns empty payload when no report."""
        share_manager = MagicMock()
        share_manager.get_pending_report.return_value = None

        with patch(
            "custom_components.lipro.control.service_router.get_anonymous_share_manager",
            return_value=share_manager,
        ):
            result = await async_handle_get_anonymous_share_report(
                hass, service_call(hass, {})
            )

        assert result == {"has_data": False, "devices": [], "errors": []}
