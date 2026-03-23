"""Internal submit-flow helpers for anonymous-share manager formal homes."""

from __future__ import annotations

import asyncio
from typing import Protocol

from ..telemetry.models import OperationOutcome, build_operation_outcome
from .report_builder import build_developer_feedback_report


class SubmitStateLike(Protocol):
    """Submit-state surface required by manager submit flows."""

    upload_lock: asyncio.Lock
    installation_id: str | None
    ha_version: str | None


class AnonymousShareSubmitManagerLike(Protocol):
    """Formal manager surface consumed by submit-flow helpers."""

    @property
    def is_enabled(self) -> bool:
        """Return whether anonymous sharing is enabled."""

    @property
    def last_submit_outcome(self) -> OperationOutcome | None:
        """Return the latest submit outcome for this manager."""

    def is_aggregate_view(self) -> bool:
        """Return whether this manager represents an aggregate view."""

    def iter_scoped_managers(self) -> list[AnonymousShareSubmitManagerLike]:
        """Return child managers participating in aggregate submission."""

    def get_submit_state(self) -> SubmitStateLike:
        """Return the current scope submit state."""

    def get_primary_submit_state(self) -> SubmitStateLike:
        """Return the preferred aggregate submit state."""

    def set_last_submit_outcome(self, outcome: OperationOutcome | None) -> None:
        """Persist one submit outcome on the manager."""

    def has_pending_report_data(self) -> bool:
        """Return whether the manager has pending report data."""

    def should_skip_report_submission(self, *, force: bool) -> bool:
        """Return whether report submission should be skipped."""

    def should_submit_if_needed(self) -> bool:
        """Return whether threshold-driven submission should run."""

    def build_report(self) -> dict[str, object]:
        """Build the anonymous-share payload for this manager."""

    async def async_submit_share_payload_with_outcome(
        self,
        session,
        report: dict[str, object],
        *,
        label: str,
    ) -> OperationOutcome:
        """Submit one payload and return the structured outcome."""

    async def async_submit_share_payload(
        self,
        session,
        report: dict[str, object],
        *,
        label: str,
    ) -> bool:
        """Submit one payload with bool compatibility."""

    async def async_finalize_successful_submit(self) -> None:
        """Finalize one successful submit by updating manager state."""

    async def submit_report(self, session, *, force: bool = False) -> bool:
        """Submit the manager report, optionally forcing a send."""

    async def submit_if_needed(self, session) -> bool:
        """Submit the manager report only when thresholds are met."""


async def _submit_developer_feedback_locked(
    manager: AnonymousShareSubmitManagerLike,
    session,
    feedback: dict[str, object],
    *,
    logger,
) -> bool:
    """Submit one developer-feedback payload while holding the scope lock."""
    state = (
        manager.get_primary_submit_state()
        if manager.is_aggregate_view()
        else manager.get_submit_state()
    )
    async with state.upload_lock:
        report = build_developer_feedback_report(
            installation_id=state.installation_id,
            ha_version=state.ha_version,
            feedback=feedback,
        )
        outcome = await manager.async_submit_share_payload_with_outcome(
            session,
            report,
            label="Developer feedback",
        )
        manager.set_last_submit_outcome(outcome)
        if not outcome.is_success:
            return False
        logger.info("Developer feedback report submitted")
        return True


async def submit_developer_feedback(
    manager: AnonymousShareSubmitManagerLike,
    session,
    feedback: dict[str, object],
    *,
    logger,
) -> bool:
    """Submit one developer-feedback payload through the manager formal home."""
    return await _submit_developer_feedback_locked(
        manager,
        session,
        feedback,
        logger=logger,
    )


async def _submit_aggregate_report(
    manager: AnonymousShareSubmitManagerLike,
    session,
    *,
    force: bool,
) -> bool:
    """Submit all scoped reports for one aggregate manager view."""
    success = True
    aggregate_outcome: OperationOutcome | None = None
    for child_manager in manager.iter_scoped_managers():
        child_success = await child_manager.submit_report(session, force=force)
        success = child_success and success
        child_outcome = child_manager.last_submit_outcome
        if child_outcome is None:
            continue
        if aggregate_outcome is None:
            aggregate_outcome = child_outcome

    manager.set_last_submit_outcome(
        aggregate_outcome
        or build_operation_outcome(
            kind=("success" if success else "failed"),
            reason_code=("submitted" if success else "submit_failed"),
        )
    )
    return success


async def _submit_scoped_report(
    manager: AnonymousShareSubmitManagerLike,
    session,
    *,
    force: bool,
) -> bool:
    """Submit one scoped manager report when the current state requires it."""
    if not manager.is_enabled:
        return False
    if not manager.has_pending_report_data():
        return True
    if manager.should_skip_report_submission(force=force):
        return True

    async with manager.get_submit_state().upload_lock:
        report = manager.build_report()
        if not await manager.async_submit_share_payload(
            session,
            report,
            label="Anonymous share",
        ):
            return False
        await manager.async_finalize_successful_submit()
        return True


async def submit_report(
    manager: AnonymousShareSubmitManagerLike,
    session,
    *,
    force: bool,
) -> bool:
    """Submit the anonymous-share payload(s) through the manager formal home."""
    if manager.is_aggregate_view():
        return await _submit_aggregate_report(manager, session, force=force)
    return await _submit_scoped_report(manager, session, force=force)


async def _submit_if_needed_for_aggregate(
    manager: AnonymousShareSubmitManagerLike,
    session,
) -> bool:
    """Submit aggregate child managers only when their thresholds are met."""
    success = True
    for child_manager in manager.iter_scoped_managers():
        success = await child_manager.submit_if_needed(session) and success
    return success


async def submit_if_needed(
    manager: AnonymousShareSubmitManagerLike,
    session,
) -> bool:
    """Submit the anonymous-share payload only when thresholds are met."""
    if manager.is_aggregate_view():
        return await _submit_if_needed_for_aggregate(manager, session)
    if not manager.is_enabled:
        return True
    if manager.should_submit_if_needed():
        return await manager.submit_report(session)
    return True
