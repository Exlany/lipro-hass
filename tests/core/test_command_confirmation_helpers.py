"""Tests for command confirmation and post-refresh helpers."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.lipro.core.command.confirmation_tracker import (
    CommandConfirmationTracker,
)
from custom_components.lipro.core.command.expectation import PendingCommandExpectation
from custom_components.lipro.core.command.post_refresh import (
    on_post_command_refresh_task_done,
    schedule_post_command_refresh,
)


@pytest.fixture
def tracker() -> CommandConfirmationTracker:
    """Create a tracker with stable timing bounds for helper tests."""
    return CommandConfirmationTracker(
        default_post_command_refresh_delay_seconds=3.0,
        min_post_command_refresh_delay_seconds=1.5,
        max_post_command_refresh_delay_seconds=8.0,
        state_latency_margin_seconds=0.6,
        state_latency_ewma_alpha=0.25,
        state_confirm_timeout_seconds=20.0,
    )


def _make_task(*, done: bool = False) -> Mock:
    task = Mock()
    task.done.return_value = done
    task.cancel = Mock()
    task.add_done_callback = Mock()
    return task


def _build_tracker(tasks: list[Mock]) -> Mock:
    def _track(coro):
        coro.close()
        return tasks.pop(0)

    return Mock(side_effect=_track)


def test_pending_command_expectation_tracks_stale_keys_and_confirmation() -> None:
    pending = PendingCommandExpectation(
        sent_at=10.0,
        expected={"powerState": "1", "brightness": "50"},
    )

    assert pending.is_expired(now=31.0, timeout_seconds=20.0) is True
    assert pending.stale_keys(
        {"powerState": "0", "brightness": "50", "mode": "auto"}
    ) == {"powerState"}
    assert pending.observe({"powerState": 1}) is False
    assert pending.observe({"brightness": "50"}) is True
    assert pending.expected == {}


def test_filter_pending_command_mismatches_prunes_expired_expectations(
    tracker: CommandConfirmationTracker,
) -> None:
    pending_expectations = {
        "device-1": PendingCommandExpectation(
            sent_at=0.0,
            expected={"powerState": "1"},
        )
    }

    with patch(
        "custom_components.lipro.core.command.confirmation_tracker.monotonic",
        return_value=100.0,
    ):
        filtered, blocked = tracker.filter_pending_command_mismatches(
            pending_expectations=pending_expectations,
            device_serial="device-1",
            properties={"powerState": "0"},
        )

    assert filtered == {"powerState": "0"}
    assert blocked == set()
    assert pending_expectations == {}


def test_filter_pending_command_mismatches_returns_original_when_nothing_pending(
    tracker: CommandConfirmationTracker,
) -> None:
    properties = {"powerState": "1"}

    filtered, blocked = tracker.filter_pending_command_mismatches(
        pending_expectations={},
        device_serial="device-1",
        properties=properties,
    )

    assert filtered == properties
    assert blocked == set()


def test_filter_pending_command_mismatches_blocks_unconfirmed_keys(
    tracker: CommandConfirmationTracker,
) -> None:
    pending_expectations = {
        "device-1": PendingCommandExpectation(
            sent_at=90.0,
            expected={"powerState": "1", "brightness": "50"},
        )
    }

    with patch(
        "custom_components.lipro.core.command.confirmation_tracker.monotonic",
        return_value=100.0,
    ):
        filtered, blocked = tracker.filter_pending_command_mismatches(
            pending_expectations=pending_expectations,
            device_serial="device-1",
            properties={"powerState": "0", "brightness": "50", "mode": "auto"},
        )

    assert filtered == {"brightness": "50", "mode": "auto"}
    assert blocked == {"powerState"}


def test_filter_pending_command_mismatches_returns_original_when_all_values_match(
    tracker: CommandConfirmationTracker,
) -> None:
    pending_expectations = {
        "device-1": PendingCommandExpectation(
            sent_at=90.0,
            expected={"powerState": "1"},
        )
    }

    with patch(
        "custom_components.lipro.core.command.confirmation_tracker.monotonic",
        return_value=100.0,
    ):
        filtered, blocked = tracker.filter_pending_command_mismatches(
            pending_expectations=pending_expectations,
            device_serial="device-1",
            properties={"powerState": "1"},
        )

    assert filtered == {"powerState": "1"}
    assert blocked == set()


def test_track_command_expectation_clears_invalid_inputs(
    tracker: CommandConfirmationTracker,
) -> None:
    pending_expectations = {
        "device-1": PendingCommandExpectation(sent_at=1.0, expected={"power": "1"})
    }

    tracker.track_command_expectation(
        pending_expectations=pending_expectations,
        device_serial="device-1",
        command="POWER_ON",
        properties=None,
    )
    assert pending_expectations == {}

    pending_expectations["device-1"] = PendingCommandExpectation(
        sent_at=1.0,
        expected={"power": "1"},
    )
    tracker.track_command_expectation(
        pending_expectations=pending_expectations,
        device_serial="device-1",
        command="CHANGE_STATE",
        properties=[{"value": "1"}],
    )
    assert pending_expectations == {}


def test_track_command_expectation_records_stringified_expected_values(
    tracker: CommandConfirmationTracker,
) -> None:
    pending_expectations: dict[str, PendingCommandExpectation] = {}

    with patch(
        "custom_components.lipro.core.command.confirmation_tracker.monotonic",
        return_value=123.0,
    ):
        tracker.track_command_expectation(
            pending_expectations=pending_expectations,
            device_serial="device-1",
            command="CHANGE_STATE",
            properties=[
                {"key": "powerState", "value": 1},
                {"key": "mode", "value": "sleep"},
            ],
        )

    assert pending_expectations["device-1"].sent_at == 123.0
    assert pending_expectations["device-1"].expected == {
        "powerState": "1",
        "mode": "sleep",
    }


def test_update_state_latency_bounds_and_applies_ewma(
    tracker: CommandConfirmationTracker,
) -> None:
    latencies: dict[str, float] = {}

    tracker.update_state_latency(
        device_state_latency_seconds=latencies,
        device_serial="device-1",
        observed_latency=20.0,
    )
    assert latencies == {"device-1": 8.0}

    tracker.update_state_latency(
        device_state_latency_seconds=latencies,
        device_serial="device-1",
        observed_latency=0.1,
    )
    assert latencies["device-1"] == pytest.approx(6.375)


def test_observe_command_confirmation_updates_latency_and_clears_pending(
    tracker: CommandConfirmationTracker,
) -> None:
    pending_expectations = {
        "device-1": PendingCommandExpectation(
            sent_at=10.0,
            expected={"powerState": "1"},
        )
    }
    latencies: dict[str, float] = {}

    with patch(
        "custom_components.lipro.core.command.confirmation_tracker.monotonic",
        return_value=15.0,
    ):
        latency = tracker.observe_command_confirmation(
            pending_expectations=pending_expectations,
            device_state_latency_seconds=latencies,
            device_serial="device-1",
            properties={"powerState": 1},
        )

    assert latency == 5.0
    assert latencies == {"device-1": 5.0}
    assert pending_expectations == {}


def test_observe_command_confirmation_returns_none_when_pending_not_matched(
    tracker: CommandConfirmationTracker,
) -> None:
    pending_expectations = {
        "device-1": PendingCommandExpectation(
            sent_at=10.0,
            expected={"powerState": "1"},
        )
    }

    with patch(
        "custom_components.lipro.core.command.confirmation_tracker.monotonic",
        return_value=15.0,
    ):
        latency = tracker.observe_command_confirmation(
            pending_expectations=pending_expectations,
            device_state_latency_seconds={},
            device_serial="device-1",
            properties={"powerState": "0"},
        )

    assert latency is None
    assert pending_expectations["device-1"].expected == {"powerState": "1"}


def test_observe_command_confirmation_returns_none_without_pending_or_when_expired(
    tracker: CommandConfirmationTracker,
) -> None:
    assert (
        tracker.observe_command_confirmation(
            pending_expectations={},
            device_state_latency_seconds={},
            device_serial="device-1",
            properties={"powerState": "1"},
        )
        is None
    )

    pending_expectations = {
        "device-1": PendingCommandExpectation(
            sent_at=0.0,
            expected={"powerState": "1"},
        )
    }
    with patch(
        "custom_components.lipro.core.command.confirmation_tracker.monotonic",
        return_value=100.0,
    ):
        assert (
            tracker.observe_command_confirmation(
                pending_expectations=pending_expectations,
                device_state_latency_seconds={},
                device_serial="device-1",
                properties={"powerState": "1"},
            )
            is None
        )

    assert pending_expectations == {}


def test_get_adaptive_post_refresh_delay_delegates_to_policy(
    tracker: CommandConfirmationTracker,
) -> None:
    with patch(
        "custom_components.lipro.core.command.confirmation_tracker.compute_adaptive_post_refresh_delay",
        return_value=4.2,
    ) as mock_compute:
        delay = tracker.get_adaptive_post_refresh_delay(
            device_state_latency_seconds={"device-1": 2.5},
            device_serial="device-1",
        )

    assert delay == 4.2
    assert mock_compute.call_args.kwargs["learned_latency_seconds"] == 2.5


def test_prune_runtime_state_for_devices_removes_stale_entries(
    tracker: CommandConfirmationTracker,
) -> None:
    del tracker
    pending_expectations = {
        "active": PendingCommandExpectation(sent_at=1.0, expected={"x": "1"}),
        "stale": PendingCommandExpectation(sent_at=2.0, expected={"y": "2"}),
    }
    latencies = {"active": 1.0, "stale": 2.0}

    CommandConfirmationTracker.prune_runtime_state_for_devices(
        pending_expectations=pending_expectations,
        device_state_latency_seconds=latencies,
        active_serials={"active"},
    )

    assert set(pending_expectations) == {"active"}
    assert latencies == {"active": 1.0}


def test_on_post_command_refresh_task_done_only_clears_matching_task() -> None:
    tracked = _make_task()
    post_command_refresh_tasks = {"device-1": tracked}

    on_post_command_refresh_task_done(
        post_command_refresh_tasks=post_command_refresh_tasks,
        refresh_key="device-1",
        finished_task=_make_task(),
    )
    assert post_command_refresh_tasks == {"device-1": tracked}

    on_post_command_refresh_task_done(
        post_command_refresh_tasks=post_command_refresh_tasks,
        refresh_key="device-1",
        finished_task=tracked,
    )
    assert post_command_refresh_tasks == {}


def test_schedule_post_command_refresh_tracks_immediate_and_delayed_refresh() -> None:
    immediate_task = _make_task()
    delayed_task = _make_task()
    track_background_task = _build_tracker([immediate_task, delayed_task])
    request_refresh = AsyncMock()
    post_command_refresh_tasks: dict[str, Mock] = {}

    with patch(
        "custom_components.lipro.core.command.post_refresh.resolve_delayed_refresh_delay",
        return_value=2.5,
    ), patch(
        "custom_components.lipro.core.command.post_refresh.run_delayed_refresh",
        new=AsyncMock(return_value=None),
    ) as run_delayed_refresh:
        schedule_post_command_refresh(
            track_background_task=track_background_task,
            request_refresh=request_refresh,
            post_command_refresh_tasks=post_command_refresh_tasks,
            mqtt_connected=True,
            device_serial="device-1",
            pending_expectations={},
            get_adaptive_post_refresh_delay=Mock(return_value=3.0),
            skip_immediate=False,
        )

    assert track_background_task.call_count == 2
    assert post_command_refresh_tasks == {"device-1": delayed_task}
    assert delayed_task.add_done_callback.called is True
    assert run_delayed_refresh.call_args.kwargs["delay_seconds"] == 2.5


def test_schedule_post_command_refresh_cancels_previous_delayed_task() -> None:
    previous_task = _make_task(done=False)
    delayed_task = _make_task()
    track_background_task = _build_tracker([delayed_task])
    request_refresh = AsyncMock()
    post_command_refresh_tasks: dict[str, Mock] = {"device-1": previous_task}

    with patch(
        "custom_components.lipro.core.command.post_refresh.resolve_delayed_refresh_delay",
        return_value=1.0,
    ), patch(
        "custom_components.lipro.core.command.post_refresh.run_delayed_refresh",
        new=AsyncMock(return_value=None),
    ):
        schedule_post_command_refresh(
            track_background_task=track_background_task,
            request_refresh=request_refresh,
            post_command_refresh_tasks=post_command_refresh_tasks,
            mqtt_connected=True,
            device_serial="device-1",
            pending_expectations={},
            get_adaptive_post_refresh_delay=Mock(return_value=3.0),
            skip_immediate=True,
        )

    previous_task.cancel.assert_called_once_with()
    request_refresh.assert_not_called()
    assert post_command_refresh_tasks == {"device-1": delayed_task}


def test_schedule_post_command_refresh_returns_when_no_delay() -> None:
    track_background_task = Mock()
    request_refresh = AsyncMock()
    post_command_refresh_tasks: dict[str, Mock] = {}

    with patch(
        "custom_components.lipro.core.command.post_refresh.resolve_delayed_refresh_delay",
        return_value=None,
    ):
        schedule_post_command_refresh(
            track_background_task=track_background_task,
            request_refresh=request_refresh,
            post_command_refresh_tasks=post_command_refresh_tasks,
            mqtt_connected=True,
            device_serial="device-1",
            pending_expectations={},
            get_adaptive_post_refresh_delay=Mock(return_value=3.0),
            skip_immediate=True,
        )

    track_background_task.assert_not_called()
    assert post_command_refresh_tasks == {}
