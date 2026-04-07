"""Failure-path setup-entry init runtime topical suites."""

from __future__ import annotations

from .test_init import (
    CONF_ACCESS_TOKEN,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REFRESH_TOKEN,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
    DEFAULT_REQUEST_TIMEOUT,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    AsyncMock,
    AuthSessionSnapshot,
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    LiproAuthError,
    LiproConnectionError,
    LiproDevice,
    MagicMock,
    MockConfigEntry,
    async_setup_entry,
    asyncio,
    patch,
    pytest,
)


class _InitRuntimeBehaviorBase:
    """Shared helpers for init runtime-behavior topical suites."""

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


class TestInitSetupEntryFailureBehavior(_InitRuntimeBehaviorBase):
    """Tests for setup-entry rollback, coercion, and named failure contracts."""

    async def test_async_setup_entry_forward_setup_failure_rolls_back_runtime_data(
        self, hass
    ) -> None:
        """Platform setup failure should shut down coordinator and clear runtime data."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
                CONF_PASSWORD_HASH: "hashed-password",
                CONF_ACCESS_TOKEN: "old_access",
                CONF_REFRESH_TOKEN: "old_refresh",
            },
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
        mock_coordinator.async_shutdown = AsyncMock()

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
                AsyncMock(side_effect=RuntimeError("platform setup failed")),
            ),
            patch.object(hass.config_entries, "async_update_entry"),
            patch("custom_components.lipro._LOGGER.debug") as mock_debug,
            pytest.raises(RuntimeError, match="platform setup failed"),
        ):
            await async_setup_entry(hass, entry)

        mock_coordinator.async_shutdown.assert_awaited_once()
        assert mock_debug.call_args.args[1:] == (
            "setup",
            "setup_failed",
            "cleanup_and_raise",
            "RuntimeError",
        )
        assert getattr(entry, "runtime_data", None) is None
        entry.add_update_listener.assert_not_called()
        entry.async_on_unload.assert_not_called()

    async def test_async_setup_entry_programming_error_during_hook_binding_cleans_up(
        self,
        hass,
    ) -> None:
        """Unexpected hook-binding errors should clean up without claiming a lifecycle contract."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
                CONF_PASSWORD_HASH: "hashed-password",
                CONF_ACCESS_TOKEN: "old_access",
                CONF_REFRESH_TOKEN: "old_refresh",
            },
        )
        entry.add_to_hass(hass)
        entry.add_update_listener = MagicMock(side_effect=TypeError("bad listener"))
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
        mock_coordinator.async_shutdown = AsyncMock()

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
            ),
            patch.object(hass.config_entries, "async_update_entry"),
            patch("custom_components.lipro._LOGGER.debug") as mock_debug,
            pytest.raises(TypeError, match="bad listener"),
        ):
            await async_setup_entry(hass, entry)

        mock_coordinator.async_shutdown.assert_awaited_once()
        mock_debug.assert_not_called()
        assert getattr(entry, "runtime_data", None) is None
        assert entry.entry_id not in hass.data[DOMAIN]["options_snapshots"]
        entry.async_on_unload.assert_not_called()

    async def test_async_setup_entry_forward_setup_cancelled_rolls_back_runtime_data(
        self,
        hass,
    ) -> None:
        """Platform setup cancellation should still shut down coordinator and clear runtime data."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
                CONF_PASSWORD_HASH: "hashed-password",
                CONF_ACCESS_TOKEN: "old_access",
                CONF_REFRESH_TOKEN: "old_refresh",
            },
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
        mock_coordinator.async_shutdown = AsyncMock()

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
                AsyncMock(side_effect=asyncio.CancelledError),
            ),
            patch.object(hass.config_entries, "async_update_entry"),
            pytest.raises(asyncio.CancelledError),
        ):
            await async_setup_entry(hass, entry)

        mock_coordinator.async_shutdown.assert_awaited_once()
        assert getattr(entry, "runtime_data", None) is None
        entry.add_update_listener.assert_not_called()
        entry.async_on_unload.assert_not_called()

    async def test_async_setup_entry_first_refresh_failure_cleans_up(
        self,
        hass,
    ) -> None:
        """First refresh failure should shut down coordinator and avoid listener setup."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
                CONF_PASSWORD_HASH: "hashed-password",
                CONF_ACCESS_TOKEN: "old_access",
                CONF_REFRESH_TOKEN: "old_refresh",
            },
        )
        entry.add_to_hass(hass)
        entry.add_update_listener = MagicMock(return_value=MagicMock())
        entry.async_on_unload = MagicMock()

        mock_auth = MagicMock()
        mock_auth.set_tokens = MagicMock()
        mock_auth.set_credentials = MagicMock()
        mock_auth.ensure_valid_token = AsyncMock()
        mock_auth.get_auth_session.return_value = AuthSessionSnapshot(
            access_token="old_access",
            refresh_token="old_refresh",
            user_id=None,
            expires_at=1234567890,
            phone_id="phone-id",
            biz_id=None,
        )

        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock(
            side_effect=RuntimeError("refresh failed")
        )
        mock_coordinator.async_shutdown = AsyncMock()

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
            pytest.raises(RuntimeError, match="refresh failed"),
        ):
            await async_setup_entry(hass, entry)

        mock_coordinator.async_shutdown.assert_awaited_once()
        assert getattr(entry, "runtime_data", None) is None
        entry.add_update_listener.assert_not_called()
        entry.async_on_unload.assert_not_called()

    async def test_async_setup_entry_first_refresh_not_ready_uses_named_contract(
        self,
        hass,
    ) -> None:
        """First refresh not-ready failures should keep a named setup contract."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
                CONF_PASSWORD_HASH: "hashed-password",
                CONF_ACCESS_TOKEN: "old_access",
                CONF_REFRESH_TOKEN: "old_refresh",
            },
        )
        entry.add_to_hass(hass)
        entry.add_update_listener = MagicMock(return_value=MagicMock())
        entry.async_on_unload = MagicMock()

        mock_auth = MagicMock()
        mock_auth.set_tokens = MagicMock()
        mock_auth.set_credentials = MagicMock()
        mock_auth.ensure_valid_token = AsyncMock()
        mock_auth.get_auth_session.return_value = AuthSessionSnapshot(
            access_token="old_access",
            refresh_token="old_refresh",
            user_id=None,
            expires_at=1234567890,
            phone_id="phone-id",
            biz_id=None,
        )

        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock(
            side_effect=ConfigEntryNotReady("refresh later")
        )
        mock_coordinator.async_shutdown = AsyncMock()

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
            patch("custom_components.lipro._LOGGER.debug") as mock_debug,
            pytest.raises(ConfigEntryNotReady),
        ):
            await async_setup_entry(hass, entry)

        mock_coordinator.async_shutdown.assert_awaited_once()
        assert mock_debug.call_args.args[1:] == (
            "setup",
            "setup_not_ready",
            "cleanup_and_raise",
            "ConfigEntryNotReady",
        )
        assert getattr(entry, "runtime_data", None) is None
        entry.add_update_listener.assert_not_called()
        entry.async_on_unload.assert_not_called()

    async def test_async_setup_entry_auth_error_raises_config_entry_auth_failed(
        self, hass
    ) -> None:
        """Auth failures are surfaced as ConfigEntryAuthFailed."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
                CONF_PASSWORD_HASH: "hashed-password",
            },
        )
        entry.add_to_hass(hass)

        mock_auth = MagicMock()
        mock_auth.set_credentials = MagicMock()
        mock_auth.ensure_valid_token = AsyncMock(side_effect=LiproAuthError("bad auth"))

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.LiproProtocolFacade", return_value=MagicMock()
            ),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch("custom_components.lipro._LOGGER.debug") as mock_debug,
            pytest.raises(ConfigEntryAuthFailed),
        ):
            await async_setup_entry(hass, entry)

        assert mock_debug.call_args.args[1:] == (
            "setup",
            "setup_auth_failed",
            "cleanup_and_raise",
            "ConfigEntryAuthFailed",
        )

    async def test_async_setup_entry_coerces_invalid_persisted_options(
        self, hass
    ) -> None:
        """Persisted non-schema options should be coerced/clamped safely."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
                CONF_PASSWORD_HASH: "hashed-password",
                CONF_ACCESS_TOKEN: "access",
                CONF_REFRESH_TOKEN: "refresh",
            },
            options={
                CONF_REQUEST_TIMEOUT: "not-an-int",
                CONF_SCAN_INTERVAL: 999999,
            },
        )
        entry.add_to_hass(hass)
        entry.add_update_listener = MagicMock(return_value=MagicMock())
        entry.async_on_unload = MagicMock()

        mock_auth = MagicMock()
        mock_auth.set_tokens = MagicMock()
        mock_auth.set_credentials = MagicMock()
        mock_auth.ensure_valid_token = AsyncMock()
        mock_auth.get_auth_session.return_value = AuthSessionSnapshot(
            access_token="access",
            refresh_token="refresh",
            user_id=None,
            expires_at=1234567890,
            phone_id="phone-id",
            biz_id=None,
        )

        mock_client = MagicMock()
        mock_coordinator = MagicMock()
        mock_coordinator.async_config_entry_first_refresh = AsyncMock()

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.LiproProtocolFacade", return_value=mock_client
            ) as pc,
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch(
                "custom_components.lipro.Coordinator",
                return_value=mock_coordinator,
            ) as pcoord,
            patch.object(
                hass.config_entries,
                "async_forward_entry_setups",
                AsyncMock(return_value=True),
            ),
            patch.object(hass.config_entries, "async_update_entry"),
        ):
            assert await async_setup_entry(hass, entry) is True

        assert pc.call_args.kwargs["request_timeout"] == DEFAULT_REQUEST_TIMEOUT
        assert pcoord.call_args.kwargs["update_interval"] == MAX_SCAN_INTERVAL

    async def test_async_setup_entry_connection_error_raises_not_ready(
        self, hass
    ) -> None:
        """Connection failures are surfaced as ConfigEntryNotReady."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PHONE_ID: "phone-id",
                CONF_PHONE: "13800000000",
                CONF_PASSWORD_HASH: "hashed-password",
            },
        )
        entry.add_to_hass(hass)

        mock_auth = MagicMock()
        mock_auth.set_credentials = MagicMock()
        mock_auth.ensure_valid_token = AsyncMock(
            side_effect=LiproConnectionError("offline")
        )

        with (
            patch(
                "custom_components.lipro.async_get_clientsession",
                return_value=MagicMock(),
            ),
            patch(
                "custom_components.lipro.LiproProtocolFacade", return_value=MagicMock()
            ),
            patch("custom_components.lipro.LiproAuthManager", return_value=mock_auth),
            patch("custom_components.lipro._LOGGER.debug") as mock_debug,
            pytest.raises(ConfigEntryNotReady),
        ):
            await async_setup_entry(hass, entry)

        assert mock_debug.call_args.args[1:] == (
            "setup",
            "setup_not_ready",
            "cleanup_and_raise",
            "ConfigEntryNotReady",
        )

