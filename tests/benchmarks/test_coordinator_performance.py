"""Performance benchmarks for coordinator refactoring.

Note: These benchmarks focus on completed runtime components.
Tests are limited to working components only.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.lipro.core.coordinator.runtime.device_runtime import (
    DeviceRuntime,
)
from custom_components.lipro.core.device.identity_index import DeviceIdentityIndex


@pytest.fixture
def mock_client():
    """Mock API client."""
    client = Mock()
    client.get_devices = AsyncMock(return_value={"devices": [], "total": 0})
    client.query_device_status = AsyncMock(return_value=[])
    return client


@pytest.fixture
def mock_auth_manager():
    """Mock auth manager."""
    auth = Mock()
    auth.async_ensure_authenticated = AsyncMock()
    auth.ensure_valid_token = AsyncMock()
    auth.is_authenticated = True
    return auth


@pytest.fixture
def device_identity_index():
    """Create device identity index."""
    return DeviceIdentityIndex()


@pytest.fixture
def device_runtime(mock_client, mock_auth_manager, device_identity_index):
    """Create device runtime for benchmarking."""
    return DeviceRuntime(
        protocol=mock_client,
        auth_manager=mock_auth_manager,
        device_identity_index=device_identity_index,
        filter_config_options={},
    )


def test_device_identity_index_registration(
    benchmark, device_identity_index, make_device
):
    """Benchmark device registration in identity index."""
    device = make_device("light", serial="test_device_001")

    def register():
        device_identity_index.register(device.serial, device)
        return device

    result = benchmark(register)
    assert result is device
    assert device_identity_index.get("test_device_001") is device


def test_device_identity_index_lookup(benchmark, device_identity_index, make_device):
    """Benchmark device identity index lookup performance."""
    # Populate identity index
    for i in range(100):
        device = make_device("light", serial=f"device_{i:03d}")
        device_identity_index.register(device.serial, device)

    def lookup_by_serial():
        return device_identity_index.get("device_050")

    result = benchmark(lookup_by_serial)
    assert result is not None


def test_device_runtime_refresh_check(benchmark, device_runtime):
    """Benchmark device list refresh decision."""

    def check_refresh():
        return device_runtime.should_refresh_device_list()

    result = benchmark(check_refresh)
    assert result is True


def test_normalize_device_key_performance(benchmark):
    """Benchmark device key normalization."""

    def normalize(key: str) -> str:
        return key.lower().strip()

    def normalize_key():
        return normalize("  DEVICE_123  ")

    result = benchmark(normalize_key)
    assert result == "device_123"


def test_device_identity_index_bulk_registration(
    benchmark, device_identity_index, make_device
):
    """Benchmark bulk device registration."""
    devices = [make_device("light", serial=f"bulk_{i:03d}") for i in range(50)]

    def bulk_register():
        for device in devices:
            device_identity_index.register(device.serial, device)

    benchmark(bulk_register)

    assert device_identity_index.get("bulk_000") is devices[0]
    assert device_identity_index.get("bulk_025") is devices[25]
    assert device_identity_index.get("bulk_049") is devices[49]


def test_device_identity_index_bulk_lookup(
    benchmark, device_identity_index, make_device
):
    """Benchmark bulk device lookups."""
    # Populate identity index
    for i in range(100):
        device = make_device("light", serial=f"device_{i:03d}")
        device_identity_index.register(device.serial, device)

    serials = [f"device_{i:03d}" for i in range(0, 100, 10)]

    def bulk_lookup():
        return [device_identity_index.get(serial) for serial in serials]

    results = benchmark(bulk_lookup)
    assert len(results) == 10
    assert all(r is not None for r in results)
