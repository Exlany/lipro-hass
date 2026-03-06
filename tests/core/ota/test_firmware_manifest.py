"""Tests for firmware manifest loading helpers."""

from __future__ import annotations

import asyncio
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.lipro import firmware_manifest


def _response_context(response: MagicMock) -> AsyncMock:
    context = AsyncMock()
    context.__aenter__ = AsyncMock(return_value=response)
    context.__aexit__ = AsyncMock(return_value=False)
    return context


def _response(
    *,
    status: int,
    payload: dict[str, Any] | None = None,
    json_side_effect: Exception | None = None,
) -> MagicMock:
    response = MagicMock()
    response.status = status
    response.headers = {}
    if json_side_effect is not None:
        response.json = AsyncMock(side_effect=json_side_effect)
    else:
        response.json = AsyncMock(return_value=(payload or {}))
    return response


@pytest.fixture(autouse=True)
def _reset_remote_manifest_state() -> Generator[None]:
    firmware_manifest.load_verified_firmware_manifest.cache_clear()
    firmware_manifest._REMOTE_MANIFEST_STATE.time = firmware_manifest._TIME_MIN_UTC
    firmware_manifest._REMOTE_MANIFEST_STATE.data = (frozenset(), {})
    firmware_manifest._REMOTE_MANIFEST_LOCK = asyncio.Lock()
    yield
    firmware_manifest.load_verified_firmware_manifest.cache_clear()
    firmware_manifest._REMOTE_MANIFEST_STATE.time = firmware_manifest._TIME_MIN_UTC
    firmware_manifest._REMOTE_MANIFEST_STATE.data = (frozenset(), {})
    firmware_manifest._REMOTE_MANIFEST_LOCK = asyncio.Lock()


def test_load_verified_firmware_manifest_uses_lru_cache() -> None:
    expected = (frozenset({"8.0.0"}), {"light": frozenset({"8.0.0"})})

    with patch(
        "custom_components.lipro.firmware_manifest.load_verified_firmware_manifest_file",
        return_value=expected,
    ) as loader:
        assert firmware_manifest.load_verified_firmware_manifest() == expected
        assert firmware_manifest.load_verified_firmware_manifest() == expected

    loader.assert_called_once()
    assert loader.call_args.args[0].name == "firmware_support_manifest.json"
    assert callable(loader.call_args.kwargs["on_error"])


@pytest.mark.asyncio
async def test_async_load_remote_manifest_returns_cached_data_within_ttl() -> None:
    now = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    cached_data = (frozenset({"7.1.0"}), {"light": frozenset({"7.1.0"})})
    firmware_manifest._REMOTE_MANIFEST_STATE.time = now
    firmware_manifest._REMOTE_MANIFEST_STATE.data = cached_data

    with (
        patch(
            "custom_components.lipro.firmware_manifest.dt_util.utcnow",
            return_value=now + timedelta(minutes=5),
        ),
        patch(
            "custom_components.lipro.firmware_manifest.async_get_clientsession"
        ) as get_session,
    ):
        result = await firmware_manifest.async_load_remote_firmware_manifest(
            MagicMock()
        )

    assert result == cached_data
    get_session.assert_not_called()


@pytest.mark.asyncio
async def test_async_load_remote_manifest_rechecks_cache_inside_lock() -> None:
    first_now = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    refreshed_data = (frozenset({"9.0.1"}), {"switch": frozenset({"9.0.1"})})
    firmware_manifest._REMOTE_MANIFEST_STATE.time = first_now - timedelta(hours=1)
    firmware_manifest._REMOTE_MANIFEST_STATE.data = (frozenset({"1.0.0"}), {})

    calls = 0

    def _utcnow() -> datetime:
        nonlocal calls
        calls += 1
        if calls == 1:
            return first_now
        refreshed_time = first_now + timedelta(minutes=1)
        firmware_manifest._REMOTE_MANIFEST_STATE.time = refreshed_time
        firmware_manifest._REMOTE_MANIFEST_STATE.data = refreshed_data
        return refreshed_time

    with (
        patch(
            "custom_components.lipro.firmware_manifest.dt_util.utcnow",
            side_effect=_utcnow,
        ),
        patch(
            "custom_components.lipro.firmware_manifest.async_get_clientsession"
        ) as get_session,
    ):
        result = await firmware_manifest.async_load_remote_firmware_manifest(
            MagicMock()
        )

    assert result == refreshed_data
    get_session.assert_not_called()


