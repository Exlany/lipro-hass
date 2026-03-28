"""Tests for AnonymousShareManager."""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.lipro.core.anonymous_share.const import (
    MAX_PENDING_DEVICES,
    SHARE_API_KEY,
)
from custom_components.lipro.core.anonymous_share.manager import AnonymousShareManager
from custom_components.lipro.core.anonymous_share.share_client import ShareWorkerClient
from custom_components.lipro.core.telemetry.models import build_operation_outcome

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
from .support import _make_manager, _make_mock_device


class TestSubmitLogic:
    """Tests for submit_if_needed interval and threshold logic."""

    async def test_submit_if_needed_respects_interval(self):
        mgr = _make_manager()
        # Add enough devices to trigger upload threshold
        for i in range(MAX_PENDING_DEVICES):
            d = _make_mock_device(iot_name=f"device_{i}")
            mgr.record_device(d)

        session = MagicMock()
        mock_response = MagicMock()
        mock_response.status = 200

        # Create a proper async context manager for session.post()
        ctx = AsyncMock()
        ctx.__aenter__ = AsyncMock(return_value=mock_response)
        ctx.__aexit__ = AsyncMock(return_value=False)
        session.post = MagicMock(return_value=ctx)

        # Last upload was long ago -> should trigger
        mgr._last_upload_time = 0
        with patch.object(mgr, "_save_reported_devices"):
            result = await mgr.submit_if_needed(session)
        assert result is True

    async def test_submit_if_needed_skips_when_too_soon(self):
        mgr = _make_manager()
        # Add a device but not enough to hit threshold
        device = _make_mock_device(iot_name="lipro_led")
        mgr.record_device(device)

        session = AsyncMock()

        # Last upload was just now, and we don't have enough data
        mgr._last_upload_time = time.time()
        result = await mgr.submit_if_needed(session)
        # Should return True (no submission needed) without calling session
        assert result is True
        session.post.assert_not_called()

    async def test_submit_report_checks_interval(self):
        mgr = _make_manager()
        device = _make_mock_device(iot_name="lipro_led")
        mgr.record_device(device)

        session = AsyncMock()

        # Set last upload to now -> interval not passed
        mgr._last_upload_time = time.time()
        result = await mgr.submit_report(session, force=False)
        # Should skip upload and return True
        assert result is True
        session.post.assert_not_called()

    async def test_submit_disabled_returns_false(self):
        mgr = _make_manager(enabled=False)
        session = AsyncMock()
        result = await mgr.submit_report(session)
        assert result is False

    async def test_submit_empty_returns_true(self):
        mgr = _make_manager()
        session = AsyncMock()
        result = await mgr.submit_report(session)
        # No data to report -> True
        assert result is True

    async def test_submit_report_non_200_returns_false(self):
        mgr = _make_manager()
        mgr.record_device(_make_mock_device(iot_name="lipro_led"))

        session = MagicMock()
        response = MagicMock()
        response.status = 500
        context = AsyncMock()
        context.__aenter__ = AsyncMock(return_value=response)
        context.__aexit__ = AsyncMock(return_value=False)
        session.post = MagicMock(return_value=context)

        assert await mgr.submit_report(session, force=True) is False

    async def test_submit_report_timeout_returns_false(self):
        mgr = _make_manager()
        mgr.record_device(_make_mock_device(iot_name="lipro_led"))

        session = MagicMock()
        session.post = MagicMock(side_effect=TimeoutError)

        assert await mgr.submit_report(session, force=True) is False

    async def test_submit_report_client_error_returns_false(self):
        mgr = _make_manager()
        mgr.record_device(_make_mock_device(iot_name="lipro_led"))

        session = MagicMock()
        session.post = MagicMock(side_effect=aiohttp.ClientError("network down"))

        assert await mgr.submit_report(session, force=True) is False

    @pytest.mark.parametrize("exc", [OSError("disk"), ValueError("bad")])
    async def test_submit_report_unexpected_error_returns_false(self, exc):
        mgr = _make_manager()
        mgr.record_device(_make_mock_device(iot_name="lipro_led"))

        session = MagicMock()
        session.post = MagicMock(side_effect=exc)

        assert await mgr.submit_report(session, force=True) is False

    async def test_submit_if_needed_disabled_returns_true(self):
        mgr = _make_manager(enabled=False)
        session = AsyncMock()
        assert await mgr.submit_if_needed(session) is True
        session.post.assert_not_called()

    async def test_submit_developer_feedback_success(self):
        """Developer feedback submit should not require anonymous-share enabled."""
        mgr = _make_manager(enabled=False)
        mgr._ha_version = "2026.2.0"

        session = MagicMock()
        response = MagicMock()
        response.status = 200
        context = AsyncMock()
        context.__aenter__ = AsyncMock(return_value=response)
        context.__aexit__ = AsyncMock(return_value=False)
        session.post = MagicMock(return_value=context)

        result = await mgr.submit_developer_feedback(
            session,
            {"source": "test", "reports": [{"phone": "13800000000"}]},
        )

        assert result is True
        session.post.assert_called_once()
        payload = session.post.call_args.kwargs["json"]
        assert payload["report_version"] == "1.2"
        assert payload["integration_version"]
        assert payload["devices"] == []
        assert payload["errors"] == []
        assert "developer_feedback" in payload

    async def test_submit_developer_feedback_non_200_returns_false(self):
        mgr = _make_manager(enabled=False)
        session = MagicMock()
        response = MagicMock()
        response.status = 500
        context = AsyncMock()
        context.__aenter__ = AsyncMock(return_value=response)
        context.__aexit__ = AsyncMock(return_value=False)
        session.post = MagicMock(return_value=context)

        result = await mgr.submit_developer_feedback(
            session,
            {"source": "test", "reports": []},
        )
        assert result is False

    def test_build_upload_headers_uses_static_api_key(self):
        headers = ShareWorkerClient.build_upload_headers()
        assert headers["X-API-Key"] == SHARE_API_KEY

    def test_build_upload_headers_includes_bearer_token(self):
        headers = ShareWorkerClient.build_upload_headers(install_token="abc")
        assert headers["Authorization"] == "Bearer abc"

    async def test_submit_report_keeps_install_token_in_memory_only(self, tmp_path):
        mgr = _make_manager()
        mgr._storage_path = str(tmp_path)
        mgr._cache_loaded = True
        mgr.record_device(_make_mock_device(iot_name="lipro_led"))

        session = MagicMock()
        response = MagicMock()
        response.status = 200
        response.headers = {}
        response.json = AsyncMock(
            return_value={
                "success": True,
                "code": "REPORT_ACCEPTED",
                "install_token": "tok-1",
                "token_expires_at": 123,
                "token_refresh_after": 100,
            }
        )
        context = AsyncMock()
        context.__aenter__ = AsyncMock(return_value=response)
        context.__aexit__ = AsyncMock(return_value=False)
        session.post = MagicMock(return_value=context)

        assert await mgr.submit_report(session, force=True) is True
        assert mgr._install_token == "tok-1"
        cache = tmp_path / ".lipro_share_auth.json"
        assert cache.exists() is False


