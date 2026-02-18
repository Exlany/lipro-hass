"""Fixtures for Lipro tests.

This module provides pytest fixtures for testing the Lipro integration.
Requires pytest-homeassistant-custom-component to be installed.

To install:
    pip install pytest-homeassistant-custom-component

Note: On Windows, this may require Microsoft C++ Build Tools.
"""

from __future__ import annotations

from collections.abc import Generator
import pathlib
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry  # noqa: F401

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
        properties: dict | None = None,
        extra_data: dict | None = None,
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
    """Create a mock LiproDataUpdateCoordinator for testing."""
    coordinator = MagicMock()
    coordinator.devices = {}
    coordinator.last_update_success = True
    coordinator.async_send_command = AsyncMock(return_value=True)
    coordinator.async_request_refresh = AsyncMock()
    coordinator.register_entity = MagicMock()
    coordinator.unregister_entity = MagicMock()
    coordinator.get_device = MagicMock(side_effect=coordinator.devices.get)
    return coordinator


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: None,
) -> Generator[None]:
    """Enable custom integrations for all tests."""
    import custom_components

    # Filter out editable-install placeholder paths that are not real directories.
    # These are injected by setuptools editable installs and cause HA loader to crash
    # when it tries to call pathlib.Path(path).iterdir() on them.
    real_paths = [p for p in custom_components.__path__ if pathlib.Path(p).is_dir()]
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
    """Create a mock LiproClient."""
    with patch(
        "custom_components.lipro.config_flow.LiproClient",
        autospec=True,
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        # config_flow uses login_with_hash, not login
        mock_client.login_with_hash = AsyncMock(
            return_value={
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "user_id": 10001,
                "biz_id": "test_biz_id",
            }
        )
        yield mock_client


@pytest.fixture
def mock_lipro_client_auth_error() -> Generator[MagicMock]:
    """Create a mock LiproClient that raises auth error."""
    with patch(
        "custom_components.lipro.config_flow.LiproClient",
        autospec=True,
    ) as mock_client_class:
        from custom_components.lipro.core.api import LiproAuthError

        mock_client = mock_client_class.return_value
        mock_client.login_with_hash = AsyncMock(
            side_effect=LiproAuthError("Invalid credentials")
        )
        yield mock_client


@pytest.fixture
def mock_lipro_client_connection_error() -> Generator[MagicMock]:
    """Create a mock LiproClient that raises connection error."""
    with patch(
        "custom_components.lipro.config_flow.LiproClient",
        autospec=True,
    ) as mock_client_class:
        from custom_components.lipro.core.api import LiproConnectionError

        mock_client = mock_client_class.return_value
        mock_client.login_with_hash = AsyncMock(
            side_effect=LiproConnectionError("Connection failed")
        )
        yield mock_client