@pytest.mark.asyncio
async def test_async_load_remote_manifest_updates_cache_on_remote_success() -> None:
    now = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    parsed_data = (
        frozenset({"8.0.0"}),
        {"21p3": frozenset({"8.0.0"})},
    )
    firmware_manifest._REMOTE_MANIFEST_STATE.time = now - timedelta(hours=1)

    session = MagicMock()
    session.get = MagicMock(
        side_effect=[
            _response_context(_response(status=500)),
            _response_context(
                _response(status=200, payload={"verified_versions": ["8.0.0"]})
            ),
        ]
    )

    with (
        patch(
            "custom_components.lipro.firmware_manifest.dt_util.utcnow", return_value=now
        ),
        patch(
            "custom_components.lipro.firmware_manifest.async_get_clientsession",
            return_value=session,
        ),
        patch(
            "custom_components.lipro.firmware_manifest.parse_verified_firmware_manifest_payload",
            return_value=parsed_data,
        ) as parse_payload,
    ):
        result = await firmware_manifest.async_load_remote_firmware_manifest(
            MagicMock()
        )

    assert result == parsed_data
    assert firmware_manifest._REMOTE_MANIFEST_STATE.data == parsed_data
    assert firmware_manifest._REMOTE_MANIFEST_STATE.time == now
    assert session.get.call_count == 2
    parse_payload.assert_called_once_with({"verified_versions": ["8.0.0"]})


@pytest.mark.asyncio
async def test_async_load_remote_manifest_returns_cached_data_on_remote_errors() -> (
    None
):
    now = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    cached_data = (frozenset({"6.0.0"}), {"curtain": frozenset({"6.0.0"})})
    firmware_manifest._REMOTE_MANIFEST_STATE.time = now - timedelta(hours=2)
    firmware_manifest._REMOTE_MANIFEST_STATE.data = cached_data

    session = MagicMock()
    session.get = MagicMock(side_effect=[aiohttp.ClientError("boom"), TimeoutError()])

    with (
        patch(
            "custom_components.lipro.firmware_manifest.dt_util.utcnow", return_value=now
        ),
        patch(
            "custom_components.lipro.firmware_manifest.async_get_clientsession",
            return_value=session,
        ),
    ):
        result = await firmware_manifest.async_load_remote_firmware_manifest(
            MagicMock()
        )

    assert result == cached_data
    assert firmware_manifest._REMOTE_MANIFEST_STATE.data == cached_data
    assert firmware_manifest._REMOTE_MANIFEST_STATE.time == now
    assert session.get.call_count == 2


@pytest.mark.asyncio
async def test_async_load_remote_manifest_keeps_cached_data_when_payload_empty() -> (
    None
):
    now = datetime(2026, 1, 1, 0, 0, tzinfo=UTC)
    cached_data = (frozenset({"6.2.0"}), {"fan": frozenset({"6.2.0"})})
    firmware_manifest._REMOTE_MANIFEST_STATE.time = now - timedelta(hours=2)
    firmware_manifest._REMOTE_MANIFEST_STATE.data = cached_data

    session = MagicMock()
    session.get = MagicMock(
        side_effect=[
            _response_context(_response(status=200, payload={"verified_versions": []})),
            _response_context(_response(status=503)),
        ]
    )

    with (
        patch(
            "custom_components.lipro.firmware_manifest.dt_util.utcnow", return_value=now
        ),
        patch(
            "custom_components.lipro.firmware_manifest.async_get_clientsession",
            return_value=session,
        ),
        patch(
            "custom_components.lipro.firmware_manifest.parse_verified_firmware_manifest_payload",
            return_value=(frozenset(), {}),
        ) as parse_payload,
    ):
        result = await firmware_manifest.async_load_remote_firmware_manifest(
            MagicMock()
        )

    assert result == cached_data
    assert firmware_manifest._REMOTE_MANIFEST_STATE.data == cached_data
    assert firmware_manifest._REMOTE_MANIFEST_STATE.time == now
    parse_payload.assert_called_once_with({"verified_versions": []})