# ===========================================================================
# TestGetAnonymousShareManager
# ===========================================================================

@pytest.mark.asyncio
async def test_submit_developer_feedback_matches_boundary_fixture() -> None:
    from custom_components.lipro.core.anonymous_share.report_builder import (
        canonicalize_generated_payload,
    )
    from tests.helpers.external_boundary_fixtures import load_external_boundary_fixture

    mgr = AnonymousShareManager()
    mgr.set_enabled(True, error_reporting=True, installation_id="install-001")
    mgr._ha_version = "2026.3.0"
    session = MagicMock()
    submit_share_payload_with_outcome = AsyncMock(
        return_value=build_operation_outcome(kind="success", reason_code="submitted")
    )
    mgr._share_client = MagicMock(
        submit_share_payload_with_outcome=submit_share_payload_with_outcome
    )

    result = await mgr.submit_developer_feedback(
        session,
        {
            "note": "manual run",
            "requested_entry_id": "entry-2",
            "reports": [
                {
                    "name": "Bedroom Gateway",
                    "iotName": "lipro_gateway",
                    "deviceName": "Bedroom Gateway Alias",
                    "roomName": "Master Bedroom",
                    "productName": "Evening Scene",
                    "panel_capability_snapshot": {
                        "panels": [
                            {
                                "name": "Wall Panel",
                                "iot_name": "21JD",
                                "panel_info": [{"keyName": "Bedside"}],
                            }
                        ]
                    },
                    "ir_remote_inventory_snapshot": {
                        "gateways": [
                            {
                                "name": "Main Gateway",
                                "rc_list": [
                                    {
                                        "name": "Fan Light Remote",
                                        "address": "masked-remote-address",
                                    }
                                ],
                            }
                        ],
                        "ir_remote_devices": [
                            {
                                "name": "TV Remote",
                                "gateway_device_id": "masked-gateway-id",
                            }
                        ],
                    },
                }
            ],
        },
    )

    assert result is True
    assert submit_share_payload_with_outcome.await_args is not None
    report = submit_share_payload_with_outcome.await_args.args[1]
    assert canonicalize_generated_payload(report) == load_external_boundary_fixture(
        "share_worker",
        "developer_feedback_report.canonical.json",
    )


