"""Tests for response safety helpers."""

from __future__ import annotations

from custom_components.lipro.core.api.response_safety import (
    _mask_phone_digits,
    mask_sensitive_data,
    normalize_response_code,
)


class TestMaskSensitiveData:
    """Tests for sensitive data masking."""

    def test_mask_access_token(self):
        """Test masking access token."""
        data = '{"access_token": "secret123", "other": "value"}'
        result = mask_sensitive_data(data)
        assert '"access_token": "***"' in result
        assert "secret123" not in result
        assert '"other": "value"' in result

    def test_mask_refresh_token(self):
        """Test masking refresh token."""
        data = '{"refresh_token": "refresh_secret"}'
        result = mask_sensitive_data(data)
        assert '"refresh_token": "***"' in result
        assert "refresh_secret" not in result

    def test_mask_password(self):
        """Test masking password."""
        data = '{"password": "mypassword123"}'
        result = mask_sensitive_data(data)
        assert '"password": "***"' in result
        assert "mypassword123" not in result

    def test_mask_password_hash(self):
        """Test masking password hash fields."""
        data = '{"password_hash": "deadbeef", "passwordHash": "cafebabe"}'
        result = mask_sensitive_data(data)
        assert '"password_hash": "***"' in result
        assert '"passwordHash": "***"' in result
        assert "deadbeef" not in result
        assert "cafebabe" not in result

    def test_mask_phone(self):
        """Test masking phone number (keep first 3 and last 4)."""
        data = '{"phone": "13800001234"}'
        result = mask_sensitive_data(data)
        assert '"phone": "138****1234"' in result
        assert "13800001234" not in result

    def test_mask_phone_with_plus_prefix(self):
        """Test masking phone number that includes country-code prefix."""
        data = '{"phone": "+8613800001234"}'
        result = mask_sensitive_data(data)
        assert '"phone": "+861****1234"' in result
        assert "+8613800001234" not in result

    def test_mask_numeric_user_and_biz_ids(self):
        """Test masking numeric user/biz id values."""
        data = '{"user_id": 10001, "userId": 10002, "biz_id": 20001, "bizId": 20002}'
        result = mask_sensitive_data(data)
        assert '"user_id": "***"' in result
        assert '"userId": "***"' in result
        assert '"biz_id": "***"' in result
        assert '"bizId": "***"' in result
        assert "10001" not in result
        assert "10002" not in result
        assert "20001" not in result
        assert "20002" not in result

    def test_mask_camel_case_tokens(self):
        """Test masking camelCase token fields."""
        data = '{"accessToken": "token1", "refreshToken": "token2"}'
        result = mask_sensitive_data(data)
        assert '"accessToken": "***"' in result
        assert '"refreshToken": "***"' in result

    def test_mask_mqtt_keys(self):
        """Test masking MQTT access/secret keys."""
        data = '{"accessKey":"ak_test","secretKey":"sk_test"}'
        result = mask_sensitive_data(data)
        assert '"accessKey": "***"' in result
        assert '"secretKey": "***"' in result
        assert "ak_test" not in result
        assert "sk_test" not in result

    def test_mask_install_token(self):
        """Test masking anonymous share install token fields."""
        data = '{"install_token": "tok-1", "installToken": "tok-2"}'
        result = mask_sensitive_data(data)
        assert '"install_token": "***"' in result
        assert '"installToken": "***"' in result
        assert "tok-1" not in result
        assert "tok-2" not in result

    def test_mask_phone_short_digits(self):
        """Test masking phone with 6 digits (medium-length branch)."""
        data = '{"phone": "123456"}'
        result = mask_sensitive_data(data)
        assert "123456" not in result
        assert '"phone": "12***56"' in result

    def test_mask_phone_digits_very_short(self):
        """Test _mask_phone_digits with 4 or fewer digits."""
        assert _mask_phone_digits("1234") == "***"
        assert _mask_phone_digits("12") == "***"

    def test_mask_device_name_room_name_and_network_fields(self):
        """Test masking additional privacy-sensitive device/network fields."""
        data = (
            '{"deviceName":"Bedroom Light","roomName":"Master",'
            '"wifi_ssid":"HomeWifi","mac":"5c:cd:7c:11:22:33","ip":"10.0.0.10"}'
        )
        result = mask_sensitive_data(data)
        assert '"deviceName": "***"' in result
        assert '"roomName": "***"' in result
        assert '"wifi_ssid": "***"' in result
        assert '"mac": "***"' in result
        assert '"ip": "***"' in result
        assert "Bedroom Light" not in result
        assert "Master" not in result
        assert "HomeWifi" not in result


def test_normalize_response_code_edge_variants() -> None:
    """Response-code normalization should handle bool/float/empty/string-edge values."""

    class _CodeObject:
        def __str__(self) -> str:
            return "  custom_code  "

    assert normalize_response_code(True) == 1
    assert normalize_response_code(2.0) == 2
    assert normalize_response_code(2.5) == "2.5"
    assert normalize_response_code("   ") is None
    assert normalize_response_code("+-1") == "+-1"
    assert normalize_response_code(_CodeObject()) == "custom_code"
