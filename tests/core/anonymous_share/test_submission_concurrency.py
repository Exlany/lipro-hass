"""Consent and duplicate-send contracts for queued anonymous-share uploads."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro.core.telemetry.models import build_operation_outcome

from .support import _make_manager, _make_mock_device


async def test_waiting_report_rechecks_disabled_sharing() -> None:
    """Revoking consent while waiting for another upload must prevent a send."""
    manager = _make_manager()
    manager.record_device(_make_mock_device())
    state = manager.get_submit_state()
    submit = AsyncMock(
        return_value=build_operation_outcome(kind="success", reason_code="submitted")
    )
    with patch.object(manager, "async_submit_share_payload_with_outcome", submit):
        async with state.upload_lock:
            task = asyncio.create_task(manager.submit_report(MagicMock(), force=True))
            await asyncio.sleep(0)
            manager.set_enabled(False)
        assert await task is False
    submit.assert_not_awaited()


async def test_queued_reports_do_not_send_cleared_payload_twice() -> None:
    """The second waiter must observe completion of the first report."""
    manager = _make_manager()
    manager.record_device(_make_mock_device())
    started = asyncio.Event()
    finish = asyncio.Event()

    async def submit(*args: object, **kwargs: object):
        started.set()
        await finish.wait()
        return build_operation_outcome(kind="success", reason_code="submitted")

    send = AsyncMock(side_effect=submit)
    with patch.object(manager, "async_submit_share_payload_with_outcome", send):
        first = asyncio.create_task(manager.submit_report(MagicMock(), force=True))
        await started.wait()
        second = asyncio.create_task(manager.submit_report(MagicMock(), force=True))
        await asyncio.sleep(0)
        finish.set()
        results = await asyncio.gather(first, second)
    assert all(results)
    send.assert_awaited_once()


async def test_report_acknowledges_only_data_present_before_upload(tmp_path) -> None:
    """New models and repeated errors collected during I/O remain pending."""
    manager = _make_manager()
    manager._storage_path = str(tmp_path)
    manager.record_device(_make_mock_device(iot_name="before"))
    manager.record_api_error("/status", 500, "retry")
    started = asyncio.Event()
    finish = asyncio.Event()

    async def submit(*args: object, **kwargs: object):
        started.set()
        await finish.wait()
        return build_operation_outcome(kind="success", reason_code="submitted")

    with patch.object(
        manager,
        "async_submit_share_payload_with_outcome",
        AsyncMock(side_effect=submit),
    ):
        task = asyncio.create_task(manager.submit_report(MagicMock(), force=True))
        await started.wait()
        manager.record_device(_make_mock_device(iot_name="during"))
        manager.record_api_error("/status", 500, "retry")
        manager.record_api_error("/new", 503, "unavailable")
        finish.set()
        assert await task

    assert manager.pending_count == (1, 2)
    assert manager._reported_device_keys == {"before"}
    pending = manager.build_report()
    assert pending["device_count"] == 1
    assert all(
        error.count == 1 for error in manager.get_submit_state().collector.errors
    )
    cached = json.loads((tmp_path / ".lipro_reported_devices.json").read_text())
    assert cached == {"devices": ["before"]}


async def test_changed_device_record_survives_acknowledgement() -> None:
    """An updated record with the same model key is not the delivered record."""
    manager = _make_manager()
    manager.record_device(_make_mock_device(iot_name="model", properties={"power": 0}))

    async def submit(*args: object, **kwargs: object):
        manager.record_device(
            _make_mock_device(iot_name="model", properties={"power": 1})
        )
        return build_operation_outcome(kind="success", reason_code="submitted")

    with patch.object(
        manager,
        "async_submit_share_payload_with_outcome",
        AsyncMock(side_effect=submit),
    ):
        assert await manager.submit_report(MagicMock(), force=True)
    assert manager.pending_count == (1, 0)
    assert manager.get_submit_state().collector.devices["model"].properties == {
        "power": 1
    }


async def test_lite_report_does_not_acknowledge_omitted_records() -> None:
    """The 413 fallback only delivers the first ten devices and errors."""
    manager = _make_manager()
    for index in range(12):
        manager.record_device(_make_mock_device(iot_name=f"model-{index}"))
        manager.record_api_error(f"/endpoint/{index}", 500, "retry")
    with patch.object(
        manager,
        "async_submit_share_payload_with_outcome",
        AsyncMock(
            return_value=build_operation_outcome(
                kind="success", reason_code="submitted_lite_payload"
            )
        ),
    ):
        assert await manager.submit_report(MagicMock(), force=True)
    assert manager.pending_count == (2, 2)
    assert manager._reported_device_keys == {f"model-{index}" for index in range(10)}
    assert set(manager.get_submit_state().collector.devices) == {"model-10", "model-11"}


async def test_cancelled_upload_keeps_pending_records() -> None:
    """No acknowledgement is applied when an in-flight upload is cancelled."""
    manager = _make_manager()
    manager.record_device(_make_mock_device())
    manager.record_api_error("/status", 500, "retry")
    with (
        patch.object(
            manager,
            "async_submit_share_payload_with_outcome",
            AsyncMock(side_effect=asyncio.CancelledError),
        ),
        pytest.raises(asyncio.CancelledError),
    ):
        await manager.submit_report(MagicMock(), force=True)
    assert manager.pending_count == (1, 1)
    assert manager._reported_device_keys == set()
