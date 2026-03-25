"""Topicized CommandRuntime sender tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

import pytest

from .test_command_runtime_support import (
    COMMAND_RESULT_STATE_CONFIRMED,
    COMMAND_RESULT_STATE_FAILED,
    COMMAND_RESULT_STATE_PENDING,
    COMMAND_VERIFICATION_RESULT_TIMEOUT,
    CommandSender,
)

pytest_plugins = ("tests.core.coordinator.runtime.test_command_runtime_support",)

class TestCommandSender:
    """Test CommandSender component."""

    @pytest.mark.asyncio
    async def test_send_command_success(self, mock_client, mock_device):
        """Test successful command send."""
        sender = CommandSender(protocol=mock_client)
        trace: dict[str, Any] = {}

        with patch(
            "custom_components.lipro.core.coordinator.runtime.command.sender.execute_command_plan_with_trace"
        ) as mock_exec:
            mock_plan = Mock()
            mock_exec.return_value = (
                mock_plan,
                {"pushSuccess": True, "msgSn": "12345"},
                "iot",
            )

            result, route = await sender.send_command(
                device=mock_device,
                command="POWER_ON",
                properties=None,
                fallback_device_id=None,
                trace=trace,
            )

            assert isinstance(result, dict)
            assert result["pushSuccess"] is True
            assert route == "iot"

    @pytest.mark.asyncio
    async def test_verify_command_delivery_timeout(self, mock_client, mock_device):
        """Test command delivery verification timeout."""
        sender = CommandSender(protocol=mock_client)
        trace: dict[str, Any] = {}

        # Mock to always return None (no result)
        async def mock_query_once(*args, **kwargs):
            return None

        with patch(
            "custom_components.lipro.core.coordinator.runtime.command.sender.query_command_result_once",
            side_effect=mock_query_once,
        ):
            verified, classification = await sender.verify_command_delivery(
                msg_sn="12345", retry_delays=[0.001], trace=trace, device=mock_device
            )

            assert verified is False
            assert trace["verification_result"] == COMMAND_VERIFICATION_RESULT_TIMEOUT
            assert classification is None

    @pytest.mark.asyncio
    async def test_verify_command_delivery_confirmed_result(
        self, mock_client, mock_device
    ):
        """Test command delivery with confirmed classification."""
        sender = CommandSender(protocol=mock_client)
        trace: dict[str, Any] = {}

        async def mock_query_once(*args, **kwargs):
            return {"code": 0}

        with (
            patch(
                "custom_components.lipro.core.coordinator.runtime.command.sender.query_command_result_once",
                side_effect=mock_query_once,
            ),
            patch(
                "custom_components.lipro.core.coordinator.runtime.command.sender.classify_command_result_payload",
                return_value=COMMAND_RESULT_STATE_CONFIRMED,
            ),
        ):
            verified, classification = await sender.verify_command_delivery(
                msg_sn="12345", retry_delays=[0.001], trace=trace, device=mock_device
            )

            assert verified is True
            assert trace["verification_result"] == COMMAND_RESULT_STATE_CONFIRMED
            assert classification == COMMAND_RESULT_STATE_CONFIRMED

    @pytest.mark.asyncio
    async def test_verify_command_delivery_failed_result(
        self, mock_client, mock_device
    ):
        """Test command delivery with failed classification."""
        sender = CommandSender(protocol=mock_client)
        trace: dict[str, Any] = {}

        async def mock_query_once(*args, **kwargs):
            return {"code": 1}

        with (
            patch(
                "custom_components.lipro.core.coordinator.runtime.command.sender.query_command_result_once",
                side_effect=mock_query_once,
            ),
            patch(
                "custom_components.lipro.core.coordinator.runtime.command.sender.classify_command_result_payload",
                return_value=COMMAND_RESULT_STATE_FAILED,
            ),
        ):
            verified, classification = await sender.verify_command_delivery(
                msg_sn="12345", retry_delays=[0.001], trace=trace, device=mock_device
            )

            assert verified is False
            assert trace["verification_result"] == COMMAND_RESULT_STATE_FAILED
            assert classification == COMMAND_RESULT_STATE_FAILED

    @pytest.mark.asyncio
    async def test_verify_command_delivery_pending_classification(
        self, mock_client, mock_device
    ):
        """Test command delivery with pending classification that times out."""
        sender = CommandSender(protocol=mock_client)
        trace: dict[str, Any] = {}

        async def mock_query_once(*args, **kwargs):
            return {"code": 100000}

        with (
            patch(
                "custom_components.lipro.core.coordinator.runtime.command.sender.query_command_result_once",
                side_effect=mock_query_once,
            ),
            patch(
                "custom_components.lipro.core.coordinator.runtime.command.sender.classify_command_result_payload",
                return_value=COMMAND_RESULT_STATE_PENDING,
            ),
        ):
            verified, classification = await sender.verify_command_delivery(
                msg_sn="12345", retry_delays=[0.001], trace=trace, device=mock_device
            )

            assert verified is False
            assert trace["verification_result"] == COMMAND_VERIFICATION_RESULT_TIMEOUT
            assert classification is None
