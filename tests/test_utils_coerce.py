"""Tests for shared core coercion helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.lipro.core.utils.coerce import coerce_boollike


def test_coerce_boollike_parses_common_variants() -> None:
    assert coerce_boollike(True) is True
    assert coerce_boollike(False) is False
    assert coerce_boollike(1) is True
    assert coerce_boollike(0) is False
    assert coerce_boollike(2) is True
    assert coerce_boollike(0.0) is False
    assert coerce_boollike(0.5) is True
    assert coerce_boollike(" true ") is True
    assert coerce_boollike("on") is True
    assert coerce_boollike("off") is False
    assert coerce_boollike(" no ") is False


def test_coerce_boollike_uses_default_for_unknown_values() -> None:
    assert coerce_boollike("maybe") is False
    assert coerce_boollike("maybe", default=True) is True
    assert coerce_boollike(None) is False
    assert coerce_boollike(None, default=True) is True
    assert coerce_boollike(object()) is False
    assert coerce_boollike(object(), default=True) is True


def test_coerce_boollike_logs_without_raw_value_content() -> None:
    logger = MagicMock()
    raw_value = "Bearer super-secret-token"

    assert coerce_boollike(raw_value, logger=logger, context="mqtt") is False
    logger.debug.assert_called_once_with(
        "Unexpected %s bool-like string value (len=%d)",
        "mqtt",
        len(raw_value),
    )
