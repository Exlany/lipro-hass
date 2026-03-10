"""Tests for the extracted MQTT topic builder."""

from __future__ import annotations

import logging

from custom_components.lipro.core.mqtt.topic_builder import MqttTopicBuilder


def test_topic_builder_build_topic_pairs_skips_invalid_ids(caplog) -> None:
    builder = MqttTopicBuilder("biz001")
    invalid_ids: list[str] = []

    with caplog.at_level(logging.WARNING):
        topic_pairs = builder.build_topic_pairs(
            ["dev_1", "bad/dev", "mesh_group_10001"],
            invalid_log_message=(
                "Skipping invalid MQTT device ID %s: invalid characters"
            ),
            on_invalid=invalid_ids.append,
        )

    assert topic_pairs == [
        ("dev_1", "Topic_Device_State/biz001/dev_1"),
        ("mesh_group_10001", "Topic_Device_State/biz001/mesh_group_10001"),
    ]
    assert invalid_ids == ["bad/dev"]
    assert "invalid characters" in caplog.text
    assert "bad/dev" not in caplog.text


def test_topic_builder_build_topic_pairs_returns_empty_for_empty_input() -> None:
    builder = MqttTopicBuilder("biz001")

    assert (
        builder.build_topic_pairs(
            [],
            invalid_log_message="Skipping invalid MQTT device ID %s",
        )
        == []
    )


def test_topic_builder_batches_topic_pairs_by_configured_size() -> None:
    builder = MqttTopicBuilder("biz001", batch_size=2)

    batches = builder.batch_topic_pairs(
        [
            ("dev_1", "topic/1"),
            ("dev_2", "topic/2"),
            ("dev_3", "topic/3"),
            ("dev_4", "topic/4"),
            ("dev_5", "topic/5"),
        ]
    )

    assert batches == [
        [("dev_1", "topic/1"), ("dev_2", "topic/2")],
        [("dev_3", "topic/3"), ("dev_4", "topic/4")],
        [("dev_5", "topic/5")],
    ]
