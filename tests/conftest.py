"""Fixtures for Lipro tests.

This module provides pytest fixtures for testing the Lipro integration.

There are two testing modes:
1. Standalone mode (default): Uses mocked homeassistant modules for testing
   core modules (api, auth, device, mqtt) without requiring Home Assistant.
2. Full HA mode: Requires pytest-homeassistant-custom-component for testing
   config_flow, coordinator, and platform integrations.

To install full HA test environment:
    pip install pytest-homeassistant-custom-component

Note: On Windows, this may require Microsoft C++ Build Tools.
"""

from __future__ import annotations

from collections.abc import Generator
import sys
from types import ModuleType
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Domain constant (avoid importing from main module which requires HA)
DOMAIN = "lipro"

# Check if pytest-homeassistant-custom-component is available
try:
    from pytest_homeassistant_custom_component.common import (
        MockConfigEntry,  # noqa: F401
    )

    HAS_HA_TEST_ENV = True
except ImportError:
    HAS_HA_TEST_ENV = False


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
        device_id: int = 1,
        serial: str = "03ab5ccd7cxxxxxx",
        name: str | None = None,
        properties: dict | None = None,
        extra_data: dict | None = None,
        **overrides: Any,
    ) -> Any:
        from custom_components.lipro.core.device import LiproDevice

        defaults = _DEVICE_TYPE_DEFAULTS.get(kind, _DEVICE_TYPE_DEFAULTS["light"])
        return LiproDevice(
            device_id=device_id,
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
    coordinator.get_device = MagicMock(side_effect=lambda s: coordinator.devices.get(s))
    return coordinator


def _create_mock_module(name: str) -> ModuleType:
    """Create a mock module."""
    module = ModuleType(name)
    module.__dict__.update(MagicMock().__dict__)
    return module


def pytest_configure(config):
    """Configure pytest to handle missing homeassistant module.

    This creates mock modules for homeassistant when running in standalone mode.
    When pytest-homeassistant-custom-component is installed, this is skipped.
    """
    # Register custom markers
    config.addinivalue_line(
        "markers", "github: tests specifically for GitHub Actions CI"
    )
    config.addinivalue_line("markers", "integration: tests requiring external services")
    config.addinivalue_line("markers", "slow: tests that take longer to run")

    if HAS_HA_TEST_ENV:
        # Full HA test environment available, no mocking needed
        return

    # Create mock homeassistant module for tests that don't need it
    if "homeassistant" not in sys.modules:
        # Create base modules as proper ModuleType objects
        mock_ha = _create_mock_module("homeassistant")
        mock_helpers = _create_mock_module("homeassistant.helpers")
        mock_components = _create_mock_module("homeassistant.components")

        # Set up const with required attributes
        mock_const = MagicMock()
        mock_const.CONF_PASSWORD = "password"
        mock_const.ATTR_ENTITY_ID = "entity_id"
        mock_const.Platform = MagicMock()

        # Register base modules
        sys.modules["homeassistant"] = mock_ha
        sys.modules["homeassistant.core"] = MagicMock()
        sys.modules["homeassistant.config_entries"] = MagicMock()
        sys.modules["homeassistant.const"] = mock_const
        sys.modules["homeassistant.exceptions"] = MagicMock()

        # Register helpers as a proper module with submodules
        sys.modules["homeassistant.helpers"] = mock_helpers
        sys.modules["homeassistant.helpers.aiohttp_client"] = MagicMock()
        sys.modules["homeassistant.helpers.config_validation"] = MagicMock()
        sys.modules["homeassistant.helpers.entity_registry"] = MagicMock()
        sys.modules["homeassistant.helpers.update_coordinator"] = MagicMock()
        sys.modules["homeassistant.helpers.debounce"] = MagicMock()
        sys.modules["homeassistant.helpers.device_registry"] = MagicMock()
        sys.modules["homeassistant.helpers.entity"] = MagicMock()
        sys.modules["homeassistant.helpers.entity_platform"] = MagicMock()
        sys.modules["homeassistant.helpers.translation"] = MagicMock()

        # Register components as a proper module with submodules
        sys.modules["homeassistant.components"] = mock_components
        sys.modules["homeassistant.components.persistent_notification"] = MagicMock()
        sys.modules["homeassistant.components.light"] = MagicMock()
        sys.modules["homeassistant.components.switch"] = MagicMock()
        sys.modules["homeassistant.components.cover"] = MagicMock()
        sys.modules["homeassistant.components.fan"] = MagicMock()
        sys.modules["homeassistant.components.climate"] = MagicMock()
        sys.modules["homeassistant.components.sensor"] = MagicMock()
        sys.modules["homeassistant.components.binary_sensor"] = MagicMock()
        sys.modules["homeassistant.components.select"] = MagicMock()
        sys.modules["homeassistant.components.diagnostics"] = MagicMock()

        # Register data_entry_flow module
        mock_data_entry_flow = MagicMock()
        mock_data_entry_flow.FlowResultType = MagicMock()
        sys.modules["homeassistant.data_entry_flow"] = mock_data_entry_flow


# Fixture to enable custom integrations (only used with full HA test env)
if HAS_HA_TEST_ENV:

    @pytest.fixture(autouse=True)
    def auto_enable_custom_integrations(
        enable_custom_integrations: None,
    ) -> Generator[None, None, None]:
        """Enable custom integrations for all tests."""
        return


# Fixtures for config_flow tests (require pytest-homeassistant-custom-component)


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock, None, None]:
    """Override async_setup_entry."""
    with patch(
        "custom_components.lipro.async_setup_entry",
        return_value=True,
    ) as mock_setup:
        yield mock_setup


@pytest.fixture
def mock_lipro_client() -> Generator[MagicMock, None, None]:
    """Create a mock LiproClient."""
    with patch(
        "custom_components.lipro.config_flow.LiproClient",
        autospec=True,
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.login = AsyncMock(
            return_value={
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "user_id": 10001,
            }
        )
        yield mock_client


@pytest.fixture
def mock_lipro_client_auth_error() -> Generator[MagicMock, None, None]:
    """Create a mock LiproClient that raises auth error."""
    with patch(
        "custom_components.lipro.config_flow.LiproClient",
        autospec=True,
    ) as mock_client_class:
        from custom_components.lipro.core.api import LiproAuthError

        mock_client = mock_client_class.return_value
        mock_client.login = AsyncMock(side_effect=LiproAuthError("Invalid credentials"))
        yield mock_client


@pytest.fixture
def mock_lipro_client_connection_error() -> Generator[MagicMock, None, None]:
    """Create a mock LiproClient that raises connection error."""
    with patch(
        "custom_components.lipro.config_flow.LiproClient",
        autospec=True,
    ) as mock_client_class:
        from custom_components.lipro.core.api import LiproConnectionError

        mock_client = mock_client_class.return_value
        mock_client.login = AsyncMock(
            side_effect=LiproConnectionError("Connection failed")
        )
        yield mock_client
