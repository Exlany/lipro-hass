"""Integration tests for Lipro data update coordinator.

These tests exercise the real coordinator methods (_async_update_data,
_fetch_devices, _update_device_status, _load_product_configs, etc.)
with mocked API responses, verifying the coordinator's actual behavior.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.api import MAX_DEVICES_PER_QUERY
from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import (
    CONF_DEVICE_FILTER_DID_LIST,
    CONF_DEVICE_FILTER_DID_MODE,
    CONF_DEVICE_FILTER_HOME_LIST,
    CONF_DEVICE_FILTER_HOME_MODE,
    CONF_DEVICE_FILTER_SSID_LIST,
    CONF_DEVICE_FILTER_SSID_MODE,
    DEVICE_FILTER_MODE_EXCLUDE,
    DEVICE_FILTER_MODE_INCLUDE,
)
from custom_components.lipro.core.api import (
    LiproApiError,
    LiproAuthError,
    LiproConnectionError,
    LiproRefreshTokenExpiredError,
)
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import UpdateFailed

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CONFIG_ENTRY_DATA = {
    "phone": "13800000000",
    "password_hash": "e10adc3949ba59abbe56e057f20f883e",
    "phone_id": "test-phone-id",
    "access_token": "test_token",
    "refresh_token": "test_refresh",
    "user_id": 10001,
}


def _make_api_device(
    *,
    serial: str = "03ab5ccd7cxxxxxx",
    name: str = "Test Light",
    device_type: int = 1,
    iot_name: str = "lipro_led",
    physical_model: str = "light",
    is_group: bool = False,
    product_id: int | None = None,
) -> dict[str, object]:
    """Build a device dict matching the API response format."""
    d = {
        "deviceId": 1,
        "serial": serial,
        "deviceName": name,
        "type": device_type,
        "iotName": iot_name,
        "physicalModel": physical_model,
        "isGroup": is_group,
    }
    if product_id is not None:
        d["productId"] = product_id
    return d


@pytest.fixture
def coordinator(hass, mock_lipro_api_client, mock_auth_manager):
    """Create a real LiproDataUpdateCoordinator wired to mock API/auth."""
    entry = MockConfigEntry(
        domain="lipro",
        data=_CONFIG_ENTRY_DATA,
        options={},
        unique_id="lipro_10001",
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
    ) as mock_share:
        mock_share.return_value = MagicMock(is_enabled=False, set_enabled=MagicMock())
        from custom_components.lipro.core.coordinator import LiproDataUpdateCoordinator

        return LiproDataUpdateCoordinator(
            hass, mock_lipro_api_client, mock_auth_manager, entry
        )


# =========================================================================
# 1. _async_update_data happy-path flow
# =========================================================================


class TestCoordinatorUpdateFlow:
    """Test _async_update_data fetches devices on first call then queries status."""

    @pytest.mark.asyncio
    async def test_first_update_fetches_devices_and_status(
        self, coordinator, mock_lipro_api_client
    ):
        """First call should fetch devices, load product configs, then query status."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [
                _make_api_device(serial="03ab5ccd7c000001", name="Light 1"),
            ]
        }
        mock_lipro_api_client.query_device_status.return_value = [
            {
                "deviceId": "03ab5ccd7c000001",
                "properties": [{"key": "powerState", "value": "1"}],
            }
        ]
        mock_lipro_api_client.query_connect_status.return_value = {
            "03ab5ccd7c000001": True,
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            result = await coordinator._async_update_data()

        assert "03ab5ccd7c000001" in result
        mock_lipro_api_client.get_device_list.assert_called_once()
        mock_lipro_api_client.query_device_status.assert_called_once()
        mock_lipro_api_client.get_product_configs.assert_called_once()

    @pytest.mark.asyncio
    async def test_second_update_skips_device_fetch(
        self, coordinator, mock_lipro_api_client
    ):
        """Subsequent calls should NOT re-fetch devices."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [_make_api_device(serial="03ab5ccd7c000001")]
        }
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()
            mock_lipro_api_client.get_device_list.reset_mock()
            await coordinator._async_update_data()

        mock_lipro_api_client.get_device_list.assert_not_called()

    @pytest.mark.asyncio
    async def test_periodic_update_refetches_device_list(
        self, coordinator, mock_lipro_api_client
    ):
        """Periodic refresh should re-fetch devices even without force flag."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [_make_api_device(serial="03ab5ccd7c000001")]
        }
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()
            mock_lipro_api_client.get_device_list.reset_mock()

            coordinator._force_device_refresh = False
            coordinator._last_device_refresh_at = 0.0
            with patch(
                "custom_components.lipro.core.coordinator.device_refresh.monotonic",
                return_value=9999.0,
            ):
                await coordinator._async_update_data()

        mock_lipro_api_client.get_device_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_valid_token_called(
        self, coordinator, mock_lipro_api_client, mock_auth_manager
    ):
        """_async_update_data must call ensure_valid_token before anything else."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [_make_api_device()]
        }
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()

        mock_auth_manager.ensure_valid_token.assert_awaited()


# =========================================================================
# 2. _fetch_devices — pagination, gateway filtering, ID collection
# =========================================================================


class TestCoordinatorFetchDevices:
    """Test _fetch_devices pagination, gateway filtering, and ID buckets."""

    @pytest.mark.asyncio
    async def test_single_page(self, coordinator, mock_lipro_api_client):
        """Fewer than MAX_DEVICES_PER_QUERY devices should require one page."""
        devices = [_make_api_device(serial=f"03ab5ccd7c{i:06x}") for i in range(3)]
        mock_lipro_api_client.get_device_list.return_value = {"devices": devices}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._fetch_devices()

        assert len(coordinator.devices) == 3
        mock_lipro_api_client.get_device_list.assert_called_once_with(
            offset=0, limit=MAX_DEVICES_PER_QUERY
        )

    @pytest.mark.asyncio
    async def test_pagination_multiple_pages(self, coordinator, mock_lipro_api_client):
        """When first page is full, coordinator should request a second page."""
        page1 = [
            _make_api_device(serial=f"03ab5ccd7c{i:06x}")
            for i in range(MAX_DEVICES_PER_QUERY)
        ]
        page2 = [_make_api_device(serial=f"03ab5ccd7d{i:06x}") for i in range(5)]
        mock_lipro_api_client.get_device_list.side_effect = [
            {"devices": page1},
            {"devices": page2},
        ]

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._fetch_devices()

        assert len(coordinator.devices) == MAX_DEVICES_PER_QUERY + 5
        assert mock_lipro_api_client.get_device_list.call_count == 2

    @pytest.mark.asyncio
    async def test_fetch_devices_rejects_malformed_devices_payload(
        self, coordinator, mock_lipro_api_client
    ):
        """Malformed devices payload should fail fast with a clear API error."""
        mock_lipro_api_client.get_device_list.return_value = {"devices": "invalid"}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            with pytest.raises(LiproApiError, match="Malformed device list payload"):
                await coordinator._fetch_devices()

    @pytest.mark.asyncio
    async def test_fetch_devices_skips_non_dict_rows(
        self, coordinator, mock_lipro_api_client
    ):
        """Non-dict device rows should be ignored without breaking refresh."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [
                _make_api_device(serial="03ab5ccd7c000001"),
                "bad-row",
                123,
            ]
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._fetch_devices()

        assert set(coordinator.devices) == {"03ab5ccd7c000001"}

    @pytest.mark.asyncio
    async def test_gateway_devices_filtered_out(
        self, coordinator, mock_lipro_api_client
    ):
        """Gateway devices must be excluded from the device dict."""
        devices = [
            _make_api_device(serial="03ab5ccd7c000001", physical_model="light"),
            _make_api_device(
                serial="03ab5ccd7c000002",
                physical_model="gateway",
                device_type=11,
            ),
        ]
        mock_lipro_api_client.get_device_list.return_value = {"devices": devices}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._fetch_devices()

        assert len(coordinator.devices) == 1
        assert "03ab5ccd7c000001" in coordinator.devices
        assert "03ab5ccd7c000002" not in coordinator.devices

    @pytest.mark.asyncio
    async def test_group_vs_device_id_collection(
        self, coordinator, mock_lipro_api_client
    ):
        """Groups go to _group_ids_to_query; non-groups to _iot_ids_to_query."""
        devices = [
            _make_api_device(serial="03ab5ccd7c000001"),
            _make_api_device(
                serial="mesh_group_10001",
                name="All Lights",
                is_group=True,
            ),
        ]
        mock_lipro_api_client.get_device_list.return_value = {"devices": devices}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._fetch_devices()

        assert "03ab5ccd7c000001" in coordinator._iot_ids_to_query
        assert "mesh_group_10001" in coordinator._group_ids_to_query
        assert "mesh_group_10001" not in coordinator._iot_ids_to_query

    @pytest.mark.asyncio
    async def test_outlet_ids_collected(self, coordinator, mock_lipro_api_client):
        """Outlet devices should appear in _outlet_ids_to_query."""
        devices = [
            _make_api_device(serial="03ab5ccd7c000001", physical_model="light"),
            _make_api_device(
                serial="03ab5ccd7c000002",
                physical_model="outlet",
                device_type=6,
            ),
        ]
        mock_lipro_api_client.get_device_list.return_value = {"devices": devices}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._fetch_devices()

        assert "03ab5ccd7c000002" in coordinator._outlet_ids_to_query
        assert "03ab5ccd7c000001" not in coordinator._outlet_ids_to_query

    @pytest.mark.asyncio
    async def test_group_outlet_ids_collected(
        self, coordinator, mock_lipro_api_client
    ):
        """Group outlets should be queried as both group IDs and outlet IDs."""
        devices = [
            _make_api_device(
                serial="mesh_group_10001",
                name="All Outlets",
                physical_model="outlet",
                is_group=True,
            ),
        ]
        mock_lipro_api_client.get_device_list.return_value = {"devices": devices}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._fetch_devices()

        assert "mesh_group_10001" in coordinator._group_ids_to_query
        assert "mesh_group_10001" in coordinator._outlet_ids_to_query
        assert "mesh_group_10001" not in coordinator._iot_ids_to_query

    @pytest.mark.asyncio
    async def test_device_filter_include_home_applies_in_fetch_path(
        self, coordinator, mock_lipro_api_client
    ):
        """Include-home mode should keep only rows that match configured home list."""
        coordinator.hass.config_entries.async_update_entry(
            coordinator.config_entry,
            options={
                CONF_DEVICE_FILTER_HOME_MODE: DEVICE_FILTER_MODE_INCLUDE,
                CONF_DEVICE_FILTER_HOME_LIST: "Main Home",
            },
        )
        coordinator._load_options()
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [
                {
                    **_make_api_device(serial="03ab5ccd7c000001"),
                    "homeName": "Main Home",
                },
                {**_make_api_device(serial="03ab5ccd7c000002"), "homeName": "Other"},
            ]
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._fetch_devices()

        assert set(coordinator.devices) == {"03ab5ccd7c000001"}

    @pytest.mark.asyncio
    async def test_device_filter_exclude_did_applies_in_fetch_path(
        self, coordinator, mock_lipro_api_client
    ):
        """Exclude-did mode should drop rows whose did/serial matches filter list."""
        coordinator.hass.config_entries.async_update_entry(
            coordinator.config_entry,
            options={
                CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_EXCLUDE,
                CONF_DEVICE_FILTER_DID_LIST: "03ab5ccd7c000002",
            },
        )
        coordinator._load_options()
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [
                _make_api_device(serial="03ab5ccd7c000001"),
                _make_api_device(serial="03ab5ccd7c000002"),
            ]
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._fetch_devices()

        assert set(coordinator.devices) == {"03ab5ccd7c000001"}

    @pytest.mark.asyncio
    async def test_device_filter_include_ssid_reads_device_info_json(
        self, coordinator, mock_lipro_api_client
    ):
        """Include-ssid mode should support ssid from deviceInfo JSON."""
        coordinator.hass.config_entries.async_update_entry(
            coordinator.config_entry,
            options={
                CONF_DEVICE_FILTER_SSID_MODE: DEVICE_FILTER_MODE_INCLUDE,
                CONF_DEVICE_FILTER_SSID_LIST: "homewifi",
            },
        )
        coordinator._load_options()
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [
                {
                    **_make_api_device(serial="03ab5ccd7c000001"),
                    "deviceInfo": '{"wifi_ssid":"HomeWiFi"}',
                },
                {
                    **_make_api_device(serial="03ab5ccd7c000002"),
                    "deviceInfo": '{"wifi_ssid":"GuestWiFi"}',
                },
            ]
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._fetch_devices()

        assert set(coordinator.devices) == {"03ab5ccd7c000001"}

    @pytest.mark.asyncio
    async def test_device_filter_include_with_empty_list_excludes_all(
        self, coordinator, mock_lipro_api_client
    ):
        """Include mode with an empty list should exclude all devices."""
        coordinator.hass.config_entries.async_update_entry(
            coordinator.config_entry,
            options={
                CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_INCLUDE,
                CONF_DEVICE_FILTER_DID_LIST: "",
            },
        )
        coordinator._load_options()
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [
                _make_api_device(serial="03ab5ccd7c000001"),
                _make_api_device(serial="03ab5ccd7c000002"),
            ]
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._fetch_devices()

        assert coordinator.devices == {}

    @pytest.mark.asyncio
    async def test_stale_devices_removed_only_after_consecutive_misses(
        self, coordinator, mock_lipro_api_client
    ):
        """Remove stale devices only after multiple consecutive missing fetches."""
        device_entry = MagicMock(id="reg-id", name="Stale Device")
        registry = MagicMock()
        registry.async_get_device.return_value = device_entry

        # Initial set: A + B, then B missing for 3 consecutive fetches
        mock_lipro_api_client.get_device_list.side_effect = [
            {
                "devices": [
                    _make_api_device(serial="03ab5ccd7c000001"),
                    _make_api_device(serial="03ab5ccd7c000002"),
                ]
            },
            {"devices": [_make_api_device(serial="03ab5ccd7c000001")]},
            {"devices": [_make_api_device(serial="03ab5ccd7c000001")]},
            {"devices": [_make_api_device(serial="03ab5ccd7c000001")]},
        ]

        with (
            patch(
                "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
            ) as mock_share,
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.dr.async_get"
            ) as dr_get,
        ):
            mock_share.return_value = MagicMock(is_enabled=False)
            dr_get.return_value = registry

            await coordinator._fetch_devices()  # seed baseline
            await coordinator._fetch_devices()  # miss #1
            await coordinator._fetch_devices()  # miss #2
            registry.async_remove_device.assert_not_called()

            await coordinator._fetch_devices()  # miss #3 -> remove

        registry.async_remove_device.assert_called_once_with("reg-id")

    @pytest.mark.asyncio
    async def test_stale_device_counter_resets_when_device_reappears(
        self, coordinator, mock_lipro_api_client
    ):
        """A reappearing device should reset missing counter and avoid removal."""
        device_entry = MagicMock(id="reg-id", name="Flaky Device")
        registry = MagicMock()
        registry.async_get_device.return_value = device_entry

        # A + B -> A only (miss B #1) -> A + B (reset) -> A only (miss B #1 again)
        mock_lipro_api_client.get_device_list.side_effect = [
            {
                "devices": [
                    _make_api_device(serial="03ab5ccd7c000001"),
                    _make_api_device(serial="03ab5ccd7c000002"),
                ]
            },
            {"devices": [_make_api_device(serial="03ab5ccd7c000001")]},
            {
                "devices": [
                    _make_api_device(serial="03ab5ccd7c000001"),
                    _make_api_device(serial="03ab5ccd7c000002"),
                ]
            },
            {"devices": [_make_api_device(serial="03ab5ccd7c000001")]},
        ]

        with (
            patch(
                "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
            ) as mock_share,
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.dr.async_get"
            ) as dr_get,
        ):
            mock_share.return_value = MagicMock(is_enabled=False)
            dr_get.return_value = registry

            await coordinator._fetch_devices()
            await coordinator._fetch_devices()
            await coordinator._fetch_devices()
            await coordinator._fetch_devices()

        registry.async_remove_device.assert_not_called()

    @pytest.mark.asyncio
    async def test_stale_reconcile_uses_unfiltered_cloud_serials(
        self, coordinator, mock_lipro_api_client
    ):
        """Device filter should not cause stale-removal for cloud-present devices."""
        coordinator.hass.config_entries.async_update_entry(
            coordinator.config_entry,
            options={
                CONF_DEVICE_FILTER_DID_MODE: DEVICE_FILTER_MODE_INCLUDE,
                CONF_DEVICE_FILTER_DID_LIST: "03ab5ccd7c000001",
            },
        )
        coordinator._load_options()

        registry = MagicMock()
        stale_candidate = MagicMock(id="reg-id", name="Filtered Device")
        registry.async_get_device.return_value = stale_candidate

        # Device B is always cloud-present but filtered out from coordinator.devices.
        mock_lipro_api_client.get_device_list.side_effect = [
            {
                "devices": [
                    _make_api_device(serial="03ab5ccd7c000001"),
                    _make_api_device(serial="03ab5ccd7c000002"),
                ]
            },
            {
                "devices": [
                    _make_api_device(serial="03ab5ccd7c000001"),
                    _make_api_device(serial="03ab5ccd7c000002"),
                ]
            },
            {
                "devices": [
                    _make_api_device(serial="03ab5ccd7c000001"),
                    _make_api_device(serial="03ab5ccd7c000002"),
                ]
            },
            {
                "devices": [
                    _make_api_device(serial="03ab5ccd7c000001"),
                    _make_api_device(serial="03ab5ccd7c000002"),
                ]
            },
        ]

        with (
            patch(
                "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
            ) as mock_share,
            patch(
                "custom_components.lipro.core.coordinator.device_refresh.dr.async_get"
            ) as dr_get,
        ):
            mock_share.return_value = MagicMock(is_enabled=False)
            dr_get.return_value = registry
            await coordinator._fetch_devices()
            await coordinator._fetch_devices()
            await coordinator._fetch_devices()
            await coordinator._fetch_devices()

        registry.async_remove_device.assert_not_called()

    @pytest.mark.asyncio
    async def test_stale_reconcile_bootstraps_from_registry_on_cold_start(
        self, coordinator, mock_lipro_api_client
    ):
        """Cold start with empty cloud list should eventually remove orphan registry devices."""
        device_registry = dr.async_get(coordinator.hass)
        stale_serial = "03ab5ccd7cdead01"
        stale_entry = device_registry.async_get_or_create(
            config_entry_id=coordinator.config_entry.entry_id,
            identifiers={(DOMAIN, stale_serial)},
            manufacturer="Lipro",
            name="Orphan Device",
        )
        assert (
            device_registry.async_get_device(identifiers={(DOMAIN, stale_serial)})
            == stale_entry
        )

        mock_lipro_api_client.get_device_list.side_effect = [
            {"devices": []},
            {"devices": []},
            {"devices": []},
        ]

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._fetch_devices()
            await coordinator._fetch_devices()
            await coordinator._fetch_devices()

        assert (
            device_registry.async_get_device(identifiers={(DOMAIN, stale_serial)})
            is None
        )


