"""Tests for config-flow submission helpers."""

from __future__ import annotations

import logging

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lipro.const.base import DOMAIN
from custom_components.lipro.const.config import (
    CONF_PASSWORD_HASH,
    CONF_PHONE,
    CONF_PHONE_ID,
    CONF_REMEMBER_PASSWORD_HASH,
)
from custom_components.lipro.flow.login import hash_password
from custom_components.lipro.flow.submission import (
    build_reauth_description_placeholders,
    resolve_entry_remember_password_hash,
    resolve_reauth_expected_user_id,
    validate_reauth_submission,
    validate_reconfigure_submission,
    validate_user_submission,
)

_LOGGER = logging.getLogger(__name__)


def test_validate_user_submission_returns_typed_payload() -> None:
    submission, errors = validate_user_submission(
        {
            CONF_PHONE: "+8613800012345",
            "password": "testpassword",
            CONF_REMEMBER_PASSWORD_HASH: False,
        },
        logger=_LOGGER,
    )

    assert errors == {}
    assert submission is not None
    assert submission.phone == "+8613800012345"
    assert submission.password_hash == hash_password("testpassword")
    assert submission.remember_password_hash is False


def test_validate_user_submission_collects_phone_and_password_errors() -> None:
    submission, errors = validate_user_submission(
        {
            CONF_PHONE: "12abc",
            "password": "123",
        },
        logger=_LOGGER,
    )

    assert submission is None
    assert errors == {
        CONF_PHONE: "invalid_phone",
        "password": "invalid_password",
    }


def test_resolve_entry_remember_password_hash_prefers_explicit_flag() -> None:
    assert (
        resolve_entry_remember_password_hash(
            {
                CONF_REMEMBER_PASSWORD_HASH: False,
                CONF_PASSWORD_HASH: "stored-hash",
            }
        )
        is False
    )
    assert resolve_entry_remember_password_hash({CONF_PASSWORD_HASH: "stored-hash"}) is True


def test_resolve_reauth_expected_user_id_falls_back_to_unique_id() -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="lipro_10001",
        data={
            CONF_PHONE: "13800000000",
            CONF_PHONE_ID: "phone-id",
        },
    )

    assert resolve_reauth_expected_user_id(entry) == 10001


def test_validate_reauth_submission_uses_entry_identity_and_defaults() -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="lipro_10001",
        data={
            CONF_PHONE: "13800000000",
            CONF_PHONE_ID: "phone-id",
            CONF_PASSWORD_HASH: "stored-hash",
        },
    )

    submission, errors = validate_reauth_submission(
        entry,
        {"password": "testpassword"},
        logger=_LOGGER,
    )

    assert errors == {}
    assert submission is not None
    assert submission.phone == "13800000000"
    assert submission.phone_id == "phone-id"
    assert submission.password_hash == hash_password("testpassword")
    assert submission.remember_password_hash is True
    assert build_reauth_description_placeholders(entry) == {"phone": "138****0000"}


def test_validate_reauth_submission_rejects_missing_entry_identity() -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_PHONE: "13800000000"},
    )

    submission, errors = validate_reauth_submission(
        entry,
        {"password": "testpassword"},
        logger=_LOGGER,
    )

    assert submission is None
    assert errors == {"base": "invalid_entry"}


def test_validate_reauth_submission_rejects_invalid_phone_id_type() -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="lipro_10001",
        data={
            CONF_PHONE: "13800000000",
            CONF_PHONE_ID: 12345,
        },
    )

    submission, errors = validate_reauth_submission(
        entry,
        {"password": "testpassword"},
        logger=_LOGGER,
    )

    assert submission is None
    assert errors == {"base": "invalid_entry"}


def test_validate_reauth_submission_rejects_invalid_stored_phone() -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="lipro_10001",
        data={
            CONF_PHONE: "not-a-phone",
            CONF_PHONE_ID: "phone-id",
        },
    )

    submission, errors = validate_reauth_submission(
        entry,
        {"password": "testpassword"},
        logger=_LOGGER,
    )

    assert submission is None
    assert errors == {"base": "invalid_entry"}


def test_validate_reconfigure_submission_uses_existing_defaults() -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PHONE: "13800000000",
            CONF_PHONE_ID: "phone-id",
            CONF_PASSWORD_HASH: "stored-hash",
        },
    )

    submission, errors = validate_reconfigure_submission(
        entry,
        {
            CONF_PHONE: "13800000000",
            "password": "testpassword",
        },
        logger=_LOGGER,
    )

    assert errors == {}
    assert submission is not None
    assert submission.phone == "13800000000"
    assert submission.phone_id == "phone-id"
    assert submission.remember_password_hash is True


def test_validate_reconfigure_submission_rejects_invalid_phone_id_type() -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PHONE: "13800000000",
            CONF_PHONE_ID: 12345,
            CONF_PASSWORD_HASH: "stored-hash",
        },
    )

    submission, errors = validate_reconfigure_submission(
        entry,
        {
            CONF_PHONE: "13800000000",
            "password": "testpassword",
        },
        logger=_LOGGER,
    )

    assert submission is None
    assert errors == {"base": "invalid_entry"}
