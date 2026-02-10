"""Tests for Lipro diagnostics."""

from __future__ import annotations

from custom_components.lipro.diagnostics import (
    PROPERTY_KEYS_TO_REDACT,
    TO_REDACT,
    _redact_device_properties,
)


class TestRedactDeviceProperties:
    """Tests for _redact_device_properties function."""

    def test_redact_mac(self):
        """Test mac is redacted."""
        props = {"mac": "5C:CD:7C:XX:XX:XX", "powerState": "1"}
        result = _redact_device_properties(props)
        assert result["mac"] == "**REDACTED**"
        assert result["powerState"] == "1"

    def test_redact_mac_address(self):
        """Test macAddress is redacted."""
        props = {"macAddress": "5C:CD:7C:XX:XX:XX"}
        result = _redact_device_properties(props)
        assert result["macAddress"] == "**REDACTED**"

    def test_redact_ip(self):
        """Test ip is redacted."""
        props = {"ip": "192.168.1.100"}
        result = _redact_device_properties(props)
        assert result["ip"] == "**REDACTED**"

    def test_redact_ip_address(self):
        """Test ipAddress is redacted."""
        props = {"ipAddress": "192.168.1.100"}
        result = _redact_device_properties(props)
        assert result["ipAddress"] == "**REDACTED**"

    def test_non_sensitive_preserved(self):
        """Test non-sensitive properties are preserved."""
        props = {
            "powerState": "1",
            "brightness": "80",
            "temperature": "4000",
        }
        result = _redact_device_properties(props)
        assert result == props

    def test_empty_properties(self):
        """Test empty properties dict."""
        result = _redact_device_properties({})
        assert result == {}

    def test_case_insensitive_redaction(self):
        """Test redaction is case-insensitive."""
        props = {"MAC": "5C:CD:7C:XX:XX:XX", "IP": "192.168.1.1"}
        result = _redact_device_properties(props)
        assert result["MAC"] == "**REDACTED**"
        assert result["IP"] == "**REDACTED**"


class TestToRedactKeys:
    """Tests for TO_REDACT set completeness."""

    def test_contains_auth_keys(self):
        """Test TO_REDACT contains authentication keys."""
        assert "password" in TO_REDACT
        assert "password_hash" in TO_REDACT
        assert "access_token" in TO_REDACT
        assert "refresh_token" in TO_REDACT
        assert "user_id" in TO_REDACT

    def test_contains_device_id_keys(self):
        """Test TO_REDACT contains device identification keys."""
        assert "serial" in TO_REDACT
        assert "device_id" in TO_REDACT
        assert "deviceId" in TO_REDACT
        assert "groupId" in TO_REDACT
        assert "iotName" in TO_REDACT
        assert "gatewayDeviceId" in TO_REDACT

    def test_contains_user_keys(self):
        """Test TO_REDACT contains user identification keys."""
        assert "phone" in TO_REDACT
        assert "phone_id" in TO_REDACT


class TestPropertyKeysToRedact:
    """Tests for PROPERTY_KEYS_TO_REDACT set completeness."""

    def test_contains_network_keys(self):
        """Test PROPERTY_KEYS_TO_REDACT contains network-related keys."""
        assert "mac" in PROPERTY_KEYS_TO_REDACT
        assert "macAddress" in PROPERTY_KEYS_TO_REDACT
        assert "ip" in PROPERTY_KEYS_TO_REDACT
        assert "ipAddress" in PROPERTY_KEYS_TO_REDACT

    def test_count(self):
        """Test PROPERTY_KEYS_TO_REDACT has expected count."""
        assert len(PROPERTY_KEYS_TO_REDACT) == 6
