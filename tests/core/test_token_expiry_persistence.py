"""Persist renewed leases even when the vendor retains the same token pair."""

from unittest.mock import MagicMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import (
    CONF_ACCESS_TOKEN,
    CONF_EXPIRES_AT,
    CONF_REFRESH_TOKEN,
)
from custom_components.lipro.core.auth import AuthSessionSnapshot
from custom_components.lipro.entry_auth import persist_entry_tokens_if_changed


def test_expiry_only_refresh_is_persisted_once(hass) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_ACCESS_TOKEN: "synthetic-access",
            CONF_REFRESH_TOKEN: "synthetic-refresh",
            CONF_EXPIRES_AT: 100.0,
        },
    )
    entry.add_to_hass(hass)
    manager = MagicMock()
    manager.get_auth_session.return_value = AuthSessionSnapshot(
        access_token="synthetic-access",
        refresh_token="synthetic-refresh",
        user_id=None,
        expires_at=200.0,
        phone_id=None,
    )

    persist_entry_tokens_if_changed(hass, entry, manager)
    assert entry.data[CONF_EXPIRES_AT] == 200.0
    assert entry.data[CONF_ACCESS_TOKEN] == "synthetic-access"
    assert entry.data[CONF_REFRESH_TOKEN] == "synthetic-refresh"

    with patch.object(hass.config_entries, "async_update_entry") as update:
        persist_entry_tokens_if_changed(hass, entry, manager)
    update.assert_not_called()
