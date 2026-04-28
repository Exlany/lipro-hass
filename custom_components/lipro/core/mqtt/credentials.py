"""MQTT credential helpers for Lipro integration."""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
import hashlib
import hmac

from Crypto.Cipher import AES

from ...const.api import MQTT_AES_KEY, MQTT_INSTANCE_ID


def decrypt_mqtt_credential(encrypted_hex: str) -> str:
    """Decrypt MQTT credential using AES/ECB/PKCS5Padding.

    The credentials from API are AES encrypted and hex encoded.
    """
    try:
        encrypted_bytes = binascii.unhexlify(encrypted_hex)
        cipher = AES.new(MQTT_AES_KEY.encode("utf-8"), AES.MODE_ECB)
        decrypted = cipher.decrypt(encrypted_bytes)

        # Remove PKCS5 padding with validation.
        padding_len = decrypted[-1]
        if not 1 <= padding_len <= 16:
            msg = f"Invalid PKCS5 padding length: {padding_len}"
            raise ValueError(msg)
        if decrypted[-padding_len:] != bytes([padding_len]) * padding_len:
            msg = "Invalid PKCS5 padding bytes"
            raise ValueError(msg)
        decrypted = decrypted[:-padding_len]

        return decrypted.decode("utf-8")
    except (ValueError, UnicodeDecodeError, binascii.Error, IndexError) as err:
        msg = f"Failed to decrypt MQTT credential: {err}"
        raise ValueError(msg) from err


@dataclass(frozen=True)
class MqttCredentials:
    """MQTT connection credentials."""

    client_id: str
    username: str
    password: str

    @classmethod
    def create(
        cls,
        access_key: str,
        secret_key: str,
        biz_id: str,
        phone_id: str,
    ) -> MqttCredentials:
        """Create MQTT credentials from decrypted keys."""
        client_id = f"GID_App@@@{biz_id}-android-{phone_id}"[:64]
        username = f"Signature|{access_key}|{MQTT_INSTANCE_ID}"

        signature = hmac.new(
            secret_key.encode("utf-8"),
            client_id.encode("utf-8"),
            hashlib.sha1,
        ).digest()
        password = base64.b64encode(signature).decode("utf-8")

        return cls(client_id=client_id, username=username, password=password)


__all__ = ["MqttCredentials", "decrypt_mqtt_credential"]