@pytest.mark.asyncio
async def test_aggregate_submit_report_skips_disabled_scopes() -> None:
    root_manager = AnonymousShareManager()
    default_manager = root_manager.for_scope("__default__")
    disabled_manager = root_manager.for_scope("entry-disabled")

    default_manager.set_enabled(True, installation_id="install-default")
    disabled_manager.set_enabled(False, installation_id="install-disabled")
    default_manager.record_device(_make_mock_device(iot_name="lipro_led"))

    response = MagicMock()
    response.status = 200
    context = AsyncMock()
    context.__aenter__ = AsyncMock(return_value=response)
    context.__aexit__ = AsyncMock(return_value=False)
    session = MagicMock(post=MagicMock(return_value=context))

    aggregate_manager = root_manager.aggregate_view()

    assert await aggregate_manager.submit_report(session, force=True) is True
    session.post.assert_called_once()


@pytest.mark.asyncio
async def test_aggregate_developer_feedback_uses_primary_scope_client_without_overwriting_default_outcome() -> None:
    root_manager = AnonymousShareManager()
    default_manager = root_manager.for_scope("__default__")
    primary_manager = root_manager.for_scope("entry-1")

    default_manager.set_enabled(False, installation_id="install-default")
    default_manager.set_last_submit_outcome(
        build_operation_outcome(kind="failed", reason_code="default_scope_outcome")
    )
    primary_manager.set_enabled(True, installation_id="install-entry-1")
    primary_manager._ha_version = "2026.3.0"

    default_submit = AsyncMock(
        return_value=build_operation_outcome(kind="failed", reason_code="default_client")
    )
    primary_submit = AsyncMock(
        return_value=build_operation_outcome(kind="success", reason_code="submitted")
    )
    default_manager._share_client = MagicMock(
        submit_share_payload_with_outcome=default_submit
    )
    primary_manager._share_client = MagicMock(
        submit_share_payload_with_outcome=primary_submit
    )

    aggregate_manager = root_manager.aggregate_view()

    result = await aggregate_manager.submit_developer_feedback(
        MagicMock(),
        {"source": "test", "reports": []},
    )

    assert result is True
    primary_submit.assert_awaited_once()
    default_submit.assert_not_awaited()
    assert aggregate_manager.last_submit_outcome is not None
    assert aggregate_manager.last_submit_outcome.is_success is True
    assert default_manager.last_submit_outcome is not None
    assert default_manager.last_submit_outcome.reason_code == "default_scope_outcome"
