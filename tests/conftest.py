"""Fixtures for Lipro tests.

This module provides pytest fixtures for testing the Lipro integration.
Requires pytest-homeassistant-custom-component to be installed.

To install:
    pip install pytest-homeassistant-custom-component

Note: On Windows, this may require Microsoft C++ Build Tools.
"""

from __future__ import annotations

import asyncio
from collections.abc import Generator, Mapping
from datetime import timedelta
import pathlib
from types import MappingProxyType
from typing import TYPE_CHECKING, Any
from unittest.mock import DEFAULT, AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry  # noqa: F401

if TYPE_CHECKING:
    from custom_components.lipro.core.device import LiproDevice

# Domain constant

DOMAIN = "lipro"
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_TOPICIZED_THIN_SHELLS = {
    "tests/core/test_share_client.py": {
        "tests/core/test_share_client_primitives.py",
        "tests/core/test_share_client_refresh.py",
        "tests/core/test_share_client_submit.py",
        "tests/core/test_share_client_boundary.py",
    },
    "tests/core/api/test_api_command_surface_responses.py": {
        "tests/core/api/test_api_command_surface_responses_errors.py",
        "tests/core/api/test_api_command_surface_responses_iot.py",
        "tests/core/api/test_api_command_surface_responses_success.py",
    },
    "tests/core/api/test_api_device_surface.py": {
        "tests/core/api/test_api_device_surface_connect_status.py",
        "tests/core/api/test_api_device_surface_devices.py",
        "tests/core/api/test_api_device_surface_mesh_groups.py",
        "tests/core/api/test_api_device_surface_optional_capabilities.py",
        "tests/core/api/test_api_device_surface_outlet_power.py",
        "tests/core/api/test_api_device_surface_status.py",
    },
    "tests/core/api/test_api_status_service.py": {
        "tests/core/api/test_api_status_service_fallback.py",
        "tests/core/api/test_api_status_service_wrappers.py",
    },
    "tests/core/api/test_api_transport_and_schedule.py": {
        "tests/core/api/test_api_transport_and_schedule_close.py",
        "tests/core/api/test_api_transport_and_schedule_mqtt.py",
        "tests/core/api/test_api_transport_and_schedule_schedules.py",
        "tests/core/api/test_api_transport_and_schedule_transport_boundary.py",
    },
    "tests/core/coordinator/runtime/test_command_runtime.py": {
        "tests/core/coordinator/runtime/test_command_runtime_builder_retry.py",
        "tests/core/coordinator/runtime/test_command_runtime_sender.py",
        "tests/core/coordinator/runtime/test_command_runtime_confirmation.py",
        "tests/core/coordinator/runtime/test_command_runtime_orchestration.py",
    },
    "tests/core/coordinator/runtime/test_mqtt_runtime.py": {
        "tests/core/coordinator/runtime/test_mqtt_runtime_connection.py",
        "tests/core/coordinator/runtime/test_mqtt_runtime_init.py",
        "tests/core/coordinator/runtime/test_mqtt_runtime_messages.py",
        "tests/core/coordinator/runtime/test_mqtt_runtime_notifications.py",
    },
    "tests/meta/test_dependency_guards.py": {
        "tests/meta/dependency_guards_policy.py",
        "tests/meta/dependency_guards_protocol_contracts.py",
        "tests/meta/dependency_guards_review_ledgers.py",
        "tests/meta/dependency_guards_service_runtime.py",
    },
    "tests/meta/test_governance_followup_route.py": {
        "tests/meta/governance_followup_route_closeouts.py",
        "tests/meta/governance_followup_route_continuation.py",
        "tests/meta/governance_followup_route_current_milestones.py",
    },
    "tests/meta/test_governance_milestone_archives.py": {
        "tests/meta/governance_milestone_archives_assets.py",
        "tests/meta/governance_milestone_archives_ordering.py",
        "tests/meta/governance_milestone_archives_truth.py",
    },
    "tests/meta/test_governance_phase_history.py": {
        "tests/meta/governance_phase_history_archive_execution.py",
        "tests/meta/governance_phase_history_current_milestones.py",
        "tests/meta/governance_phase_history_mid_closeouts.py",
    },
    "tests/meta/test_governance_phase_history_topology.py": {
        "tests/meta/governance_phase_history_topology_closeouts.py",
        "tests/meta/governance_phase_history_topology_execution.py",
        "tests/meta/governance_phase_history_topology_foundations.py",
    },
    "tests/meta/test_public_surface_guards.py": {
        "tests/meta/public_surface_architecture_policy.py",
        "tests/meta/public_surface_phase_notes.py",
        "tests/meta/public_surface_runtime_contracts.py",
    },
    "tests/meta/test_toolchain_truth.py": {
        "tests/meta/toolchain_truth_checker_paths.py",
        "tests/meta/toolchain_truth_ci_contract.py",
        "tests/meta/toolchain_truth_docs_fast_path.py",
        "tests/meta/toolchain_truth_python_stack.py",
        "tests/meta/toolchain_truth_release_contract.py",
        "tests/meta/toolchain_truth_testing_governance.py",
    },
    "tests/platforms/test_light_entity_behavior.py": {
        "tests/platforms/test_light_entity_additional_coverage.py",
        "tests/platforms/test_light_entity_commands.py",
        "tests/platforms/test_light_entity_properties.py",
    },
    "tests/platforms/test_select_behavior.py": {
        "tests/platforms/select_gear_behavior_cases.py",
        "tests/platforms/select_mapped_behavior_cases.py",
        "tests/platforms/select_setup_behavior_cases.py",
    },
    "tests/services/test_services_diagnostics.py": {
        "tests/services/test_services_diagnostics_capabilities.py",
        "tests/services/test_services_diagnostics_feedback.py",
        "tests/services/test_services_diagnostics_payloads.py",
    },
}