# =========================================================================
# 3. Error handling — each Lipro error maps to the correct HA exception
# =========================================================================


class TestCoordinatorErrorHandling:
    """Test _async_update_data error-to-HA-exception mapping."""

    @pytest.mark.asyncio
    async def test_refresh_token_expired_raises_config_entry_auth_failed(
        self, coordinator, mock_auth_manager
    ):
        """LiproRefreshTokenExpiredError -> ConfigEntryAuthFailed."""
        mock_auth_manager.ensure_valid_token.side_effect = (
            LiproRefreshTokenExpiredError("expired")
        )
        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_auth_error_raises_config_entry_auth_failed(
        self, coordinator, mock_auth_manager
    ):
        """LiproAuthError -> ConfigEntryAuthFailed."""
        mock_auth_manager.ensure_valid_token.side_effect = LiproAuthError("bad token")
        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_connection_error_raises_update_failed(
        self, coordinator, mock_auth_manager
    ):
        """LiproConnectionError -> UpdateFailed."""
        mock_auth_manager.ensure_valid_token.side_effect = LiproConnectionError(
            "timeout"
        )
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_api_error_raises_update_failed(
        self, coordinator, mock_lipro_api_client
    ):
        """LiproApiError during device fetch -> UpdateFailed."""
        mock_lipro_api_client.get_device_list.side_effect = LiproApiError("server error")
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_auth_error_during_fetch_raises_config_entry_auth_failed(
        self, coordinator, mock_lipro_api_client
    ):
        """LiproAuthError during get_devices -> ConfigEntryAuthFailed."""
        mock_lipro_api_client.get_device_list.side_effect = LiproAuthError("unauthorized")
        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_connection_error_during_status_query_raises_update_failed(
        self, coordinator, mock_lipro_api_client
    ):
        """LiproConnectionError during status query should fail the update."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [_make_api_device(serial="03ab5ccd7c000001")]
        }
        mock_lipro_api_client.get_product_configs.return_value = []
        mock_lipro_api_client.query_device_status.side_effect = LiproConnectionError(
            "timeout"
        )
        mock_lipro_api_client.query_connect_status.return_value = {}

        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_auth_error_during_connect_status_raises_config_entry_auth_failed(
        self, coordinator, mock_lipro_api_client
    ):
        """LiproAuthError during connect-status query should trigger reauth."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [_make_api_device(serial="03ab5ccd7c000001")]
        }
        mock_lipro_api_client.get_product_configs.return_value = []
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.side_effect = LiproAuthError(
            "unauthorized"
        )

        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()

    @pytest.mark.asyncio
    async def test_auth_error_during_outlet_power_query_raises_config_entry_auth_failed(
        self, coordinator, mock_lipro_api_client
    ):
        """LiproAuthError during outlet power query should trigger reauth."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [
                _make_api_device(
                    serial="03ab5ccd7c000001",
                    physical_model="outlet",
                    device_type=6,
                )
            ]
        }
        mock_lipro_api_client.get_product_configs.return_value = []
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}
        mock_lipro_api_client.fetch_outlet_power_info.side_effect = LiproAuthError(
            "unauthorized"
        )

        with pytest.raises(ConfigEntryAuthFailed):
            await coordinator._async_update_data()


# =========================================================================
# 4. _load_product_configs — color temp ranges applied to devices
# =========================================================================


class TestCoordinatorProductConfigs:
    """Test _load_product_configs applies color temp and fan gear ranges."""

    @pytest.mark.asyncio
    async def test_color_temp_range_applied_by_iot_name(
        self, coordinator, mock_lipro_api_client
    ):
        """Product config matched by iotName sets min/max color temp."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [
                _make_api_device(
                    serial="03ab5ccd7c000001",
                    iot_name="lipro_led",
                ),
            ]
        }
        mock_lipro_api_client.get_product_configs.return_value = [
            {
                "id": 99,
                "fwIotName": "lipro_led",
                "name": "LED Panel",
                "minTemperature": 3000,
                "maxTemperature": 5700,
            }
        ]
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()

        device = coordinator.devices["03ab5ccd7c000001"]
        assert device.min_color_temp_kelvin == 3000
        assert device.max_color_temp_kelvin == 5700

    @pytest.mark.asyncio
    async def test_color_temp_range_applied_by_product_id(
        self, coordinator, mock_lipro_api_client
    ):
        """Product config matched by productId takes priority over iotName."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [
                _make_api_device(
                    serial="03ab5ccd7c000001",
                    iot_name="lipro_led",
                    product_id=42,
                ),
            ]
        }
        mock_lipro_api_client.get_product_configs.return_value = [
            {
                "id": 42,
                "fwIotName": "lipro_led",
                "name": "LED Panel v2",
                "minTemperature": 2700,
                "maxTemperature": 6500,
            },
            {
                "id": 99,
                "fwIotName": "lipro_led",
                "name": "LED Panel v1",
                "minTemperature": 3000,
                "maxTemperature": 5000,
            },
        ]
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()

        device = coordinator.devices["03ab5ccd7c000001"]
        # productId=42 matches config id=42 (priority 1)
        assert device.min_color_temp_kelvin == 2700
        assert device.max_color_temp_kelvin == 6500

    @pytest.mark.asyncio
    async def test_single_color_temp_device(self, coordinator, mock_lipro_api_client):
        """maxTemperature=0 means single color temp (no adjustment)."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [
                _make_api_device(serial="03ab5ccd7c000001", iot_name="lipro_led"),
            ]
        }
        mock_lipro_api_client.get_product_configs.return_value = [
            {
                "id": 1,
                "fwIotName": "lipro_led",
                "name": "Single Color",
                "minTemperature": 0,
                "maxTemperature": 0,
            }
        ]
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()

        device = coordinator.devices["03ab5ccd7c000001"]
        assert device.min_color_temp_kelvin == 0
        assert device.max_color_temp_kelvin == 0
        assert device.supports_color_temp is False

    @pytest.mark.asyncio
    async def test_fan_gear_range_applied(self, coordinator, mock_lipro_api_client):
        """maxFanGear from product config is applied to the device."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [
                _make_api_device(
                    serial="03ab5ccd7c000001",
                    iot_name="lipro_fan_light",
                    physical_model="fanLight",
                ),
            ]
        }
        mock_lipro_api_client.get_product_configs.return_value = [
            {
                "id": 1,
                "fwIotName": "lipro_fan_light",
                "name": "Fan Light",
                "minTemperature": 2700,
                "maxTemperature": 6500,
                "maxFanGear": 8,
            }
        ]
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()

        device = coordinator.devices["03ab5ccd7c000001"]
        assert device.default_max_fan_gear_in_model == 8
        assert device.max_fan_gear == 8

    @pytest.mark.asyncio
    async def test_fan_gear_range_uses_model_default_when_product_max_missing(
        self, coordinator, mock_lipro_api_client
    ):
        """None maxFanGear should keep model default upper-bound."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [
                _make_api_device(
                    serial="03ab5ccd7c000001",
                    iot_name="21F1",
                    physical_model="fanLight",
                ),
            ]
        }
        mock_lipro_api_client.get_product_configs.return_value = [
            {
                "id": 1,
                "fwIotName": "21F1",
                "name": "Fan Light",
                "minTemperature": 2700,
                "maxTemperature": 6500,
                "maxFanGear": None,
            }
        ]
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()

        device = coordinator.devices["03ab5ccd7c000001"]
        assert device.default_max_fan_gear_in_model == 10
        assert device.max_fan_gear == 10

    @pytest.mark.asyncio
    async def test_fan_gear_range_adapts_when_product_max_missing(
        self, coordinator, mock_lipro_api_client
    ):
        """When maxFanGear is missing, runtime fanGear should adapt upper-bound."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [
                _make_api_device(
                    serial="03ab5ccd7c000001",
                    iot_name="fan_unknown_model",
                    physical_model="fanLight",
                ),
            ]
        }
        mock_lipro_api_client.get_product_configs.return_value = [
            {
                "id": 1,
                "fwIotName": "fan_unknown_model",
                "name": "Fan Light",
                "minTemperature": 2700,
                "maxTemperature": 6500,
                "maxFanGear": None,
            }
        ]
        mock_lipro_api_client.query_device_status.return_value = [
            {
                "deviceId": "03ab5ccd7c000001",
                "properties": [{"key": "fanGear", "value": "10"}],
            }
        ]
        mock_lipro_api_client.query_connect_status.return_value = {
            "03ab5ccd7c000001": True
        }

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()

        device = coordinator.devices["03ab5ccd7c000001"]
        assert device.default_max_fan_gear_in_model == 6
        assert device.max_fan_gear == 10

    @pytest.mark.asyncio
    async def test_cached_product_config_reapplied_after_full_device_refresh(
        self, coordinator, mock_lipro_api_client
    ):
        """Cached product config should be reapplied to replaced device objects."""
        serial = "03ab5ccd7c000001"
        mock_lipro_api_client.get_device_list.side_effect = [
            {"devices": [_make_api_device(serial=serial, iot_name="lipro_led")]},
            {"devices": [_make_api_device(serial=serial, iot_name="lipro_led")]},
        ]
        mock_lipro_api_client.get_product_configs.return_value = [
            {
                "id": 99,
                "fwIotName": "lipro_led",
                "name": "LED Panel",
                "minTemperature": 3011,
                "maxTemperature": 5733,
            }
        ]
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()
            first_device = coordinator.devices[serial]
            assert first_device.min_color_temp_kelvin == 3011
            assert first_device.max_color_temp_kelvin == 5733
            mock_lipro_api_client.get_product_configs.reset_mock()

            coordinator._force_device_refresh = True
            await coordinator._async_update_data()

        second_device = coordinator.devices[serial]
        assert second_device is not first_device
        assert second_device.min_color_temp_kelvin == 3011
        assert second_device.max_color_temp_kelvin == 5733
        mock_lipro_api_client.get_product_configs.assert_not_called()

    @pytest.mark.asyncio
    async def test_product_config_api_error_is_non_fatal(
        self, coordinator, mock_lipro_api_client
    ):
        """LiproApiError from get_product_configs should not abort the update."""
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [_make_api_device(serial="03ab5ccd7c000001")]
        }
        mock_lipro_api_client.get_product_configs.side_effect = LiproApiError(
            "server error"
        )
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            result = await coordinator._async_update_data()

        # Update should still succeed with default color temp values
        assert "03ab5ccd7c000001" in result


# =========================================================================
# 5. async_shutdown — clears data, stops MQTT, closes client
# =========================================================================


class TestCoordinatorShutdown:
    """Test async_shutdown releases all resources."""

    @pytest.mark.asyncio
    async def test_shutdown_clears_devices(self, coordinator, mock_lipro_api_client):
        """After shutdown, _devices and related dicts must be empty."""
        # Populate some devices first
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [_make_api_device(serial="03ab5ccd7c000001")]
        }
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(
                is_enabled=False, submit_report=AsyncMock()
            )
            await coordinator._async_update_data()
            assert len(coordinator.devices) == 1

            await coordinator.async_shutdown()

        assert len(coordinator._devices) == 0
        assert len(coordinator._device_identity_index.mapping) == 0
        assert len(coordinator._entities) == 0
        assert len(coordinator._entities_by_device) == 0
        assert len(coordinator._product_configs) == 0
        assert len(coordinator._mqtt_message_cache) == 0

    @pytest.mark.asyncio
    async def test_shutdown_closes_client(self, coordinator, mock_lipro_api_client):
        """async_shutdown must call client.close()."""
        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(
                is_enabled=False, submit_report=AsyncMock()
            )
            await coordinator.async_shutdown()

        mock_lipro_api_client.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_shutdown_stops_mqtt(self, coordinator, mock_lipro_api_client):
        """async_shutdown must stop the MQTT client if one exists."""
        mock_mqtt = AsyncMock()
        coordinator._mqtt_client = mock_mqtt

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(
                is_enabled=False, submit_report=AsyncMock()
            )
            await coordinator.async_shutdown()

        mock_mqtt.stop.assert_awaited_once()
        assert coordinator._mqtt_client is None
        assert coordinator._mqtt_connected is False


# =========================================================================
# 6. async_refresh_devices — sets force flag
# =========================================================================


class TestCoordinatorRefreshDevices:
    """Test async_refresh_devices sets the force-refresh flag."""

    @pytest.mark.asyncio
    async def test_sets_force_flag_and_clears_product_configs(
        self, coordinator, mock_lipro_api_client
    ):
        """async_refresh_devices should set _force_device_refresh and clear configs."""
        # Pre-populate product configs cache
        coordinator._product_configs = {"lipro_led": {"id": 1}}

        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [_make_api_device(serial="03ab5ccd7c000001")]
        }
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}
        mock_lipro_api_client.get_product_configs.return_value = []

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator.async_refresh_devices()

        # After refresh, product configs should have been cleared (then reloaded)
        # and get_devices should have been called because the flag was set
        mock_lipro_api_client.get_device_list.assert_called()

    @pytest.mark.asyncio
    async def test_force_flag_causes_device_refetch(
        self, coordinator, mock_lipro_api_client
    ):
        """Setting _force_device_refresh=True causes _fetch_devices on next update."""
        # First update populates devices
        mock_lipro_api_client.get_device_list.return_value = {
            "devices": [_make_api_device(serial="03ab5ccd7c000001")]
        }
        mock_lipro_api_client.query_device_status.return_value = []
        mock_lipro_api_client.query_connect_status.return_value = {}
        mock_lipro_api_client.get_product_configs.return_value = []

        with patch(
            "custom_components.lipro.core.anonymous_share.get_anonymous_share_manager"
        ) as mock_share:
            mock_share.return_value = MagicMock(is_enabled=False)
            await coordinator._async_update_data()
            mock_lipro_api_client.get_device_list.reset_mock()

            # Set force flag manually
            coordinator._force_device_refresh = True
            coordinator._product_configs.clear()
            await coordinator._async_update_data()

        # get_devices should be called again because of the force flag
        mock_lipro_api_client.get_device_list.assert_called_once()
