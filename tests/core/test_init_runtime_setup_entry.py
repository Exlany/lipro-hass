"""Setup-entry init runtime topical suites."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro import async_setup_entry
from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import (
    CONF_ACCESS_TOKEN,
    CONF_DEBUG_MODE,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REFRESH_TOKEN,
)
from custom_components.lipro.core import (
    AuthSessionSnapshot,
    LiproAuthManager,
    LiproProtocolFacade,
)
from custom_components.lipro.entry_auth import (
    build_entry_auth_context,
    persist_entry_tokens_if_changed,
)
from custom_components.lipro.runtime_infra import (
    async_ensure_runtime_infra,
    remove_device_registry_listener,
    setup_device_registry_listener,
)
from custom_components.lipro.services.contracts import (
    SERVICE_FETCH_BODY_SENSOR_HISTORY,
    SERVICE_FETCH_DOOR_SENSOR_HISTORY,
    SERVICE_GET_CITY,
    SERVICE_GET_DEVELOPER_REPORT,
    SERVICE_QUERY_COMMAND_RESULT,
    SERVICE_QUERY_USER_CLOUD,
    SERVICE_SUBMIT_DEVELOPER_FEEDBACK,
)
from homeassistant.exceptions import ConfigEntryAuthFailed

from .test_init_runtime_behavior import _InitRuntimeBehaviorBase

_TEST_LOGGER = logging.getLogger(__name__)


class TestInitSetupEntryBehavior(_InitRuntimeBehaviorBase):
    async def test_async_setup_entry_success_with_token_update(self, hass) -> None:
        """async_setup_entry builds coordinator and updates stored tokens when changed."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
                CONF_PASSWORD_HASH: "hashed-password",
                CONF_ACCESS_TOKEN: "old_access",
                CONF_REFRESH_TOKEN: "old_refresh",
            },
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.add_update_listener = MagicMock(return_value=MagicMock())
        entry.async_on_unload = MagicMock()

        mock_auth = MagicMock()
        mock_auth.set_tokens = MagicMock()
        mock_auth.set_credentials = MagicMock()
        mock_auth.ensure_valid_token = AsyncMock()
        mock_auth.get_auth_session.return_value = AuthSessionSnapshot(
            access_token="new_access",
            refresh_token="new_refresh",
            user_id=None,
            expires_at=1234567890,
            phone_id="phone-id",
            biz_id=None,
        )

        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()
        mock_coordinator.config_entry = entry

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.LiproProtocolFacade", return_value=MagicMock()
            ),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch(
                "custom_components.lipro.Coordinator",
                return_value=mock_coordinator,
            ),
            patch.object(
                hass.config_entries,
                "async_forward_entry_setups",
                AsyncMock(return_value=True),
            ) as mock_forward,
            patch.object(hass.config_entries, "async_update_entry") as mock_update,
        ):
            assert await async_setup_entry(hass, entry) is True

        mock_auth.set_tokens.assert_called_once()
        mock_auth.ensure_valid_token.assert_awaited_once()
        mock_coordinator.async_config_entry_first_refresh.assert_awaited_once()
        assert entry.runtime_data is mock_coordinator
        mock_forward.assert_awaited_once()
        mock_update.assert_called_once()
        entry.add_update_listener.assert_called_once()
        entry.async_on_unload.assert_called_once()
        assert hass.services.has_service(DOMAIN, SERVICE_GET_DEVELOPER_REPORT)
        assert hass.services.has_service(DOMAIN, SERVICE_SUBMIT_DEVELOPER_FEEDBACK)
        assert hass.services.has_service(DOMAIN, SERVICE_QUERY_COMMAND_RESULT)
        assert hass.services.has_service(DOMAIN, SERVICE_GET_CITY)
        assert hass.services.has_service(DOMAIN, SERVICE_QUERY_USER_CLOUD)
        assert hass.services.has_service(DOMAIN, SERVICE_FETCH_BODY_SENSOR_HISTORY)
        assert hass.services.has_service(DOMAIN, SERVICE_FETCH_DOOR_SENSOR_HISTORY)

    async def test_async_setup_entry_wires_runtime_data_to_coordinator(self, hass) -> None:
        """Runtime setup should store the constructed coordinator on entry.runtime_data."""
        entry = MockConfigEntry(domain=DOMAIN, data={"phone_id": "test-phone-id"})
        entry.add_to_hass(hass)
        client = MagicMock()
        auth_manager = MagicMock()
        coordinator = MagicMock()
        coordinator.async_config_entry_first_refresh = AsyncMock()
        coordinator.async_shutdown = AsyncMock()

        with (
            patch("custom_components.lipro.async_ensure_runtime_infra", new=AsyncMock()),
            patch(
                "custom_components.lipro.build_entry_auth_context",
                return_value=(client, auth_manager),
            ),
            patch("custom_components.lipro.async_authenticate_entry", new=AsyncMock()),
            patch("custom_components.lipro.get_entry_int_option", return_value=30),
            patch("custom_components.lipro.Coordinator", return_value=coordinator) as ctor,
            patch("custom_components.lipro.persist_entry_tokens_if_changed"),
            patch.object(hass.config_entries, "async_forward_entry_setups", new=AsyncMock()),
            patch("custom_components.lipro.store_entry_options_snapshot"),
        ):
            assert await async_setup_entry(hass, entry) is True

        assert entry.runtime_data is coordinator
        coordinator.async_config_entry_first_refresh.assert_awaited_once_with()
        assert ctor.call_count == 1

    def test_build_entry_auth_context_missing_phone_id_raises(self, hass) -> None:
        """Missing required keys in entry.data should raise ConfigEntryAuthFailed."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE: "13800000000",
            },
        )

        with pytest.raises(ConfigEntryAuthFailed):
            build_entry_auth_context(
                hass,
                entry,
                get_client_session=lambda _: MagicMock(),
                protocol_factory=LiproProtocolFacade,
                auth_manager_factory=LiproAuthManager,
                logger=_TEST_LOGGER,
            )

    def test_build_entry_auth_context_missing_phone_raises(self, hass) -> None:
        """Missing phone in entry.data should raise ConfigEntryAuthFailed."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
            },
        )

        with pytest.raises(ConfigEntryAuthFailed):
            build_entry_auth_context(
                hass,
                entry,
                get_client_session=lambda _: MagicMock(),
                protocol_factory=LiproProtocolFacade,
                auth_manager_factory=LiproAuthManager,
                logger=_TEST_LOGGER,
            )

    async def test_async_ensure_runtime_infra_handles_corrupt_domain_data(
        self,
        hass,
    ) -> None:
        """Shared infra should still be set up when hass.data[DOMAIN] is corrupted."""
        hass.data[DOMAIN] = "not-a-dict"

        mock_setup_services = AsyncMock()
        mock_setup_listener = MagicMock()

        await async_ensure_runtime_infra(
            hass,
            setup_services=mock_setup_services,
            setup_device_registry_listener=mock_setup_listener,
        )

        mock_setup_services.assert_awaited_once()
        mock_setup_listener.assert_called_once()

    def test_device_registry_listener_helpers_handle_corrupt_domain_data(
        self,
        hass,
    ) -> None:
        """Listener helpers should no-op when hass.data[DOMAIN] is corrupted."""
        hass.data[DOMAIN] = "not-a-dict"
        setup_device_registry_listener(hass, logger=_TEST_LOGGER)
        remove_device_registry_listener(hass)

    def test_persist_entry_tokens_skips_when_tokens_missing(self, hass) -> None:
        """Token persistence should not update entry when auth data is incomplete."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
            },
        )
        entry.add_to_hass(hass)

        mock_auth = MagicMock()
        mock_auth.get_auth_session.return_value = AuthSessionSnapshot(
            access_token=None,
            refresh_token=None,
            user_id=None,
            expires_at=None,
            phone_id="phone-id",
            biz_id=None,
        )

        with patch.object(hass.config_entries, "async_update_entry") as mock_update:
            persist_entry_tokens_if_changed(hass, entry, mock_auth)

        mock_update.assert_not_called()