def _normalize_pytest_target(raw: str) -> str:
    candidate = raw.split("::", 1)[0]
    if not candidate or candidate.startswith("-"):
        return ""
    path = pathlib.Path(candidate)
    try:
        return path.resolve().relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        return candidate.lstrip("./")


def pytest_ignore_collect(collection_path: pathlib.Path, config: pytest.Config) -> bool:
    """Keep thin-shell suites runnable by path without duplicating full-suite collection."""
    try:
        relative_path = collection_path.resolve().relative_to(_REPO_ROOT).as_posix()
    except ValueError:
        return False

    if relative_path not in _TOPICIZED_THIN_SHELLS:
        return False

    explicit_targets = {
        normalized
        for normalized in (_normalize_pytest_target(arg) for arg in config.args)
        if normalized
    }
    if relative_path not in explicit_targets:
        return True

    sibling_topics = _TOPICIZED_THIN_SHELLS[relative_path]
    return any(topic in explicit_targets for topic in sibling_topics)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Drop thin-shell items when their topical siblings are explicitly collected together."""
    explicit_targets = {
        normalized
        for normalized in (_normalize_pytest_target(arg) for arg in config.args)
        if normalized
    }
    if not explicit_targets:
        return

    shells_to_drop = {
        shell
        for shell, topics in _TOPICIZED_THIN_SHELLS.items()
        if shell in explicit_targets and any(topic in explicit_targets for topic in topics)
    }
    if not shells_to_drop:
        return

    items[:] = [
        item
        for item in items
        if all(not item.nodeid.startswith(f"{shell}::") for shell in shells_to_drop)
    ]


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


class _CoordinatorDouble:
    """Coordinator test double aligned with the formal runtime surface."""

    def __init__(self) -> None:
        self._devices_store: dict[str, Any] = {}
        self._devices_view = MappingProxyType(self._devices_store)
        self._device_locks: dict[str, asyncio.Lock] = {}
        self.config_entry: Any | None = None
        self.update_interval: timedelta | None = None
        self.last_update_success = True
        self.async_send_command: Any = AsyncMock(return_value=True)
        self.async_request_refresh: Any = AsyncMock()
        self.async_update_listeners: Any = MagicMock()
        self.register_entity: Any = MagicMock()
        self.unregister_entity: Any = MagicMock()
        self.async_add_listener: Any = MagicMock(return_value=lambda: None)

        async def _async_command_service_send_command(
            device: Any,
            command: str,
            properties: list[dict[str, str]] | None = None,
        ) -> Any:
            return await self.async_send_command(device, command, properties)

        self.command_service: Any = MagicMock(last_failure=None)
        self.command_service.async_send_command = AsyncMock(
            side_effect=_async_command_service_send_command
        )

        self.get_device: Any = MagicMock()
        self.get_device.side_effect = self._lookup_get_device
        self.get_device_by_id: Any = MagicMock()
        self.get_device_by_id.side_effect = self._lookup_get_device_by_id
        self.get_device_lock: Any = MagicMock(side_effect=self._get_device_lock)

        async def _async_apply_optimistic_state(
            device: Any,
            properties: Mapping[str, object],
        ) -> None:
            device_lock = self._get_device_lock(device.serial)
            async with device_lock:
                device.update_properties(dict(properties))

        self.async_apply_optimistic_state: Any = AsyncMock(
            side_effect=_async_apply_optimistic_state
        )

        self.auth_service: Any = MagicMock(
            async_ensure_authenticated=AsyncMock(),
            async_trigger_reauth=AsyncMock(),
        )

        self.protocol: Any = MagicMock()
        self.protocol.query_ota_info = AsyncMock(return_value=[])
        self.protocol.get_device_schedules = AsyncMock(return_value=[])
        self.protocol.add_device_schedule = AsyncMock(return_value=[])
        self.protocol.delete_device_schedules = AsyncMock(return_value=[])
        self.protocol.query_command_result = AsyncMock(return_value={})
        self.protocol.get_city = AsyncMock(return_value={})
        self.protocol.query_user_cloud = AsyncMock(return_value={})
        self.protocol.fetch_body_sensor_history = AsyncMock(return_value={})
        self.protocol.fetch_door_sensor_history = AsyncMock(return_value={})
        self.protocol.protocol_diagnostics_snapshot = MagicMock(return_value={})
        self.protocol.diagnostics_context = MagicMock(snapshot=MagicMock(return_value={}))

        async def _async_query_ota_info(**kwargs: Any) -> Any:
            return await self.protocol.query_ota_info(**kwargs)

        async def _async_get_device_schedules(*args: Any, **kwargs: Any) -> Any:
            return await self.protocol.get_device_schedules(*args, **kwargs)

        async def _async_add_device_schedule(*args: Any, **kwargs: Any) -> Any:
            return await self.protocol.add_device_schedule(*args, **kwargs)

        async def _async_delete_device_schedules(*args: Any, **kwargs: Any) -> Any:
            return await self.protocol.delete_device_schedules(*args, **kwargs)

        async def _async_query_command_result(**kwargs: Any) -> Any:
            return await self.protocol.query_command_result(**kwargs)

        async def _async_get_city() -> Any:
            return await self.protocol.get_city()

        async def _async_query_user_cloud() -> Any:
            return await self.protocol.query_user_cloud()

        async def _async_fetch_body_sensor_history(**kwargs: Any) -> Any:
            return await self.protocol.fetch_body_sensor_history(**kwargs)

        async def _async_fetch_door_sensor_history(**kwargs: Any) -> Any:
            return await self.protocol.fetch_door_sensor_history(**kwargs)

        self.async_query_ota_info = AsyncMock(side_effect=_async_query_ota_info)

        async def _async_query_device_ota_info(
            device: Any,
            *,
            allow_rich_v2_fallback: bool | None = None,
        ) -> Any:
            return await self.protocol.query_ota_info(
                device_id=device.serial,
                device_type=device.device_type_hex,
                iot_name=device.iot_name or None,
                allow_rich_v2_fallback=(
                    device.capabilities.is_light
                    if allow_rich_v2_fallback is None
                    else allow_rich_v2_fallback
                ),
            )

        self.async_query_device_ota_info = AsyncMock(
            side_effect=_async_query_device_ota_info
        )
        self.async_query_command_result = AsyncMock(
            side_effect=_async_query_command_result
        )
        self.async_get_city = AsyncMock(side_effect=_async_get_city)
        self.async_query_user_cloud = AsyncMock(side_effect=_async_query_user_cloud)
        self.async_fetch_body_sensor_history = AsyncMock(
            side_effect=_async_fetch_body_sensor_history
        )
        self.async_fetch_door_sensor_history = AsyncMock(
            side_effect=_async_fetch_door_sensor_history
        )

        self.protocol_service: Any = MagicMock()
        self.protocol_service.async_get_device_schedules = AsyncMock(
            side_effect=_async_get_device_schedules
        )
        self.protocol_service.async_add_device_schedule = AsyncMock(
            side_effect=_async_add_device_schedule
        )
        self.protocol_service.async_delete_device_schedules = AsyncMock(
            side_effect=_async_delete_device_schedules
        )
        self.protocol_service.async_get_device_schedules_for_device = AsyncMock(
            side_effect=_async_get_device_schedules
        )
        self.protocol_service.async_add_device_schedule_for_device = AsyncMock(
            side_effect=_async_add_device_schedule
        )
        self.protocol_service.async_delete_device_schedules_for_device = AsyncMock(
            side_effect=_async_delete_device_schedules
        )
        self.protocol_service.async_query_ota_info = AsyncMock(
            side_effect=_async_query_ota_info
        )
        self.protocol_service.async_query_command_result = AsyncMock(
            side_effect=_async_query_command_result
        )
        self.protocol_service.async_get_city = AsyncMock(side_effect=_async_get_city)
        self.protocol_service.async_query_user_cloud = AsyncMock(
            side_effect=_async_query_user_cloud
        )
        self.protocol_service.async_fetch_body_sensor_history = AsyncMock(
            side_effect=_async_fetch_body_sensor_history
        )
        self.protocol_service.async_fetch_door_sensor_history = AsyncMock(
            side_effect=_async_fetch_door_sensor_history
        )

        self.schedule_service = MagicMock(
            async_get_schedules=self.protocol_service.async_get_device_schedules_for_device,
            async_add_schedule=self.protocol_service.async_add_device_schedule_for_device,
            async_delete_schedules=self.protocol_service.async_delete_device_schedules_for_device,
        )

        self.device_refresh_service: Any = MagicMock()
        self.device_refresh_service.devices = self.devices
        self.device_refresh_service.get_device_by_id = self.get_device_by_id
        self.device_refresh_service.request_force_refresh = MagicMock()
        self.device_refresh_service.request_group_reconciliation = MagicMock()
        self.device_refresh_service.async_refresh_devices = AsyncMock()

        self.mqtt_service: Any = MagicMock(connected=True)
        self.mqtt_service.async_setup = AsyncMock(return_value=True)
        self.mqtt_service.async_stop = AsyncMock()
        self.mqtt_service.async_sync_subscriptions = AsyncMock()

        self.telemetry_service: Any = MagicMock()
        self.telemetry_service.build_snapshot = MagicMock(return_value={})

    @property
    def devices(self) -> Mapping[str, Any]:
        return self._devices_view

    @devices.setter
    def devices(self, value: Mapping[str, Any]) -> None:
        self._devices_store = dict(value)
        self._devices_view = MappingProxyType(self._devices_store)
        self.device_refresh_service.devices = self._devices_view

    def iter_devices(self) -> tuple[LiproDevice, ...]:
        return tuple(self._devices_view.values())

    def _lookup_get_device(self, serial: str) -> Any:
        if self.get_device._mock_return_value is not DEFAULT:
            return self.get_device._mock_return_value
        return self._devices_store.get(serial)

    def _lookup_get_device_by_id(self, device_id: str) -> Any:
        if self.get_device_by_id._mock_return_value is not DEFAULT:
            return self.get_device_by_id._mock_return_value
        return self._devices_store.get(device_id)

    def _get_device_lock(self, serial: str) -> asyncio.Lock:
        return self._device_locks.setdefault(serial, asyncio.Lock())

    def set_device(self, device: Any) -> None:
        self._devices_store[device.serial] = device
        self.device_refresh_service.devices = self._devices_view

    def set_devices(self, *devices: Any) -> None:
        self.devices = {device.serial: device for device in devices}


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
