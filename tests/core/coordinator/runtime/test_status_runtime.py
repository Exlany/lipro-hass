"""Tests for StatusRuntime."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.lipro.core.coordinator.runtime.status.executor import (
    StatusExecutor,
)
from custom_components.lipro.core.coordinator.runtime.status.scheduler import (
    StatusScheduler,
)
from custom_components.lipro.core.coordinator.runtime.status_runtime import (
    StatusRuntime,
)
from custom_components.lipro.core.device import LiproDevice


@pytest.fixture
def mock_device() -> LiproDevice:
    """Create a test device."""
    return LiproDevice(
        device_number=1,
        serial="TEST001",
        name="Test Device",
        device_type=1,
        iot_name="lipro_led",
        physical_model="light",
        properties={"connectState": "1"},
    )


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

    def test_get_outlet_power_query_slice_returns_empty_for_empty_input(self) -> None:
        scheduler = StatusScheduler(power_query_interval=300, outlet_power_cycle_size=2)

        assert scheduler.get_outlet_power_query_slice([]) == []

    def test_get_outlet_power_query_slice_returns_all_when_within_cycle_size(self) -> None:
        scheduler = StatusScheduler(power_query_interval=300, outlet_power_cycle_size=5)
        outlet_ids = ["outlet1", "outlet2"]

        assert scheduler.get_outlet_power_query_slice(outlet_ids) == outlet_ids

    def test_get_outlet_power_query_slice_wraps_at_cycle_boundary(self) -> None:
        scheduler = StatusScheduler(power_query_interval=300, outlet_power_cycle_size=2)
        outlet_ids = ["outlet1", "outlet2", "outlet3"]

        scheduler.advance_outlet_power_cycle(outlet_ids)

        assert scheduler.get_outlet_power_query_slice(outlet_ids) == [
            "outlet3",
            "outlet1",
        ]

    def test_advance_outlet_power_cycle_resets_offset_for_empty_input(self) -> None:
        scheduler = StatusScheduler(power_query_interval=300, outlet_power_cycle_size=2)

        scheduler.advance_outlet_power_cycle(["outlet1", "outlet2", "outlet3"])
        scheduler.advance_outlet_power_cycle([])

        assert scheduler.get_scheduling_metrics()["outlet_cycle_offset"] == 0


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
        mock_device.update_properties({"connectState": "0"})
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
    async def test_status_executor_skips_unknown_devices(self) -> None:
        executor = StatusExecutor(
            query_device_status=AsyncMock(return_value={"missing": {"brightness": 100}}),
            apply_properties_update=AsyncMock(return_value=True),
            get_device_by_id=lambda _device_id: None,
        )

        result = await executor.execute_status_query(["missing"])

        assert result["updated_count"] == 0
        assert result["error"] is None

    @pytest.mark.asyncio
    async def test_status_executor_reports_query_errors(self) -> None:
        executor = StatusExecutor(
            query_device_status=AsyncMock(side_effect=RuntimeError("boom")),
            apply_properties_update=AsyncMock(return_value=True),
            get_device_by_id=lambda _device_id: MagicMock(),
        )

        result = await executor.execute_status_query(["device1"])

        assert result["updated_count"] == 0
        assert result["error"] == "boom"

    @pytest.mark.asyncio
    async def test_status_executor_isolates_single_device_apply_failures(self) -> None:
        first = MagicMock(serial="device1")
        second = MagicMock(serial="device2")

        async def _apply(device, properties, source):
            assert source == "rest_status"
            if device.serial == "device1":
                raise RuntimeError("apply-boom")
            return bool(properties)

        executor = StatusExecutor(
            query_device_status=AsyncMock(
                return_value={
                    "device1": {"powerState": "1"},
                    "device2": {"powerState": "0"},
                }
            ),
            apply_properties_update=AsyncMock(side_effect=_apply),
            get_device_by_id=lambda device_id: {"device1": first, "device2": second}.get(device_id),
        )

        result = await executor.execute_status_query(["device1", "device2"])

        assert result["updated_count"] == 1
        assert result["error"] is None
        assert result["apply_errors"] == ["device1:apply-boom"]

    @pytest.mark.asyncio
    async def test_status_executor_parallel_queries_return_empty_for_empty_batches(
        self,
    ) -> None:
        executor = StatusExecutor(
            query_device_status=AsyncMock(return_value={}),
            apply_properties_update=AsyncMock(return_value=True),
            get_device_by_id=lambda _device_id: None,
        )

        assert await executor.execute_parallel_queries([]) == []

    @pytest.mark.asyncio
    async def test_status_executor_parallel_queries_surfaces_batch_errors(self) -> None:
        executor = StatusExecutor(
            query_device_status=AsyncMock(return_value={}),
            apply_properties_update=AsyncMock(return_value=True),
            get_device_by_id=lambda _device_id: None,
        )
        executor.execute_status_query = AsyncMock(  # type: ignore[method-assign]
            side_effect=[
                {
                    "duration": 0.1,
                    "device_count": 1,
                    "updated_count": 1,
                    "error": None,
                },
                RuntimeError("parallel-boom"),
            ]
        )

        results = await executor.execute_parallel_queries(
            [["device1"], ["device2"]],
            concurrency=2,
        )

        assert results[0]["updated_count"] == 1
        assert results[1]["device_count"] == 1
        assert results[1]["error"] == "parallel-boom"

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
