# ruff: noqa: SLF001

"""Internal submit-flow helpers for anonymous-share manager formal homes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..telemetry.models import OperationOutcome, build_operation_outcome
from .report_builder import build_developer_feedback_report

if TYPE_CHECKING:
    from logging import Logger

    import aiohttp

    from .manager import AnonymousShareManager


async def submit_developer_feedback(
    manager: AnonymousShareManager,
    session: aiohttp.ClientSession,
    feedback: dict[str, object],
    *,
    logger: Logger,
) -> bool:
    """Submit one developer-feedback payload through the manager formal home."""
    state = manager._primary_state() if manager._aggregate else manager._state
    async with state.upload_lock:
        report = build_developer_feedback_report(
            installation_id=state.installation_id,
            ha_version=state.ha_version,
            feedback=feedback,
        )
        outcome = await manager._submit_share_payload_with_outcome(
            session,
            report,
            label="Developer feedback",
        )
        state.last_submit_outcome = outcome
        if not outcome.is_success:
            return False
        logger.info("Developer feedback report submitted")
        return True


async def submit_report(
    manager: AnonymousShareManager,
    session: aiohttp.ClientSession,
    *,
    force: bool,
) -> bool:
    """Submit the anonymous-share payload(s) through the manager formal home."""
    if manager._aggregate:
        success = True
        aggregate_outcome: OperationOutcome | None = None
        for child_manager in manager._iter_managers():
            child_success = await child_manager.submit_report(session, force=force)
            success = child_success and success
            child_outcome = child_manager.last_submit_outcome
            if child_outcome is None:
                continue
            if aggregate_outcome is None:
                aggregate_outcome = child_outcome
        manager._state.last_submit_outcome = (
            aggregate_outcome
            or build_operation_outcome(
                kind=("success" if success else "failed"),
                reason_code=("submitted" if success else "submit_failed"),
            )
        )
        return success

    if not manager._collector.is_enabled:
        return False
    if not manager._has_pending_report_data():
        return True
    if manager._should_skip_report_submission(force=force):
        return True

    async with manager._state.upload_lock:
        report = manager.build_report()
        if not await manager._async_submit_share_payload(
            session,
            report,
            label="Anonymous share",
        ):
            return False
        await manager._async_finalize_successful_submit()
        return True


async def submit_if_needed(
    manager: AnonymousShareManager,
    session: aiohttp.ClientSession,
) -> bool:
    """Submit the anonymous-share payload only when thresholds are met."""
    if manager._aggregate:
        success = True
        for child_manager in manager._iter_managers():
            success = await child_manager.submit_if_needed(session) and success
        return success
    if not manager._collector.is_enabled:
        return True
    if manager._should_submit_if_needed():
        return await manager.submit_report(session)
    return True
