"""Internal submit-flow helpers for anonymous-share manager formal homes."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
import logging
from typing import Protocol

import aiohttp

from ..telemetry.models import OperationOutcome, build_operation_outcome
from .report_builder import build_developer_feedback_report
from .share_client_support import SharePayload


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

    def iter_scoped_managers(self) -> Sequence[AnonymousShareSubmitManagerLike]:
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

    def build_report(self) -> SharePayload:
        """Build the anonymous-share payload for this manager."""

    async def async_submit_share_payload_with_outcome(
        self,
        session: aiohttp.ClientSession,
        report: SharePayload,
        *,
        label: str,
    ) -> OperationOutcome:
        """Submit one payload and return the structured outcome."""

    async def async_finalize_successful_submit(self) -> None:
        """Finalize one successful submit by updating manager state."""

    async def submit_report(
        self, session: aiohttp.ClientSession, *, force: bool = False
    ) -> bool:
        """Submit the manager report, optionally forcing a send."""

    async def submit_if_needed(self, session: aiohttp.ClientSession) -> bool:
        """Submit the manager report only when thresholds are met."""


async def _submit_developer_feedback_locked(
    manager: AnonymousShareSubmitManagerLike,
    session: aiohttp.ClientSession,
    feedback: dict[str, object],
    *,
    logger: logging.Logger,
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
    session: aiohttp.ClientSession,
    feedback: dict[str, object],
    *,
    logger: logging.Logger,
) -> bool:
    """Submit one developer-feedback payload through the manager formal home."""
    return await _submit_developer_feedback_locked(
        manager,
        session,
        feedback,
        logger=logger,
    )


def _collapse_aggregate_submit_outcome(
    *,
    success: bool,
    child_outcomes: list[OperationOutcome],
) -> OperationOutcome:
    """Return one aggregate submit outcome without hiding child failures."""
    for child_outcome in child_outcomes:
        if not child_outcome.is_success:
            return child_outcome
    if child_outcomes:
        return child_outcomes[0]
    return build_operation_outcome(
        kind=("success" if success else "failed"),
        reason_code=("submitted" if success else "submit_failed"),
    )


async def _submit_child_managers(
    manager: AnonymousShareSubmitManagerLike,
    *,
    submit_child: Callable[[AnonymousShareSubmitManagerLike], Awaitable[bool]],
) -> bool:
    """Submit aggregate child managers through one shared traversal helper."""
    success = True
    child_outcomes: list[OperationOutcome] = []
    for child_manager in manager.iter_scoped_managers():
        child_success = await submit_child(child_manager)
        success = child_success and success
        child_outcome = child_manager.last_submit_outcome
        if child_outcome is not None:
            child_outcomes.append(child_outcome)

    manager.set_last_submit_outcome(
        _collapse_aggregate_submit_outcome(
            success=success,
            child_outcomes=child_outcomes,
        )
    )
    return success


async def _submit_aggregate_report(
    manager: AnonymousShareSubmitManagerLike,
    session: aiohttp.ClientSession,
    *,
    force: bool,
) -> bool:
    """Submit all scoped reports for one aggregate manager view."""

    async def _submit_child(child_manager: AnonymousShareSubmitManagerLike) -> bool:
        if not child_manager.is_enabled:
            return True
        return await child_manager.submit_report(session, force=force)

    return await _submit_child_managers(manager, submit_child=_submit_child)


async def _submit_scoped_report(
    manager: AnonymousShareSubmitManagerLike,
    session: aiohttp.ClientSession,
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
        outcome = await manager.async_submit_share_payload_with_outcome(
            session,
            report,
            label="Anonymous share",
        )
        manager.set_last_submit_outcome(outcome)
        if not outcome.is_success:
            return False
        await manager.async_finalize_successful_submit()
        return True


async def submit_report(
    manager: AnonymousShareSubmitManagerLike,
    session: aiohttp.ClientSession,
    *,
    force: bool,
) -> bool:
    """Submit the anonymous-share payload(s) through the manager formal home."""
    if manager.is_aggregate_view():
        return await _submit_aggregate_report(manager, session, force=force)
    return await _submit_scoped_report(manager, session, force=force)


async def _submit_if_needed_for_aggregate(
    manager: AnonymousShareSubmitManagerLike,
    session: aiohttp.ClientSession,
) -> bool:
    """Submit aggregate child managers only when their thresholds are met."""

    async def _submit_child(child_manager: AnonymousShareSubmitManagerLike) -> bool:
        return await child_manager.submit_if_needed(session)

    return await _submit_child_managers(manager, submit_child=_submit_child)


async def submit_if_needed(
    manager: AnonymousShareSubmitManagerLike,
    session: aiohttp.ClientSession,
) -> bool:
    """Submit the anonymous-share payload only when thresholds are met."""
    if manager.is_aggregate_view():
        return await _submit_if_needed_for_aggregate(manager, session)
    if not manager.is_enabled:
        return True
    if manager.should_submit_if_needed():
        return await manager.submit_report(session)
    return True
