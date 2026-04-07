"""Tests for AnonymousShareManager."""

from __future__ import annotations

from typing import cast
from unittest.mock import MagicMock

import pytest

from custom_components.lipro.core import LiproApiError
from custom_components.lipro.core.anonymous_share import (
    get_anonymous_share_manager,
    registry as manager_registry,
)
from custom_components.lipro.core.api import LiproRestFacade
from custom_components.lipro.core.api.observability import (
    record_api_error as record_observed_api_error,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class TestObservabilityScope:
    """Tests for observability routing into anonymous-share scopes."""

    def test_default_observability_path_still_records_to_default_scope(
        self, monkeypatch
    ):
        manager_registry._get_root_manager.cache_clear()
        manager = get_anonymous_share_manager()
        manager.set_enabled(True, error_reporting=True, installation_id="default")

        record_observed_api_error("/api/default", 500, "fail", method="POST")

        assert manager.pending_count == (0, 1)
        report = manager.get_pending_report()
        assert report is not None
        errors = cast(list[dict[str, object]], report["errors"])
        assert errors[0]["endpoint"] == "/api/default"

    def test_observability_entry_scope_targets_matching_manager(self, monkeypatch):
        manager_registry._get_root_manager.cache_clear()
        hass = MagicMock()
        hass.data = {}

        entry_one_manager = get_anonymous_share_manager(hass, entry_id="entry-1")
        entry_two_manager = get_anonymous_share_manager(hass, entry_id="entry-2")
        entry_one_manager.set_enabled(True, error_reporting=True, installation_id="one")
        entry_two_manager.set_enabled(True, error_reporting=True, installation_id="two")

        record_observed_api_error(
            "/api/two",
            401,
            "unauthorized",
            method="POST",
            entry_id="entry-2",
        )

        assert entry_one_manager.pending_count == (0, 0)
        assert entry_two_manager.pending_count == (0, 1)

class TestClientObservabilityScope:
    """Tests for explicit entry routing from API client errors."""

    @pytest.mark.asyncio
    async def test_client_records_api_error_with_entry_scope(self, monkeypatch) -> None:
        observed: dict[str, object] = {}

        def _capture(
            endpoint: str,
            code: str | int,
            message: str,
            method: str = "",
            *,
            entry_id: str | None = None,
        ) -> None:
            observed.update(
                {
                    "endpoint": endpoint,
                    "code": code,
                    "message": message,
                    "method": method,
                    "entry_id": entry_id,
                }
            )

        monkeypatch.setattr(
            "custom_components.lipro.core.api.auth_recovery._record_api_error",
            _capture,
        )
        client = LiproRestFacade("550e8400-e29b-41d4-a716-446655440000", entry_id="entry-2")

        with pytest.raises(LiproApiError, match="boom"):
            await client._finalize_mapping_result(
                path="/api/test",
                result={"code": 500, "message": "boom"},
                request_token=None,
                is_retry=False,
                retry_on_auth_error=False,
                retry_request=None,
                success_payload=lambda result: result,
            )

        assert observed == {
            "endpoint": "/api/test",
            "code": 500,
            "message": "boom",
            "method": "POST",
            "entry_id": "entry-2",
        }


