"""Fixtures for Lipro tests.

This module provides pytest fixtures for testing the Lipro integration.
Requires pytest-homeassistant-custom-component to be installed.

To install:
    uv add --dev pytest-homeassistant-custom-component

Note: On Windows, this may require Microsoft C++ Build Tools.
"""

from __future__ import annotations

from collections.abc import Generator
import pathlib
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry  # noqa: F401

from tests import topicized_collection as _topicized_collection
from tests.coordinator_double import _CoordinatorDouble

pytest_ignore_collect = _topicized_collection.pytest_ignore_collect
pytest_collection_modifyitems = _topicized_collection.pytest_collection_modifyitems


# Domain constant

DOMAIN = "lipro"
# =========================================================================
# Device type defaults for make_device fixture
# =========================================================================

_DEVICE_TYPE_DEFAULTS: dict[str, dict[str, Any]] = {
    "light": {
        "device_type": 1,
        "iot_name": "lipro_led",
        "physical_model": "light",
    },
    "fanLight": {
        "device_type": 1,
        "iot_name": "lipro_fan_light",
        "physical_model": "fanLight",
    },
    "switch": {
        "device_type": 3,
        "iot_name": "lipro_switch",
        "physical_model": "switch",
    },
    "outlet": {
        "device_type": 6,
        "iot_name": "lipro_outlet",
        "physical_model": "outlet",
    },
    "heater": {
        "device_type": 7,
        "iot_name": "lipro_heater",
        "physical_model": "heater",
    },
    "curtain": {
        "device_type": 4,
        "iot_name": "lipro_curtain",
        "physical_model": "curtain",
    },
    "bodySensor": {
        "device_type": 10,
        "iot_name": "lipro_body_sensor",
        "physical_model": "bodySensor",
    },
    "doorSensor": {
        "device_type": 11,
        "iot_name": "lipro_door_sensor",
        "physical_model": "doorSensor",
    },
}


@pytest.fixture
def make_device():
    """Factory fixture to create LiproDevice instances for testing.

    Usage:
        device = make_device("light", properties={"powerState": "1"})
        device = make_device("outlet", name="My Outlet", serial="03ab5ccd7c999999")
    """

    def _make(
        kind: str = "light",
        *,
        device_number: int = 1,
        serial: str = "03ab5ccd7cxxxxxx",
        name: str | None = None,
        properties: dict[str, Any] | None = None,
        extra_data: dict[str, Any] | None = None,
        **overrides: Any,
    ) -> Any:
        from custom_components.lipro.core.device import LiproDevice

        defaults = _DEVICE_TYPE_DEFAULTS.get(kind, _DEVICE_TYPE_DEFAULTS["light"])
        return LiproDevice(
            device_number=device_number,
            serial=serial,
            name=name or f"Test {kind.capitalize()}",
            device_type=overrides.pop("device_type", defaults["device_type"]),
            iot_name=overrides.pop("iot_name", defaults["iot_name"]),
            physical_model=overrides.pop("physical_model", defaults["physical_model"]),
            properties=properties or {},
            extra_data=extra_data or {},
            **overrides,
        )

    return _make


@pytest.fixture
def mock_coordinator():
    """Create a coordinator double for testing."""
    return _CoordinatorDouble()


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None]:
    """Enable custom integrations for all tests."""
    import custom_components

    repo_custom_components = (
        pathlib.Path(__file__).resolve().parents[1] / "custom_components"
    )

    # Filter out editable-install placeholder paths that are not real directories.
    # These are injected by setuptools editable installs and cause HA loader to crash
    # when it tries to call pathlib.Path(path).iterdir() on them.
    real_paths = [p for p in custom_components.__path__ if pathlib.Path(p).is_dir()]
    if repo_custom_components.is_dir():
        real_paths.append(str(repo_custom_components))
    with patch.object(custom_components, "__path__", real_paths):
        yield


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "custom_components.lipro.async_setup_entry",
        return_value=True,
    ) as mock_setup:
        yield mock_setup


@pytest.fixture
def mock_lipro_client() -> Generator[MagicMock]:
    """Create a mock Lipro protocol facade."""
    with patch(
        "custom_components.lipro.config_flow.LiproProtocolFacade",
        autospec=True,
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        # config_flow always uses login(..., password_is_hashed=True)
        mock_client.login = AsyncMock(
            return_value={
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "user_id": 10001,
                "biz_id": "test_biz_id",
            }
        )
        yield mock_client


@pytest.fixture
def mock_lipro_api_client():
    """Create a mock Lipro protocol facade with common API responses for coordinator tests."""
    from custom_components.lipro.core.protocol import CanonicalProtocolContracts

    client = AsyncMock()
    client.get_devices = AsyncMock(return_value={"devices": [], "total": 0})
    client.query_device_status = AsyncMock(return_value=[])
    client.query_mesh_group_status = AsyncMock(return_value=[])
    client.query_connect_status = AsyncMock(return_value={})
    client.get_mqtt_config = AsyncMock(return_value={})
    client.get_product_configs = AsyncMock(return_value=[])
    client.send_command = AsyncMock(
        return_value={"pushSuccess": True, "msgSn": "test-msg-sn"}
    )
    client.send_group_command = AsyncMock(
        return_value={"pushSuccess": True, "msgSn": "test-group-msg-sn"}
    )
    client.query_command_result = AsyncMock(
        return_value={"code": "0000", "message": "success", "success": True}
    )
    client.fetch_outlet_power_info = AsyncMock(return_value={})
    client.close = AsyncMock()
    client.access_token = "test_token"
    client.refresh_token = "test_refresh"
    client.user_id = 10001
    client.phone_id = "test_phone_id"
    client.contracts = CanonicalProtocolContracts()

    mock_mqtt_facade = MagicMock()
    mock_mqtt_facade.start = AsyncMock()
    mock_mqtt_facade.stop = AsyncMock()
    mock_mqtt_facade.sync_subscriptions = AsyncMock()
    mock_mqtt_facade.wait_until_connected = AsyncMock(return_value=True)
    mock_mqtt_facade.is_connected = True
    mock_mqtt_facade.subscribed_devices = set()
    mock_mqtt_facade.subscribed_count = 0
    mock_mqtt_facade.last_error = None
    client.build_mqtt_facade = MagicMock(return_value=mock_mqtt_facade)
    client.attach_mqtt_facade = MagicMock()
    return client


@pytest.fixture
def mock_auth_manager():
    """Create a mock LiproAuthManager for coordinator tests."""
    auth = AsyncMock()
    auth.ensure_valid_token = AsyncMock()
    auth.is_authenticated = True
    return auth


@pytest.fixture
def mock_lipro_client_auth_error() -> Generator[MagicMock]:
    """Create a mock protocol facade that raises auth error."""
    with patch(
        "custom_components.lipro.config_flow.LiproProtocolFacade",
        autospec=True,
    ) as mock_client_class:
        from custom_components.lipro.core.api import LiproAuthError

        mock_client = mock_client_class.return_value
        mock_client.login = AsyncMock(side_effect=LiproAuthError("Invalid credentials"))
        yield mock_client


@pytest.fixture
def mock_lipro_client_connection_error() -> Generator[MagicMock]:
    """Create a mock protocol facade that raises connection error."""
    with patch(
        "custom_components.lipro.config_flow.LiproProtocolFacade",
        autospec=True,
    ) as mock_client_class:
        from custom_components.lipro.core.api import LiproConnectionError

        mock_client = mock_client_class.return_value
        mock_client.login = AsyncMock(
            side_effect=LiproConnectionError("Connection failed")
        )
        yield mock_client
