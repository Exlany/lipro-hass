"""Tests for status endpoint helper predicates."""

from __future__ import annotations

import pytest

from custom_components.lipro.core.api.endpoints.status import StatusEndpoints
from custom_components.lipro.core.api.errors import LiproApiError


@pytest.mark.parametrize(
    "code",
    [
        140003,
        "140003",
        " 140003 ",
        140101,
        "140101",
        " 140101 ",
        140004,
        "140004",
        " 140004 ",
        140013,
        140014,
    ],
)
def test_is_retriable_device_error_accepts_known_codes(code: int | str) -> None:
    assert StatusEndpoints.is_retriable_device_error(LiproApiError("retriable", code))


@pytest.mark.parametrize("code", [500, "500", None])
def test_is_retriable_device_error_rejects_unknown_codes(
    code: int | str | None,
) -> None:
    assert not StatusEndpoints.is_retriable_device_error(
        LiproApiError("not retriable", code)
    )
