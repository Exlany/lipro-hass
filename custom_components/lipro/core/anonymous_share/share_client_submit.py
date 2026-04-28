"""Support-only submit flow helpers for the anonymous-share client."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

import aiohttp

from ..telemetry.models import OperationOutcome, build_operation_outcome
from .share_client_ports import _SHARE_SUBMIT_ORIGIN, ShareWorkerClientLike
from .share_client_submit_attempts import submit_report_variants
from .share_client_submit_outcomes import (
    build_client_error_submit_outcome,
    build_submit_http_failure,
    build_timeout_submit_outcome,
    build_unexpected_submit_outcome,
)
from .share_client_support import (
    SharePayload,
    backoff_active,
    build_submit_variants,
    has_valid_installation_id,
    refresh_due,
)

if TYPE_CHECKING:
    from logging import Logger


async def submit_share_payload_with_outcome(
    client: ShareWorkerClientLike,
    session: aiohttp.ClientSession,
    report: SharePayload,
    *,
    label: str,
    ensure_loaded: Callable[[], Awaitable[None]],
    logger: Logger,
    now: Callable[[], float],
    build_lite_variant: Callable[[SharePayload], SharePayload],
) -> OperationOutcome:
    """Submit one payload to the share endpoint with typed failure semantics."""
    preflight_outcome = await _preflight_submit_share_payload(
        client,
        report,
        label=label,
        ensure_loaded=ensure_loaded,
        logger=logger,
        now=now,
    )
    if preflight_outcome is not None:
        return preflight_outcome

    refresh_outcome = await _refresh_submit_token_if_due(client, session, now=now)
    if refresh_outcome is not None:
        return refresh_outcome

    return await _submit_share_report_variants(
        client,
        session,
        report,
        label=label,
        logger=logger,
        now=now,
        build_lite_variant=build_lite_variant,
    )


async def _submit_share_report_variants(
    client: ShareWorkerClientLike,
    session: aiohttp.ClientSession,
    report: SharePayload,
    *,
    label: str,
    logger: Logger,
    now: Callable[[], float],
    build_lite_variant: Callable[[SharePayload], SharePayload],
) -> OperationOutcome:
    """Submit all share payload variants while preserving typed terminal outcomes."""
    try:
        submit_variants = build_submit_variants(
            report,
            install_token=client.install_token,
            build_lite_variant=build_lite_variant,
        )
        outcome, last_status = await submit_report_variants(
            client,
            session,
            submit_variants=submit_variants,
            now=now,
        )
        if outcome is not None:
            return outcome
        return build_submit_http_failure(
            label=label,
            logger=logger,
            last_status=last_status,
        )
    except TimeoutError as err:
        return build_timeout_submit_outcome(err, label=label, logger=logger)
    except aiohttp.ClientError as err:
        return build_client_error_submit_outcome(err, label=label, logger=logger)
    except OSError as err:
        return build_unexpected_submit_outcome(
            err,
            label=label,
            logger=logger,
            reason_code="os_error",
            failure_category="network",
            handling_policy="retry",
        )
    except ValueError as err:
        return build_unexpected_submit_outcome(
            err,
            label=label,
            logger=logger,
            reason_code="value_error",
            failure_category="protocol",
            handling_policy="inspect",
        )


async def _preflight_submit_share_payload(
    client: ShareWorkerClientLike,
    report: SharePayload,
    *,
    label: str,
    ensure_loaded: Callable[[], Awaitable[None]],
    logger: Logger,
    now: Callable[[], float],
) -> OperationOutcome | None:
    """Run the shared preflight checks before the submit attempt loop."""
    await ensure_loaded()

    if backoff_active(next_upload_attempt_at=client.next_upload_attempt_at, now=now):
        return build_operation_outcome(kind="skipped", reason_code="backoff_active")

    if has_valid_installation_id(report):
        return None

    logger.warning("%s upload skipped: missing installation_id", label)
    return build_operation_outcome(
        kind="failed",
        reason_code="missing_installation_id",
        failure_origin=_SHARE_SUBMIT_ORIGIN,
        error_type="MissingInstallationId",
        failure_category="protocol",
        handling_policy="inspect",
    )


async def _refresh_submit_token_if_due(
    client: ShareWorkerClientLike,
    session: aiohttp.ClientSession,
    *,
    now: Callable[[], float],
) -> OperationOutcome | None:
    """Refresh the install token when the cached schedule says it is due."""
    if not refresh_due(
        install_token=client.install_token,
        token_refresh_after=client.token_refresh_after,
        token_expires_at=client.token_expires_at,
        now_seconds=int(now()),
    ):
        return None

    refresh_outcome = await client.refresh_install_token_with_outcome(session)
    if refresh_outcome.is_success:
        return None
    return refresh_outcome
