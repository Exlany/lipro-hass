"""Topicized init regression coverage extracted from `tests/core/test_init.py` (test_init_runtime_behavior)."""

from __future__ import annotations

from .test_init import (
    _TEST_LOGGER,
    ATTR_ENTRY_ID,
    CONF_ACCESS_TOKEN,
    CONF_DEBUG_MODE,
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REFRESH_TOKEN,
    CONF_REQUEST_TIMEOUT,
    CONF_SCAN_INTERVAL,
    DEFAULT_REQUEST_TIMEOUT,
    DOMAIN,
    MAX_SCAN_INTERVAL,
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
    AsyncMock,
    AuthSessionSnapshot,
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    LiproAuthError,
    LiproAuthManager,
    LiproConnectionError,
    LiproDevice,
    LiproProtocolFacade,
    MagicMock,
    MockConfigEntry,
    ServiceValidationError,
    async_ensure_runtime_infra,
    async_handle_refresh_devices,
    async_reload_entry,
    async_setup,
    async_setup_entry,
    async_unload_entry,
    asyncio,
    build_entry_auth_context,
    dr,
    patch,
    persist_entry_tokens_if_changed,
    pytest,
    remove_device_registry_listener,
    service_call,
    setup_device_registry_listener,
)


class TestInitRuntimeBehavior:
    """Tests for __init__.py runtime behaviors."""

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

        # Calling setup twice should keep registration stable.
        assert await async_setup(hass, {}) is True
        assert hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND)

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
                client_factory=LiproProtocolFacade,
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
                client_factory=LiproProtocolFacade,
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
            pytest.raises(ConfigEntryAuthFailed),
        ):
            await async_setup_entry(hass, entry)

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
            pytest.raises(ConfigEntryNotReady),
        ):
            await async_setup_entry(hass, entry)

    async def test_async_unload_entry_removes_services_on_last_entry(
        self, hass
    ) -> None:
        """Service registrations are removed when last entry unloads."""
        await async_setup(hass, {})
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            AsyncMock(return_value=True),
        ):
            assert await async_unload_entry(hass, entry) is True

        assert not hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_SCHEDULES)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_DEVELOPER_REPORT)
        assert not hass.services.has_service(DOMAIN, SERVICE_SUBMIT_DEVELOPER_FEEDBACK)
        assert not hass.services.has_service(DOMAIN, SERVICE_QUERY_COMMAND_RESULT)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_CITY)
        assert not hass.services.has_service(DOMAIN, SERVICE_QUERY_USER_CLOUD)
        assert not hass.services.has_service(DOMAIN, SERVICE_REFRESH_DEVICES)

    async def test_async_unload_entry_shuts_down_runtime_data_coordinator(
        self, hass
    ) -> None:
        """Coordinator runtime data should be shut down on successful unload."""
        await async_setup(hass, {})
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        coordinator = MagicMock()
        coordinator.async_shutdown = AsyncMock()
        entry.runtime_data = coordinator

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            AsyncMock(return_value=True),
        ):
            assert await async_unload_entry(hass, entry) is True

        coordinator.async_shutdown.assert_awaited_once()
        assert getattr(entry, "runtime_data", None) is None

    async def test_async_unload_entry_logs_and_continues_on_shutdown_error(
        self,
        hass,
    ) -> None:
        """Unload should catch shutdown errors so unload can complete."""
        await async_setup(hass, {})
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        coordinator = MagicMock()
        coordinator.async_shutdown = AsyncMock(side_effect=RuntimeError("boom"))
        entry.runtime_data = coordinator

        with (
            patch.object(
                hass.config_entries,
                "async_unload_platforms",
                AsyncMock(return_value=True),
            ),
            patch("custom_components.lipro._LOGGER.warning") as mock_warning,
        ):
            assert await async_unload_entry(hass, entry) is True

        assert mock_warning.call_args.args[1:] == (
            "unload",
            "unload_shutdown_degraded",
            "log_and_continue",
            "RuntimeError",
        )
        assert getattr(entry, "runtime_data", None) is None

    async def test_async_unload_entry_removes_services_when_lock_unavailable(
        self,
        hass,
    ) -> None:
        """Unload should remove shared infra when lock store is unavailable."""
        await async_setup(hass, {})
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        hass.data[DOMAIN] = "not-a-dict"

        with (
            patch.object(
                hass.config_entries,
                "async_unload_platforms",
                AsyncMock(return_value=True),
            ),
            patch(
                "custom_components.lipro.has_other_runtime_entries", return_value=False
            ),
            patch("custom_components.lipro.remove_services") as mock_remove_services,
            patch(
                "custom_components.lipro.remove_device_registry_listener"
            ) as mock_remove_listener,
        ):
            assert await async_unload_entry(hass, entry) is True

        from custom_components.lipro.services.registrations import SERVICE_REGISTRATIONS

        mock_remove_services.assert_called_once_with(
            hass,
            domain=DOMAIN,
            registrations=SERVICE_REGISTRATIONS,
        )
        mock_remove_listener.assert_called_once_with(hass)

    async def test_async_reload_entry_forwards_to_hass(self, hass) -> None:
        """async_reload_entry should delegate to hass reload."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        mock_reload = AsyncMock()
        with patch.object(hass.config_entries, "async_reload", mock_reload):
            await async_reload_entry(hass, entry)

        mock_reload.assert_awaited_once_with(entry.entry_id)

    async def test_async_reload_entry_uses_named_not_ready_contract(self, hass) -> None:
        """Reload failures should preserve a named contract before re-raising."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        with (
            patch.object(
                hass.config_entries,
                "async_reload",
                AsyncMock(side_effect=ConfigEntryNotReady("retry reload")),
            ),
            patch("custom_components.lipro._LOGGER.debug") as mock_debug,
            pytest.raises(ConfigEntryNotReady),
        ):
            await async_reload_entry(hass, entry)

        assert mock_debug.call_args.args[1:] == (
            "reload",
            "reload_not_ready",
            "propagate",
            "ConfigEntryNotReady",
        )

    async def test_async_unload_entry_removes_services_when_only_non_runtime_entries_remain(
        self, hass
    ) -> None:
        """Services should be removed when no other runtime-loaded entry remains."""
        await async_setup(hass, {})
        active_entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        active_entry.add_to_hass(hass)
        active_entry.runtime_data = MagicMock(async_shutdown=AsyncMock())

        # Simulate a configured but not loaded entry (no runtime_data).
        passive_entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        passive_entry.add_to_hass(hass)

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            AsyncMock(return_value=True),
        ):
            assert await async_unload_entry(hass, active_entry) is True

        assert not hass.services.has_service(DOMAIN, SERVICE_SEND_COMMAND)
        assert not hass.services.has_service(DOMAIN, SERVICE_GET_SCHEDULES)
        assert getattr(passive_entry, "runtime_data", None) is None

    async def test_async_unload_entry_does_not_shutdown_on_failed_unload(
        self, hass
    ) -> None:
        """Coordinator shutdown should not run when platform unload fails."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)

        coordinator = MagicMock()
        coordinator.async_shutdown = AsyncMock()
        entry.runtime_data = coordinator

        with patch.object(
            hass.config_entries,
            "async_unload_platforms",
            AsyncMock(return_value=False),
        ):
            assert await async_unload_entry(hass, entry) is False

        coordinator.async_shutdown.assert_not_awaited()

    async def test_refresh_devices_handler_refreshes_all_loaded_entries(
        self, hass
    ) -> None:
        """refresh_devices should refresh all loaded entry coordinators by default."""
        first = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        first.add_to_hass(hass)
        first_service = MagicMock()
        first_service.async_refresh_devices = AsyncMock()
        first.runtime_data = MagicMock(device_refresh_service=first_service)

        second = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        second.add_to_hass(hass)
        second_service = MagicMock()
        second_service.async_refresh_devices = AsyncMock()
        second.runtime_data = MagicMock(device_refresh_service=second_service)

        result = await async_handle_refresh_devices(hass, service_call(hass, {}))

        assert result["success"] is True
        assert result["refreshed_entries"] == 2
        assert "entry_ids" not in result
        first_service.async_refresh_devices.assert_awaited_once()
        second_service.async_refresh_devices.assert_awaited_once()

    async def test_refresh_devices_handler_filters_by_entry_id(self, hass) -> None:
        """refresh_devices should refresh only the selected config entry."""
        first = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        first.add_to_hass(hass)
        first_service = MagicMock()
        first_service.async_refresh_devices = AsyncMock()
        first.runtime_data = MagicMock(device_refresh_service=first_service)

        second = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13900000000"},
            options={CONF_DEBUG_MODE: True},
        )
        second.add_to_hass(hass)
        second_service = MagicMock()
        second_service.async_refresh_devices = AsyncMock()
        second.runtime_data = MagicMock(device_refresh_service=second_service)

        result = await async_handle_refresh_devices(
            hass,
            service_call(hass, {ATTR_ENTRY_ID: second.entry_id}),
        )

        assert result["success"] is True
        assert result["refreshed_entries"] == 1
        assert result["requested_entry_id"] == second.entry_id
        first_service.async_refresh_devices.assert_not_awaited()
        second_service.async_refresh_devices.assert_awaited_once()

    async def test_refresh_devices_handler_unknown_entry_raises(self, hass) -> None:
        """refresh_devices should raise translated validation error for bad entry_id."""
        with pytest.raises(ServiceValidationError) as exc:
            await async_handle_refresh_devices(
                hass,
                service_call(hass, {ATTR_ENTRY_ID: "missing_entry"}),
            )

        assert exc.value.translation_key == "entry_not_found"

    async def test_device_registry_disable_enable_triggers_entry_reload(
        self, hass
    ) -> None:
        """Lipro device disable/enable transitions should trigger config entry reload."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = MagicMock()

        with patch.object(
            hass.config_entries,
            "async_reload",
            AsyncMock(return_value=True),
        ) as mock_reload:
            await async_setup(hass, {})

            device_registry = dr.async_get(hass)
            device_entry = device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={(DOMAIN, "03ab5ccd7c123456")},
                manufacturer="Lipro",
                name="Lipro Device",
            )

            device_registry.async_update_device(
                device_entry.id,
                disabled_by=dr.DeviceEntryDisabler.USER,
            )
            await hass.async_block_till_done()

            device_registry.async_update_device(
                device_entry.id,
                disabled_by=None,
            )
            await hass.async_block_till_done()

        assert mock_reload.await_count == 2
        assert mock_reload.await_args_list[0].args == (entry.entry_id,)
        assert mock_reload.await_args_list[1].args == (entry.entry_id,)

    async def test_device_registry_listener_ignores_non_lipro_device_updates(
        self, hass
    ) -> None:
        """Only Lipro devices with disabled_by changes should trigger reload."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = MagicMock()

        with patch.object(
            hass.config_entries,
            "async_reload",
            AsyncMock(return_value=True),
        ) as mock_reload:
            await async_setup(hass, {})

            device_registry = dr.async_get(hass)
            non_lipro = device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={("other_domain", "dev-1")},
                manufacturer="Other",
                name="Other Device",
            )
            lipro = device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={(DOMAIN, "03ab5ccd7c999999")},
                manufacturer="Lipro",
                name="Lipro Device",
            )

            # Non-Lipro device: ignore even if disabled_by changed.
            device_registry.async_update_device(
                non_lipro.id,
                disabled_by=dr.DeviceEntryDisabler.USER,
            )
            # Lipro device, but unrelated update: ignore.
            device_registry.async_update_device(
                lipro.id,
                name="Renamed Lipro Device",
            )
            await hass.async_block_till_done()

        mock_reload.assert_not_awaited()

    async def test_async_unload_entry_removes_device_registry_listener(
        self, hass
    ) -> None:
        """Device registry updates should stop reloading after the last unload."""
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={"phone": "13800000000"},
            options={CONF_DEBUG_MODE: True},
        )
        entry.add_to_hass(hass)
        entry.runtime_data = MagicMock(async_shutdown=AsyncMock())

        with patch.object(
            hass.config_entries,
            "async_reload",
            AsyncMock(return_value=True),
        ) as mock_reload:
            await async_setup(hass, {})

            device_registry = dr.async_get(hass)
            device_entry = device_registry.async_get_or_create(
                config_entry_id=entry.entry_id,
                identifiers={(DOMAIN, "03ab5ccd7c111111")},
                manufacturer="Lipro",
                name="Lipro Device",
            )

            with patch.object(
                hass.config_entries,
                "async_unload_platforms",
                AsyncMock(return_value=True),
            ):
                assert await async_unload_entry(hass, entry) is True

            device_registry.async_update_device(
                device_entry.id,
                disabled_by=dr.DeviceEntryDisabler.USER,
            )
            await hass.async_block_till_done()

        mock_reload.assert_not_awaited()
