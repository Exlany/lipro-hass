"""Consent and duplicate-send contracts for queued anonymous-share uploads."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

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
