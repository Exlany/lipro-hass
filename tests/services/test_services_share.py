"""Tests for anonymous-share service handlers."""

from __future__ import annotations

from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.services.share import async_handle_submit_anonymous_share
from homeassistant.core import HomeAssistant
from tests.helpers.service_call import service_call


@pytest.mark.asyncio
async def test_async_handle_submit_anonymous_share_success_returns_counts() -> None:
    hass = cast(HomeAssistant, MagicMock())

    share_manager = MagicMock()
    share_manager.is_enabled = True
    share_manager.pending_count = (2, 1)
    share_manager.submit_report = AsyncMock(return_value=True)

    result = await async_handle_submit_anonymous_share(
        hass,
        service_call(hass, {}),
        get_anonymous_share_manager=MagicMock(return_value=share_manager),
        get_client_session=MagicMock(return_value=object()),
        raise_service_error=MagicMock(),
        domain="lipro",
    )

    assert result == {
        "success": True,
        "devices": 2,
        "errors": 1,
    }
