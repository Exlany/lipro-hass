"""Targeted coverage tests for anonymous_share missing branches.

These tests intentionally cover specific branches reported as missing by
--cov-report=term-missing:skip-covered.
"""

from __future__ import annotations

from typing import cast
from unittest.mock import MagicMock

import aiohttp
import pytest

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.core.anonymous_share import manager as manager_module
from custom_components.lipro.core.anonymous_share.collector import (
    AnonymousShareCollector,
)
from custom_components.lipro.core.anonymous_share.manager import AnonymousShareManager
from custom_components.lipro.core.anonymous_share.share_client import ShareWorkerClient


def test_collector_parse_and_command_errors_ignored_when_disabled() -> None:
    """collector.py:176,200 - early-return branches when error collection disabled."""
    collector = AnonymousShareCollector()  # disabled by default

    collector.record_parse_error("loc", ValueError("bad"), input_sample="x")
    collector.record_command_error("cmd", "light", 500, "boom", params="p=1")

    assert list(collector.errors) == []


def test_manager_get_pending_report_includes_method_prefix_and_count_suffix() -> None:
    """manager.py:215, collector.py:161, models.py:27."""
    mgr = AnonymousShareManager()
    mgr.set_enabled(
        True,
        error_reporting=True,
        installation_id="test-id",
        ha_version="2026.1.0",
    )

    # Record the exact same error twice to trigger the duplicate-merge count path.
    mgr.record_api_error(endpoint="/api/x", code=500, message="fail", method="GET")
    mgr.record_api_error(endpoint="/api/x", code=500, message="fail", method="GET")

    report = mgr.get_pending_report()
    assert report is not None
    assert report["installation_id"] == "test-id"
    assert report["error_count"] == 1

    # method prefix (collector.py:161) + count suffix (models.py:27)
    msg = report["errors"][0]["message"]
    assert "[500] GET /api/x: fail" in msg
    assert msg.endswith(" (x2)")


def test_get_anonymous_share_manager_without_hass_creates_singleton_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """manager.py:340 - branch when global singleton is missing."""
    monkeypatch.setattr(manager_module, "_share_manager", None)

    mgr1 = manager_module.get_anonymous_share_manager()
    mgr2 = manager_module.get_anonymous_share_manager()

    assert isinstance(mgr1, AnonymousShareManager)
    assert mgr1 is mgr2




def test_get_anonymous_share_manager_with_corrupt_domain_data_does_not_crash(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """manager.py - corrupted hass domain data falls back to root-scoped views."""
    monkeypatch.setattr(manager_module, "_share_manager", None)

    hass = MagicMock()
    hass.data = {DOMAIN: "not-a-dict"}

    aggregate = manager_module.get_anonymous_share_manager(hass)
    scoped = manager_module.get_anonymous_share_manager(hass, entry_id="entry-1")

    assert isinstance(aggregate, AnonymousShareManager)
    assert isinstance(scoped, AnonymousShareManager)
    assert hass.data[DOMAIN] == "not-a-dict"

def test_share_client_parse_retry_after_returns_none_when_missing_header() -> None:
    """share_client.py:70 - no Retry-After header present."""
    assert ShareWorkerClient.parse_retry_after({}) is None


@pytest.mark.asyncio
async def test_share_client_refresh_install_token_falls_back_to_false_on_non_200() -> (
    None
):
    """share_client.py:145 - default False return for non-200/401/429 responses."""

    class _FakeResponse:
        def __init__(self) -> None:
            self.status = 500
            self.headers: dict[str, str] = {}

        async def json(self, *, content_type=None):
            return {"code": "SOME_OTHER_ERROR"}

    class _FakeContext:
        def __init__(self, response: _FakeResponse) -> None:
            self._response = response

        async def __aenter__(self) -> _FakeResponse:
            return self._response

        async def __aexit__(self, exc_type, exc, tb) -> bool:
            return False

    class _FakeSession:
        def __init__(self, response: _FakeResponse) -> None:
            self._response = response

        def post(self, *args, **kwargs):
            return _FakeContext(self._response)

    client = ShareWorkerClient()
    client.install_token = "tok"
    client.next_upload_attempt_at = 0.0

    session = cast(aiohttp.ClientSession, _FakeSession(_FakeResponse()))
    assert await client.refresh_install_token(session) is False
