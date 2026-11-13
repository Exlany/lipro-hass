"""Tests for share-friendly identifier redaction helpers."""

from __future__ import annotations

import pytest

from custom_components.lipro.core.utils.redaction import (
    DIAGNOSTICS_REDACTION_MARKERS,
    SHARE_REDACTION_MARKERS,
    looks_sensitive_value,
    redact_identifier,
    redact_sensitive_literal,
    redact_sensitive_text,
)


@pytest.mark.parametrize("value", [None, "", "   "])
def test_redact_identifier_returns_none_for_empty_inputs(value: str | None) -> None:
    assert redact_identifier(value) is None


def test_redact_identifier_masks_short_and_long_identifiers() -> None:
    assert redact_identifier("12345678") == "***"
    assert redact_identifier(" 03ab5ccd7c123456 ") == "03ab***3456"


@pytest.mark.parametrize(
    "markers", [DIAGNOSTICS_REDACTION_MARKERS, SHARE_REDACTION_MARKERS]
)
def test_token_redaction_preserves_each_sink_marker(markers) -> None:
    token = "SyntheticToken0123456789" * 3
    assert redact_sensitive_literal(token, markers=markers) == markers.token
    assert redact_sensitive_text(token, markers=markers) == markers.token
    assert "Synthetic" not in redact_sensitive_text(
        f'{{"access_token": "{token}"}}', markers=markers
    )


def test_blank_text_is_not_a_secret() -> None:
    assert looks_sensitive_value("   ") is False
    assert redact_sensitive_literal("   ", markers=SHARE_REDACTION_MARKERS) is None
