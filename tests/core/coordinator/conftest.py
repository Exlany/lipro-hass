"""Shared coordinator fixtures for topicized coordinator tests."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from tests.conftest_shared import mock_anonymous_share_manager

_CONFIG_ENTRY_DATA = {
    "phone": "13800000000",
    "password_hash": "e10adc3949ba59abbe56e057f20f883e",
    "phone_id": "test-phone-id",
    "access_token": "test_token",
    "refresh_token": "test_refresh",
    "user_id": 10001,
}


@pytest.fixture
def coordinator(hass, mock_lipro_api_client, mock_auth_manager):
    """Create coordinator with mocked dependencies."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=_CONFIG_ENTRY_DATA,
        options={},
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
    ) as mock_share:
        mock_share.return_value = mock_anonymous_share_manager()
        from custom_components.lipro.core.coordinator import Coordinator

        return Coordinator(hass, mock_lipro_api_client, mock_auth_manager, entry)


@pytest.fixture
def patch_anonymous_share_manager() -> Generator[MagicMock]:
    """Patch the anonymous share manager for coordinator runtime tests."""
    share_manager = mock_anonymous_share_manager()
    with patch(
        "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager",
        return_value=share_manager,
    ):
        yield share_manager
