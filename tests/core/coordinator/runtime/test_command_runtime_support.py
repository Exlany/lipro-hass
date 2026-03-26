"""Shared fixtures and imports for topicized CommandRuntime suites."""
# ruff: noqa: F401


from __future__ import annotations

import asyncio
from collections import deque
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.lipro.core.api import LiproApiError, LiproAuthError
from custom_components.lipro.core.command.confirmation_tracker import (
    CommandConfirmationTracker,
)
from custom_components.lipro.core.command.expectation import PendingCommandExpectation
from custom_components.lipro.core.command.result import (
    COMMAND_RESULT_STATE_CONFIRMED,
    COMMAND_RESULT_STATE_FAILED,
    COMMAND_RESULT_STATE_PENDING,
    COMMAND_VERIFICATION_RESULT_TIMEOUT,
)
from custom_components.lipro.core.coordinator.runtime.command import (
    CommandBuilder,
    CommandDispatchApiError,
    CommandSender,
    ConfirmationManager,
    RetryStrategy,
)
from custom_components.lipro.core.coordinator.runtime.command_runtime import (
    CommandRuntime,
)
from custom_components.lipro.core.device import LiproDevice


@pytest.fixture
def mock_client():
    """Create mock API client."""
    client = Mock()
    client.query_command_result = AsyncMock()
    return client


@pytest.fixture
def mock_device():
    """Create mock device."""
    device = Mock(spec=LiproDevice)
    device.serial = "test_serial_123"
    device.name = "Test Device"
    device.device_type = "light"
    device.is_group = False
    return device


@pytest.fixture
def confirmation_tracker():
    """Create confirmation tracker."""
    return CommandConfirmationTracker(
        default_post_command_refresh_delay_seconds=3.0,
        min_post_command_refresh_delay_seconds=1.5,
        max_post_command_refresh_delay_seconds=8.0,
        state_latency_margin_seconds=0.6,
        state_latency_ewma_alpha=0.35,
        state_confirm_timeout_seconds=20.0,
    )


@pytest.fixture
def runtime_deps(mock_client, confirmation_tracker):
    """Create runtime dependencies."""
    pending_expectations: dict[str, PendingCommandExpectation] = {}
    device_state_latency_seconds: dict[str, float] = {}
    post_command_refresh_tasks: dict[str, asyncio.Task[Any]] = {}
    track_background_task = Mock(side_effect=lambda coro: asyncio.create_task(coro))
    request_refresh = AsyncMock()
    mqtt_connected_provider = Mock(return_value=True)
    trigger_reauth = AsyncMock()

    builder = CommandBuilder(debug_mode=True)
    sender = CommandSender(protocol=mock_client)
    retry = RetryStrategy()
    confirmation = ConfirmationManager(
        confirmation_tracker=confirmation_tracker,
        pending_expectations=pending_expectations,
        device_state_latency_seconds=device_state_latency_seconds,
        post_command_refresh_tasks=post_command_refresh_tasks,
        track_background_task=track_background_task,
        request_refresh=request_refresh,
        mqtt_connected_provider=mqtt_connected_provider,
    )

    return {
        "builder": builder,
        "sender": sender,
        "retry": retry,
        "confirmation": confirmation,
        "trigger_reauth": trigger_reauth,
        "track_background_task": track_background_task,
        "request_refresh": request_refresh,
    }


@pytest.fixture
def command_runtime(runtime_deps):
    """Create CommandRuntime instance."""
    return CommandRuntime(
        builder=runtime_deps["builder"],
        sender=runtime_deps["sender"],
        retry=runtime_deps["retry"],
        confirmation=runtime_deps["confirmation"],
        trigger_reauth=runtime_deps["trigger_reauth"],
        debug_mode=True,
    )



__all__ = [
    "COMMAND_RESULT_STATE_CONFIRMED",
    "COMMAND_RESULT_STATE_FAILED",
    "COMMAND_RESULT_STATE_PENDING",
    "COMMAND_VERIFICATION_RESULT_TIMEOUT",
    "CommandBuilder",
    "CommandDispatchApiError",
    "CommandRuntime",
    "CommandSender",
    "ConfirmationManager",
    "LiproApiError",
    "LiproAuthError",
    "PendingCommandExpectation",
    "RetryStrategy",
    "command_runtime",
    "confirmation_tracker",
    "mock_client",
    "mock_device",
    "runtime_deps",
]
