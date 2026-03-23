"""Debug-query init service-handler topical suites."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import CONF_DEBUG_MODE
from custom_components.lipro.control.service_router import (
    async_handle_get_city,
    async_handle_get_developer_report,
    async_handle_query_command_result,
    async_handle_query_user_cloud,
)
from custom_components.lipro.core import LiproApiError
from custom_components.lipro.core.command.result import COMMAND_RESULT_STATE_CONFIRMED
from custom_components.lipro.services.contracts import (
    ATTR_DEVICE_ID,
    ATTR_ENTRY_ID,
    ATTR_MSG_SN,
)
from homeassistant.exceptions import ServiceValidationError
from tests.helpers.service_call import service_call

from .test_init_service_handlers import _InitServiceHandlerBase


class TestInitServiceHandlerDeveloperDebug(_InitServiceHandlerBase):
    """Tests for developer/debug report and cloud query handlers."""

    async def test_get_developer_report_returns_entry_reports(self, hass) -> None:
        """get_developer_report returns exporter-backed diagnostics per config entry."""
        coordinator = self._create_runtime_coordinator()

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
        first = self._create_runtime_coordinator()
        second = self._create_runtime_coordinator()

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
        coordinator = self._create_runtime_coordinator()
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
        assert result["state"] == COMMAND_RESULT_STATE_CONFIRMED
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
            "custom_components.lipro.core.command.result_policy.asyncio.sleep",
            new=sleep_mock,
        ):
            result = await async_handle_query_command_result(
                hass,
                service_call(
                    hass,
                    {ATTR_DEVICE_ID: device.serial, ATTR_MSG_SN: "682550445474"},
                ),
            )

        assert result["state"] == COMMAND_RESULT_STATE_CONFIRMED
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
        coordinator = self._attach_auth_service(MagicMock())
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
        coordinator = self._attach_auth_service(MagicMock())
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
        coordinator = self._attach_auth_service(MagicMock())
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
        first = self._attach_auth_service(MagicMock())
        first.protocol_service.async_get_city = AsyncMock(
            side_effect=LiproApiError("temporary failure", code=500)
        )
        second = self._attach_auth_service(MagicMock())
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
        first = self._attach_auth_service(MagicMock())
        first.protocol_service.async_get_city = AsyncMock(side_effect=RuntimeError("boom"))
        second = self._attach_auth_service(MagicMock())
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
        first = self._attach_auth_service(MagicMock())
        first.protocol_service.async_query_user_cloud = AsyncMock(
            side_effect=LiproApiError("temporary failure", code=500)
        )
        second = self._attach_auth_service(MagicMock())
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
        first = self._attach_auth_service(MagicMock())
        first.protocol_service.async_query_user_cloud = AsyncMock(side_effect=RuntimeError("boom"))
        second = self._attach_auth_service(MagicMock())
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
