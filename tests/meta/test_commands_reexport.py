"""Tests for coordinator commands re-export module."""

from __future__ import annotations


def test_commands_reexports_are_importable() -> None:
    from custom_components.lipro.core.coordinator.commands import (
        _MAX_DEVELOPER_COMMAND_TRACES,
        _POST_COMMAND_REFRESH_DELAY_SECONDS,
        _STATE_CONFIRM_TIMEOUT_SECONDS,
        _CommandSendMixin,
    )

    assert _POST_COMMAND_REFRESH_DELAY_SECONDS > 0
    assert _STATE_CONFIRM_TIMEOUT_SECONDS > 0
    assert _MAX_DEVELOPER_COMMAND_TRACES > 0
    assert _CommandSendMixin is not None
