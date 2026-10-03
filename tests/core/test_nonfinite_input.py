"""Malformed numeric inputs must use safe option and retry defaults."""

from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.core.anonymous_share.share_client import ShareWorkerClient
from custom_components.lipro.core.api.request_policy import RequestPolicy
from custom_components.lipro.core.utils.coerce import coerce_int_option


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_nonfinite_integer_option_uses_default(value) -> None:
    assert (
        coerce_int_option(
            value, option_name="request_timeout", default=30, min_value=5, max_value=60
        )
        == 30
    )


@pytest.mark.parametrize("header", ["nan", "inf", "-inf", "1e999"])
async def test_nonfinite_retry_header_uses_backoff(header) -> None:
    headers = {"Retry-After": header}
    assert ShareWorkerClient.parse_retry_after(headers) is None
    sleep = AsyncMock()
    wait = await RequestPolicy().handle_rate_limit("/test", headers, 1, sleep=sleep)
    assert wait == 2.0
    sleep.assert_awaited_once_with(2.0)
