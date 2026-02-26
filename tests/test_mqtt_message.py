"""Tests for MQTT message helper functions."""

from __future__ import annotations

from custom_components.lipro.core.mqtt_message import (
    build_dedup_cache_key,
    cleanup_dedup_cache,
    compute_properties_hash,
    is_duplicate_within_window,
    is_online_connect_state,
)


def test_is_online_connect_state_variants() -> None:
    assert is_online_connect_state(True) is True
    assert is_online_connect_state(1) is True
    assert is_online_connect_state(" true ") is True
    assert is_online_connect_state("on") is True
    assert is_online_connect_state(False) is False
    assert is_online_connect_state(0) is False
    assert is_online_connect_state("off") is False
    assert is_online_connect_state(None) is False


def test_compute_properties_hash_with_hashable_payload() -> None:
    payload = {"powerState": "1", "brightness": "50"}
    assert isinstance(compute_properties_hash(payload), int)


def test_compute_properties_hash_with_unhashable_payload_returns_none() -> None:
    payload = {"schedule": [1, 2, 3]}
    assert compute_properties_hash(payload) is None


def test_build_dedup_cache_key() -> None:
    assert build_dedup_cache_key("dev1", 123) == "dev1:123"


def test_is_duplicate_within_window() -> None:
    cache = {"dev1:1": 100.0}
    assert (
        is_duplicate_within_window(
            cache,
            cache_key="dev1:1",
            current_time=100.2,
            dedup_window=0.5,
        )
        is True
    )
    assert (
        is_duplicate_within_window(
            cache,
            cache_key="dev1:1",
            current_time=100.8,
            dedup_window=0.5,
        )
        is False
    )
    assert (
        is_duplicate_within_window(
            cache,
            cache_key="dev2:2",
            current_time=100.2,
            dedup_window=0.5,
        )
        is False
    )


def test_cleanup_dedup_cache_removes_stale_entries() -> None:
    cleaned = cleanup_dedup_cache(
        {"old": 1.0, "fresh": 9.5},
        current_time=10.0,
        stale_seconds=1.0,
        max_entries=10,
    )
    assert cleaned == {"fresh": 9.5}


def test_cleanup_dedup_cache_caps_to_newest_half_when_exceeding_limit() -> None:
    cache = {f"k{i}": float(i) for i in range(12)}
    cleaned = cleanup_dedup_cache(
        cache,
        current_time=20.0,
        stale_seconds=100.0,
        max_entries=5,
    )
    # Cap keeps newest half of sorted timestamps.
    assert len(cleaned) == 6
    assert set(cleaned.keys()) == {f"k{i}" for i in range(6, 12)}
