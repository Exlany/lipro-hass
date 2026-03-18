"""Protocol-root owned shared session state."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

import aiohttp

from ..api.client_base import ClientSessionState


class ProtocolSessionSnapshot(TypedDict):
    """Diagnostics-friendly snapshot of shared protocol session state."""

    phone_id: str
    entry_id: str | None
    user_id: int | None
    biz_id: str | None
    access_token_present: bool
    refresh_token_present: bool
    request_timeout: int


@dataclass(slots=True)
class ProtocolSessionState:
    """Root-owned shared protocol session view.

    The REST child facade still stores the concrete mutable session object, but
    the protocol root owns the canonical access surface exposed to upper planes.
    """

    rest_state: ClientSessionState
    mqtt_biz_id: str | None = None

    @property
    def phone_id(self) -> str:
        """Return the canonical phone identifier for this protocol root."""
        return self.rest_state.phone_id

    @property
    def entry_id(self) -> str | None:
        """Return the owning config-entry identifier when available."""
        return self.rest_state.entry_id

    @property
    def session(self) -> aiohttp.ClientSession | None:
        """Expose the underlying aiohttp session for child-transport use only."""
        return self.rest_state.session

    @property
    def request_timeout(self) -> int:
        """Return the canonical request-timeout policy for protocol calls."""
        return self.rest_state.request_timeout

    @property
    def access_token(self) -> str | None:
        """Return the current protocol access token."""
        return self.rest_state.access_token

    @access_token.setter
    def access_token(self, value: str | None) -> None:
        self.rest_state.access_token = value

    @property
    def refresh_token(self) -> str | None:
        """Return the current protocol refresh token."""
        return self.rest_state.refresh_token

    @refresh_token.setter
    def refresh_token(self, value: str | None) -> None:
        self.rest_state.refresh_token = value

    @property
    def user_id(self) -> int | None:
        """Return the authenticated user identifier when present."""
        return self.rest_state.user_id

    @user_id.setter
    def user_id(self, value: int | None) -> None:
        self.rest_state.user_id = value

    @property
    def biz_id(self) -> str | None:
        """Return the canonical biz-id view shared by REST and MQTT child façades."""
        return self.mqtt_biz_id or self.rest_state.biz_id

    @biz_id.setter
    def biz_id(self, value: str | None) -> None:
        self.rest_state.biz_id = value
        self.mqtt_biz_id = value

    def bind_mqtt_biz_id(self, biz_id: str | None) -> None:
        """Bind or clear the MQTT biz-id view owned by the protocol root."""
        self.mqtt_biz_id = biz_id
        if biz_id:
            self.rest_state.biz_id = biz_id

    def as_dict(self) -> ProtocolSessionSnapshot:
        """Return a lightweight diagnostics-friendly session snapshot."""
        return {
            "phone_id": self.phone_id,
            "entry_id": self.entry_id,
            "user_id": self.user_id,
            "biz_id": self.biz_id,
            "access_token_present": bool(self.access_token),
            "refresh_token_present": bool(self.refresh_token),
            "request_timeout": self.request_timeout,
        }


__all__ = ["ProtocolSessionSnapshot", "ProtocolSessionState"]
