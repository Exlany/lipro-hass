"""Tests for Lipro MQTT transport."""

from __future__ import annotations

import pytest

from custom_components.lipro.core.mqtt.topics import build_topic, parse_topic


class TestBuildTopic:
    """Tests for topic building."""

    def test_build_topic(self):
        """Test building MQTT topic."""
        topic = build_topic("biz001", "03ab5ccd7cxxxxxx")

        assert topic == "Topic_Device_State/biz001/03ab5ccd7cxxxxxx"

    def test_build_topic_with_special_chars(self):
        """Test building topic with various IDs."""
        topic = build_topic("biz001", "mesh_group_10001")

        assert topic == "Topic_Device_State/biz001/mesh_group_10001"

    def test_build_topic_invalid_biz_id_raises(self):
        """Invalid biz_id should be rejected."""
        with pytest.raises(ValueError, match="Invalid biz_id format"):
            build_topic("biz/invalid", "03ab5ccd7cxxxxxx")

class TestParseTopic:
    """Tests for topic parsing."""

    def test_parse_topic_valid(self):
        """Test parsing valid topic."""
        device_id = parse_topic("Topic_Device_State/biz001/03ab5ccd7cxxxxxx")

        assert device_id == "03ab5ccd7cxxxxxx"
        assert (
            parse_topic(
                "Topic_Device_State/biz001/03ab5ccd7cxxxxxx",
                expected_biz_id="lip_biz001",
            )
            == "03ab5ccd7cxxxxxx"
        )

    def test_parse_topic_invalid(self):
        """Test parsing invalid topic."""
        assert parse_topic("invalid") is None
        assert parse_topic("only/two") is None
        assert parse_topic("") is None
        # Wrong prefix should also return None
        assert parse_topic("Wrong_Prefix/biz/device") is None

    def test_parse_topic_extra_parts(self):
        """Topic with extra segments should be rejected."""
        assert parse_topic("Topic_Device_State/biz/device/extra/parts") is None

    def test_parse_topic_invalid_biz_or_device(self):
        """Topic should reject invalid biz/device segment characters."""
        assert parse_topic("Topic_Device_State/biz$/device") is None
        assert parse_topic("Topic_Device_State/biz/device#1") is None


    def test_parse_topic_rejects_mismatched_expected_biz(self):
        """Expected biz ID mismatch should reject the topic."""
        assert (
            parse_topic(
                "Topic_Device_State/biz123/03ab5ccd7cxxxxxx",
                expected_biz_id="biz001",
            )
            is None
        )
