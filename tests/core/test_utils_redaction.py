"""Tests for share-friendly identifier redaction helpers."""

from __future__ import annotations

import pytest

from custom_components.lipro.core.utils.redaction import redact_identifier


@pytest.mark.parametrize("value", [None, "", "   "])
def test_redact_identifier_returns_none_for_empty_inputs(value: str | None) -> None:
    assert redact_identifier(value) is None


def test_redact_identifier_masks_short_and_long_identifiers() -> None:
    assert redact_identifier("12345678") == "***"
    assert redact_identifier(" 03ab5ccd7c123456 ") == "03ab***3456"
