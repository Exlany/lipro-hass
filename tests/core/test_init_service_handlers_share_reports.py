"""Anonymous-share init service-handler topical suites."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro.control.service_router import (
    async_handle_get_anonymous_share_report,
    async_handle_submit_anonymous_share,
)
from custom_components.lipro.services.contracts import ATTR_ENTRY_ID
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from tests.helpers.service_call import service_call

from .test_init_service_handlers import _InitServiceHandlerBase


class TestInitServiceHandlerAnonymousShare(_InitServiceHandlerBase):
    """Tests for anonymous-share service flows."""

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

class TestInitServiceHandlerAnonymousShareEdges(_InitServiceHandlerBase):
    """Tests for anonymous-share edge contracts."""

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
