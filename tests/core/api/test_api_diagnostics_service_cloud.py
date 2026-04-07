"""Cloud-query diagnostics API service assertions."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from custom_components.lipro.const.api import PATH_QUERY_USER_CLOUD
from custom_components.lipro.core.api.diagnostics_api_service import query_user_cloud

from .test_api_diagnostics_service_support import _require_mapping_response


@pytest.mark.asyncio
async def test_query_user_cloud_uses_raw_empty_body_contract() -> None:
    request_iot_mapping_raw = AsyncMock(return_value=({"data": []}, "token"))

    result = await query_user_cloud(
        request_iot_mapping_raw=request_iot_mapping_raw,
        require_mapping_response=_require_mapping_response,
    )

    assert result == {"data": []}
    request_iot_mapping_raw.assert_awaited_once_with(PATH_QUERY_USER_CLOUD, "")
