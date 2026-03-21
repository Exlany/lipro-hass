"""Tests for request-policy pacing and rate-limit helpers."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro.const.api import MAX_RATE_LIMIT_RETRIES, MAX_RETRY_AFTER
from custom_components.lipro.core.api import request_policy as request_policy_module
from custom_components.lipro.core.api.errors import LiproApiError, LiproRateLimitError
from custom_components.lipro.core.api.request_policy import (
    COMMAND_PACING_CACHE_MAX_SIZE,
    RequestPolicy,
    compute_rate_limit_wait_time,
)


@pytest.mark.asyncio
async def test_request_policy_handle_rate_limit_raises_after_retry_budget() -> None:
    policy = RequestPolicy()

    with pytest.raises(LiproRateLimitError, match="Rate limited after"):
        await policy.handle_rate_limit(
            "/v1/devices",
            {"Retry-After": "5"},
            MAX_RATE_LIMIT_RETRIES,
        )


@pytest.mark.asyncio
async def test_request_policy_handle_rate_limit_waits_for_computed_backoff() -> None:
    policy = RequestPolicy()

    with (
        patch(
            "custom_components.lipro.core.api.request_policy.compute_rate_limit_wait_time",
            return_value=1.25,
        ),
        patch(
            "custom_components.lipro.core.api.request_policy.asyncio.sleep",
            new=AsyncMock(),
        ) as sleep,
    ):
        wait_time = await policy.handle_rate_limit(
            "/v1/devices",
            {"Retry-After": "1"},
            1,
        )

    assert wait_time == 1.25
    sleep.assert_awaited_once_with(1.25)


def test_request_policy_is_command_busy_error_false_for_empty_message() -> None:
    assert RequestPolicy.is_command_busy_error(LiproApiError("", code=500)) is False


@pytest.mark.parametrize(
    ("retry_after", "retry_count", "expected"),
    [
        (999999.0, 0, MAX_RETRY_AFTER),
        (5.0, 0, 5.0),
        (None, 0, 1.0),
        (None, 1, 2.0),
        (None, 2, 4.0),
        (-10.0, 0, 0.1),
        (0.0, 3, 0.1),
    ],
)
def test_compute_rate_limit_wait_time_edges(
    retry_after: float | None,
    retry_count: int,
    expected: float,
) -> None:
    assert (
        compute_rate_limit_wait_time(
            retry_after=retry_after,
            retry_count=retry_count,
            max_retry_after=MAX_RETRY_AFTER,
        )
        == expected
    )


def test_lipro_rate_limit_error_preserves_retry_after() -> None:
    error = LiproRateLimitError("Rate limited", retry_after=30.0)

    assert error.retry_after == 30.0
    assert str(error) == "Rate limited"
    assert error.code == 429


def test_lipro_rate_limit_error_defaults_retry_after_to_none() -> None:
    error = LiproRateLimitError("Rate limited")

    assert error.retry_after is None
    assert isinstance(error, LiproApiError)


def test_parse_retry_after_seconds() -> None:
    result = RequestPolicy.parse_retry_after({"Retry-After": "30"})
    assert result == 30.0


def test_parse_retry_after_float() -> None:
    result = RequestPolicy.parse_retry_after({"Retry-After": "1.5"})
    assert result == 1.5


def test_parse_retry_after_missing() -> None:
    result = RequestPolicy.parse_retry_after({})
    assert result is None


def test_parse_retry_after_invalid() -> None:
    result = RequestPolicy.parse_retry_after({"Retry-After": "invalid"})
    assert result is None


def test_parse_retry_after_http_date() -> None:
    future = datetime.now(UTC) + timedelta(seconds=60)
    http_date = future.strftime("%a, %d %b %Y %H:%M:%S GMT")
    result = RequestPolicy.parse_retry_after({"Retry-After": http_date})
    assert result is not None
    assert 55 <= result <= 65


def test_parse_retry_after_http_date_without_timezone_assumes_utc() -> None:
    future = datetime.now(UTC) + timedelta(seconds=60)
    naive_future = future.replace(tzinfo=None)
    http_date = naive_future.strftime("%a, %d %b %Y %H:%M:%S")
    result = RequestPolicy.parse_retry_after({"Retry-After": http_date})
    assert result is not None
    assert 55 <= result <= 65


def test_parse_retry_after_lowercase_header() -> None:
    result = RequestPolicy.parse_retry_after({"retry-after": "10"})
    assert result == 10.0


def test_parse_retry_after_negative() -> None:
    result = RequestPolicy.parse_retry_after({"Retry-After": "-5"})
    assert result == -5.0


def test_parse_retry_after_zero() -> None:
    result = RequestPolicy.parse_retry_after({"Retry-After": "0"})
    assert result == 0.0


def test_request_policy_change_state_command_and_normalize_target_helpers() -> None:
    assert RequestPolicy.is_change_state_command("change_state") is True
    assert RequestPolicy.is_change_state_command("POWER_ON") is False
    assert RequestPolicy.normalize_pacing_target("  TaRgEt  ") == "target"


def test_enforce_command_pacing_cache_limit_handles_empty_last_change_state_at_and_drops_idle_lock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(request_policy_module, "COMMAND_PACING_CACHE_MAX_SIZE", 0)

    policy = RequestPolicy()
    target = "target"
    policy.change_state_min_interval[target] = 0.2
    policy.change_state_busy_count[target] = 1
    policy.command_pacing_target_locks[target] = asyncio.Lock()

    policy.enforce_command_pacing_cache_limit()

    assert target not in policy.change_state_min_interval
    assert target not in policy.change_state_busy_count
    assert target not in policy.command_pacing_target_locks


def test_enforce_command_pacing_cache_limit_drops_oldest_targets() -> None:
    policy = RequestPolicy()
    total = COMMAND_PACING_CACHE_MAX_SIZE + 2
    for idx in range(total):
        key = f"target_{idx}"
        policy.last_change_state_at[key] = float(idx)
        policy.change_state_min_interval[key] = 0.2
        policy.change_state_busy_count[key] = 1

    policy.enforce_command_pacing_cache_limit()

    assert len(policy.last_change_state_at) == COMMAND_PACING_CACHE_MAX_SIZE
    assert len(policy.change_state_min_interval) == COMMAND_PACING_CACHE_MAX_SIZE
    assert len(policy.change_state_busy_count) == COMMAND_PACING_CACHE_MAX_SIZE
    assert "target_0" not in policy.last_change_state_at
    assert "target_1" not in policy.last_change_state_at


@pytest.mark.asyncio
async def test_enforce_command_pacing_cache_limit_keeps_lock_with_waiters() -> None:
    policy = RequestPolicy()
    total = COMMAND_PACING_CACHE_MAX_SIZE + 1
    for idx in range(total):
        key = f"target_{idx}"
        policy.last_change_state_at[key] = float(idx)
        policy.change_state_min_interval[key] = 0.2
        policy.change_state_busy_count[key] = 1

    lock = asyncio.Lock()
    await lock.acquire()
    waiter = asyncio.create_task(lock.acquire())
    await asyncio.sleep(0)
    lock.release()

    assert lock.locked() is False
    assert bool(getattr(lock, "_waiters", None)) is True

    policy.command_pacing_target_locks["target_0"] = lock
    policy.enforce_command_pacing_cache_limit()

    assert policy.command_pacing_target_locks["target_0"] is lock

    await waiter
    lock.release()


@pytest.mark.asyncio
async def test_throttle_change_state_waits_for_same_target() -> None:
    policy = RequestPolicy()
    policy.last_change_state_at["mesh_group_10001"] = 100.0

    with (
        patch(
            "custom_components.lipro.core.api.request_policy.monotonic",
            side_effect=[100.05, 100.25],
        ),
        patch(
            "custom_components.lipro.core.api.request_policy.asyncio.sleep",
            new_callable=AsyncMock,
        ) as sleep,
    ):
        await policy.throttle_change_state("mesh_group_10001", "CHANGE_STATE")

    sleep.assert_awaited_once()
    await_args = sleep.await_args
    assert await_args is not None
    wait_time = await_args.args[0]
    assert 0 < wait_time <= 0.2
    assert policy.last_change_state_at["mesh_group_10001"] == 100.25


@pytest.mark.asyncio
async def test_throttle_change_state_skips_non_change_state() -> None:
    policy = RequestPolicy()
    policy.last_change_state_at["mesh_group_10001"] = 100.0

    with patch(
        "custom_components.lipro.core.api.request_policy.asyncio.sleep",
        new_callable=AsyncMock,
    ) as sleep:
        await policy.throttle_change_state("mesh_group_10001", "POWER_ON")

    sleep.assert_not_awaited()


@pytest.mark.asyncio
async def test_record_change_state_busy_increases_adaptive_interval() -> None:
    policy = RequestPolicy()

    interval1, count1 = await policy.record_change_state_busy(
        "mesh_group_10001", "CHANGE_STATE"
    )
    interval2, count2 = await policy.record_change_state_busy(
        "mesh_group_10001", "CHANGE_STATE"
    )

    assert interval1 > 0.2
    assert interval2 > interval1
    assert count1 == 1
    assert count2 == 2
    assert policy.change_state_busy_count["mesh_group_10001"] == 2


@pytest.mark.asyncio
async def test_record_change_state_success_recovers_adaptive_interval() -> None:
    policy = RequestPolicy()

    await policy.record_change_state_busy("mesh_group_10001", "CHANGE_STATE")
    busy_interval = policy.change_state_min_interval["mesh_group_10001"]

    await policy.record_change_state_success("mesh_group_10001", "CHANGE_STATE")
    recovered_interval = policy.change_state_min_interval["mesh_group_10001"]

    assert recovered_interval >= 0.2
    assert recovered_interval < busy_interval
    assert "mesh_group_10001" not in policy.change_state_busy_count


@pytest.mark.asyncio
async def test_record_change_state_busy_skips_non_change_state() -> None:
    policy = RequestPolicy()

    interval, count = await policy.record_change_state_busy(
        "mesh_group_10001", "POWER_ON"
    )

    assert interval == 0.2
    assert count == 0
    assert policy.change_state_min_interval == {}
    assert policy.change_state_busy_count == {}


@pytest.mark.asyncio
async def test_record_change_state_busy_ignores_blank_target() -> None:
    policy = RequestPolicy()

    interval, count = await policy.record_change_state_busy("   ", "CHANGE_STATE")

    assert interval == 0.2
    assert count == 0
    assert policy.change_state_min_interval == {}


@pytest.mark.asyncio
async def test_record_change_state_success_ignores_blank_target() -> None:
    policy = RequestPolicy()
    policy.change_state_min_interval["target"] = 0.6
    policy.change_state_busy_count["target"] = 2

    await policy.record_change_state_success("   ", "CHANGE_STATE")

    assert policy.change_state_min_interval["target"] == 0.6
    assert policy.change_state_busy_count["target"] == 2


@pytest.mark.asyncio
async def test_throttle_change_state_ignores_blank_target() -> None:
    policy = RequestPolicy()

    with patch(
        "custom_components.lipro.core.api.request_policy.asyncio.sleep",
        new_callable=AsyncMock,
    ) as sleep:
        await policy.throttle_change_state("   ", "CHANGE_STATE")

    sleep.assert_not_awaited()


@pytest.mark.asyncio
async def test_iot_request_with_busy_retry_non_mapping_success_returns_empty() -> None:
    policy = RequestPolicy()

    result = await policy.iot_request_with_busy_retry(
        "/test",
        {},
        target_id="03ab5ccd7caaaaaa",
        command="POWER_ON",
        iot_request=AsyncMock(return_value="ok"),
        logger=MagicMock(),
    )

    assert result == {}


@pytest.mark.asyncio
async def test_iot_request_with_busy_retry_retries_then_succeeds() -> None:
    policy = RequestPolicy()
    iot_request = AsyncMock(
        side_effect=[
            LiproApiError("busy", code=250001),
            {"pushSuccess": True},
        ]
    )

    with patch(
        "custom_components.lipro.core.api.request_policy.asyncio.sleep",
        new=AsyncMock(),
    ) as sleep:
        result = await policy.iot_request_with_busy_retry(
            "/v2/device/send",
            {"command": "CHANGE_STATE"},
            target_id="mesh_group_10001",
            command="CHANGE_STATE",
            iot_request=iot_request,
            logger=MagicMock(),
        )

    assert result == {"pushSuccess": True}
    assert iot_request.await_count == 2
    assert any(call.args == (0.25,) for call in sleep.await_args_list)


@pytest.mark.asyncio
async def test_iot_request_with_busy_retry_non_busy_error_raises() -> None:
    policy = RequestPolicy()

    with pytest.raises(LiproApiError, match="offline"):
        await policy.iot_request_with_busy_retry(
            "/v2/device/send",
            {"command": "POWER_ON"},
            target_id="03ab5ccd7caaaaaa",
            command="POWER_ON",
            iot_request=AsyncMock(side_effect=LiproApiError("offline", code=140003)),
            logger=MagicMock(),
        )


@pytest.mark.asyncio
async def test_iot_request_with_busy_retry_exhausted_raises() -> None:
    policy = RequestPolicy()
    iot_request = AsyncMock(side_effect=LiproApiError("busy", code=250001))

    with pytest.raises(LiproApiError, match="busy"):
        await policy.iot_request_with_busy_retry(
            "/v2/device/send",
            {"command": "CHANGE_STATE"},
            target_id="mesh_group_10001",
            command="CHANGE_STATE",
            iot_request=iot_request,
            logger=MagicMock(),
        )

    assert iot_request.await_count == 4
