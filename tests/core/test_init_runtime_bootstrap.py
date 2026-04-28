"""Bootstrap/infrastructure init runtime topical suites."""

from __future__ import annotations

from custom_components.lipro import async_setup
from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.services.contracts import (
    SERVICE_ADD_SCHEDULE,
    SERVICE_DELETE_SCHEDULES,
    SERVICE_FETCH_BODY_SENSOR_HISTORY,
    SERVICE_FETCH_DOOR_SENSOR_HISTORY,
    SERVICE_GET_ANONYMOUS_SHARE_REPORT,
    SERVICE_GET_CITY,
    SERVICE_GET_DEVELOPER_REPORT,
    SERVICE_GET_SCHEDULES,
    SERVICE_QUERY_COMMAND_RESULT,
    SERVICE_QUERY_USER_CLOUD,
    SERVICE_REFRESH_DEVICES,
    SERVICE_SEND_COMMAND,
    SERVICE_SUBMIT_ANONYMOUS_SHARE,
    SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
)

from .test_init_runtime_behavior import _InitRuntimeBehaviorBase


class TestInitRuntimeInfrastructure(_InitRuntimeBehaviorBase):
    """Tests for init-time shared infrastructure contracts."""

    async def test_async_setup_registers_services(self, hass) -> None:
        """Services are registered by async_setup and idempotent."""
        assert await async_setup(hass, {}) is True
        assert hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND)
        assert hass.services.has_service(DOMAIN, SERVICE_GET_SCHEDULES)
        assert hass.services.has_service(DOMAIN, SERVICE_ADD_SCHEDULE)
        assert hass.services.has_service(DOMAIN, SERVICE_DELETE_SCHEDULES)
        assert hass.services.has_service(DOMAIN, SERVICE_SUBMIT_ANONYMOUS_SHARE)
        assert hass.services.has_service(DOMAIN, SERVICE_GET_ANONYMOUS_SHARE_REPORT)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_DEVELOPER_REPORT)
        assert not hass.services.has_service(DOMAIN, SERVICE_SUBMIT_DEVELOPER_FEEDBACK)
        assert not hass.services.has_service(DOMAIN, SERVICE_QUERY_COMMAND_RESULT)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_CITY)
        assert not hass.services.has_service(DOMAIN, SERVICE_QUERY_USER_CLOUD)
        assert not hass.services.has_service(DOMAIN, SERVICE_FETCH_BODY_SENSOR_HISTORY)
        assert not hass.services.has_service(DOMAIN, SERVICE_FETCH_DOOR_SENSOR_HISTORY)
        assert hass.services.has_service(DOMAIN, SERVICE_REFRESH_DEVICES)

        assert await async_setup(hass, {}) is True
        assert hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND)
