"""Tests for StatusRuntime."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.coordinator.runtime.status_runtime import StatusRuntime
from custom_components.lipro.core.device import LiproDevice


@pytest.fixture
def mock_device() -> LiproDevice:
    """Create a mock device."""
    device = MagicMock(spec=LiproDevice)
    device.serial = "TEST001"
    device.is_online = True
    device.has_recent_mqtt_update = MagicMock(return_value=False)
    return device


@pytest.fixture
async def status_runtime(mock_device: LiproDevice) -> StatusRuntime:
    """Create a StatusRuntime instance."""
    devices = {mock_device.serial: mock_device}

    async def mock_query_status(device_ids: list[str]) -> dict[str, dict[str, str]]:
        return {device_id: {"brightness": "100"} for device_id in device_ids}

    async def mock_apply_update(device: LiproDevice, props: dict[str, str], source: str) -> bool:
        return True

    def mock_get_device(device_id: str) -> LiproDevice | None:
        return devices.get(device_id)

    return StatusRuntime(
        power_query_interval=300,
        outlet_power_cycle_size=10,
        max_devices_per_query=50,
        initial_batch_size=32,
        query_device_status=mock_query_status,
        apply_properties_update=mock_apply_update,
        get_device_by_id=mock_get_device,
    )


class TestStatusScheduler:
    """Test StatusScheduler functionality."""

    @pytest.mark.asyncio
    async def test_should_query_power_initial(self, status_runtime: StatusRuntime) -> None:
        """Test power query should run initially."""
        assert status_runtime.should_query_power() is True

    @pytest.mark.asyncio
    async def test_mark_power_query_complete(self, status_runtime: StatusRuntime) -> None:
        """Test marking power query as complete."""
        status_runtime.mark_power_query_complete()
        assert status_runtime.should_query_power() is False

    @pytest.mark.asyncio
    async def test_get_outlet_power_query_slice(self, status_runtime: StatusRuntime) -> None:
        """Test getting outlet power query slice."""
        outlet_ids = [f"outlet{i}" for i in range(25)]
        slice_ids = status_runtime.get_outlet_power_query_slice(outlet_ids)
        assert len(slice_ids) == 10

    @pytest.mark.asyncio
    async def test_advance_outlet_power_cycle(self, status_runtime: StatusRuntime) -> None:
        """Test advancing outlet power cycle."""
        outlet_ids = [f"outlet{i}" for i in range(25)]
        first_slice = status_runtime.get_outlet_power_query_slice(outlet_ids)
        status_runtime.advance_outlet_power_cycle(outlet_ids)
        second_slice = status_runtime.get_outlet_power_query_slice(outlet_ids)
        assert first_slice != second_slice

    @pytest.mark.asyncio
    async def test_reset_power_query_state(self, status_runtime: StatusRuntime) -> None:
        """Test resetting power query state."""
        status_runtime.mark_power_query_complete()
        status_runtime.reset_power_query_state()
        assert status_runtime.should_query_power() is True


class TestStatusStrategy:
    """Test StatusStrategy functionality."""

    @pytest.mark.asyncio
    async def test_compute_query_batches(self, status_runtime: StatusRuntime) -> None:
        """Test computing query batches."""
        device_ids = [f"device{i}" for i in range(100)]
        batches = status_runtime.compute_query_batches(device_ids)
        assert len(batches) > 1
        assert all(len(batch) <= 50 for batch in batches)

    @pytest.mark.asyncio
    async def test_should_query_device_mqtt_disconnected(
        self,
        status_runtime: StatusRuntime,
        mock_device: LiproDevice,
    ) -> None:
        """Test should query device when MQTT is disconnected."""
        should_query = status_runtime.should_query_device(mock_device, mqtt_connected=False)
        assert should_query is True

    @pytest.mark.asyncio
    async def test_should_query_device_offline(
        self,
        status_runtime: StatusRuntime,
        mock_device: LiproDevice,
    ) -> None:
        """Test should query offline device."""
        mock_device.is_online = False
        should_query = status_runtime.should_query_device(mock_device, mqtt_connected=True)
        assert should_query is True

    @pytest.mark.asyncio
    async def test_filter_query_candidates(
        self,
        status_runtime: StatusRuntime,
        mock_device: LiproDevice,
    ) -> None:
        """Test filtering query candidates."""
        devices = {mock_device.serial: mock_device}
        device_ids = [mock_device.serial]
        filtered = status_runtime.filter_query_candidates(
            devices,
            device_ids,
            mqtt_connected=True,
        )
        assert len(filtered) == 1

    @pytest.mark.asyncio
    async def test_get_current_batch_size(self, status_runtime: StatusRuntime) -> None:
        """Test getting current batch size."""
        assert status_runtime.get_current_batch_size() == 32

    @pytest.mark.asyncio
    async def test_update_batch_size(self, status_runtime: StatusRuntime) -> None:
        """Test updating batch size."""
        status_runtime.update_batch_size(40)
        assert status_runtime.get_current_batch_size() == 40


class TestStatusExecutor:
    """Test StatusExecutor functionality."""

    @pytest.mark.asyncio
    async def test_execute_status_query(
        self,
        status_runtime: StatusRuntime,
        mock_device: LiproDevice,
    ) -> None:
        """Test executing status query."""
        result = await status_runtime.execute_status_query([mock_device.serial])
        assert result["device_count"] == 1
        assert result["error"] is None
        assert result["duration"] >= 0

    @pytest.mark.asyncio
    async def test_execute_status_query_empty(self, status_runtime: StatusRuntime) -> None:
        """Test executing status query with empty list."""
        result = await status_runtime.execute_status_query([])
        assert result["device_count"] == 0
        assert result["updated_count"] == 0

    @pytest.mark.asyncio
    async def test_execute_parallel_queries(
        self,
        status_runtime: StatusRuntime,
        mock_device: LiproDevice,
    ) -> None:
        """Test executing parallel queries."""
        batches = [[mock_device.serial], [mock_device.serial]]
        results = await status_runtime.execute_parallel_queries(batches, concurrency=2)
        assert len(results) == 2
        assert all(r["error"] is None for r in results)

    @pytest.mark.asyncio
    async def test_get_runtime_metrics(self, status_runtime: StatusRuntime) -> None:
        """Test getting runtime metrics."""
        metrics = status_runtime.get_runtime_metrics()
        assert "scheduler" in metrics
        assert "strategy" in metrics

    @pytest.mark.asyncio
    async def test_execute_parallel_queries(
        self,
        status_runtime: StatusRuntime,
        mock_device: LiproDevice,
    ) -> None:
        """Test executing parallel queries."""
        batches = [[mock_device.serial], [mock_device.serial]]
        results = await status_runtime.execute_parallel_queries(batches, concurrency=2)
        assert len(results) == 2
        assert all(r["error"] is None for r in results)

    @pytest.mark.asyncio
    async def test_get_runtime_metrics(self, status_runtime: StatusRuntime) -> None:
        """Test getting runtime metrics."""
        metrics = status_runtime.get_runtime_metrics()
        assert "scheduler" in metrics
        assert "strategy" in metrics
