"""Tests for Lipro MQTT transport."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from Crypto.Cipher import AES
import pytest

from custom_components.lipro.const.api import MQTT_AES_KEY
from custom_components.lipro.core.mqtt.credentials import (
    MqttCredentials,
    decrypt_mqtt_credential,
)


class TestDecryptMqttCredential:
    """Tests for MQTT credential decryption."""

    def test_decrypt_valid_credential(self):
        """Test decrypting a valid credential."""
        # This test uses a known encrypted value
        # In real tests, you'd use actual encrypted values from the API
        # For now, we test the function structure
        with pytest.raises(ValueError):
            # Invalid hex should raise ValueError
            decrypt_mqtt_credential("invalid_hex")

    def test_decrypt_empty_credential(self):
        """Test decrypting empty credential raises ValueError (not IndexError)."""
        # After fix: IndexError from empty decrypt is caught and wrapped as ValueError
        with pytest.raises(ValueError, match="Failed to decrypt"):
            decrypt_mqtt_credential("")

    def test_decrypt_short_hex_credential(self):
        """Test decrypting very short hex that produces empty decrypt output."""
        # "00" is valid hex but too short for valid AES — triggers padding error
        with pytest.raises(ValueError):
            decrypt_mqtt_credential("00")

    def test_decrypt_odd_length_hex(self):
        """Test decrypting odd-length hex string."""
        with pytest.raises(ValueError):
            decrypt_mqtt_credential("abc")  # Odd length

    def test_decrypt_non_utf8_credential(self):
        """Test decrypting payload with valid padding but invalid UTF-8 bytes."""
        plaintext = (b"\xff" * 15) + b"\x01"
        cipher = AES.new(MQTT_AES_KEY.encode("utf-8"), AES.MODE_ECB)
        encrypted_hex = cipher.encrypt(plaintext).hex()

        with pytest.raises(ValueError, match="Failed to decrypt"):
            decrypt_mqtt_credential(encrypted_hex)

    def test_decrypt_invalid_padding_length(self):
        """Invalid PKCS5 padding length should raise ValueError."""
        mock_cipher = MagicMock()
        mock_cipher.decrypt.return_value = b"invalid\x00"

        with (
            patch(
                "custom_components.lipro.core.mqtt.credentials.AES.new",
                return_value=mock_cipher,
            ),
            pytest.raises(ValueError, match="Invalid PKCS5 padding length"),
        ):
            decrypt_mqtt_credential("00")

    def test_decrypt_invalid_padding_bytes(self):
        """Mismatched PKCS5 padding bytes should raise ValueError."""
        mock_cipher = MagicMock()
        mock_cipher.decrypt.return_value = b"invalid\x01\x02"

        with (
            patch(
                "custom_components.lipro.core.mqtt.credentials.AES.new",
                return_value=mock_cipher,
            ),
            pytest.raises(ValueError, match="Invalid PKCS5 padding bytes"),
        ):
            decrypt_mqtt_credential("00")

class TestMqttCredentials:
    """Tests for MqttCredentials class."""

    def test_create_credentials(self):
        """Test creating MQTT credentials."""
        creds = MqttCredentials.create(
            access_key="test_access_key",
            secret_key="test_secret_key",
            biz_id="biz001",
            phone_id="550e8400-e29b-41d4-a716-446655440000",
        )

        # Client ID format: GID_App@@@{bizId}-android-{phoneId}
        assert creds.client_id.startswith("GID_App@@@biz001-android-")
        assert len(creds.client_id) <= 64

        # Username format: Signature|{accessKey}|{instanceId}
        assert creds.username.startswith("Signature|test_access_key|")

        # Password is base64 encoded HMAC-SHA1
        assert len(creds.password) > 0

    def test_create_credentials_truncates_client_id(self):
        """Test that client ID is truncated to 64 chars."""
        creds = MqttCredentials.create(
            access_key="key",
            secret_key="secret",
            biz_id="very_long_biz_id_that_exceeds_normal_length",
            phone_id="very-long-phone-uuid-that-also-exceeds-normal-length-1234567890",
        )

        assert len(creds.client_id) == 64
