"""Tests for log-safety helpers and placeholder sanitization."""

from __future__ import annotations

from custom_components.lipro.core.coordinator import LiproDataUpdateCoordinator
from custom_components.lipro.core.utils.log_safety import (
    mask_ip_addresses,
    safe_error_placeholder,
    summarize_properties_for_log,
)


class TestMaskIpAddresses:
    """Tests for mask_ip_addresses."""

    def test_masks_valid_ipv4_and_ipv6(self) -> None:
        assert mask_ip_addresses("peer=192.168.1.10") == "peer=[IP]"
        assert mask_ip_addresses("addr=fe80::1") == "addr=[IP]"

    def test_invalid_ipv4_not_masked(self) -> None:
        # Matches regex, but should be rejected by ipaddress.IPv4Address parsing.
        assert (
            mask_ip_addresses("peer=999.999.999.999 retry=1")
            == "peer=999.999.999.999 retry=1"
        )

    def test_empty_text_passthrough(self) -> None:
        assert mask_ip_addresses("") == ""

    def test_empty_placeholder_passthrough(self) -> None:
        assert (
            mask_ip_addresses("peer=192.168.1.10", placeholder="")
            == "peer=192.168.1.10"
        )


class TestSummarizePropertiesForLog:
    """Tests for summarize_properties_for_log."""

    def test_none_returns_empty_summary(self) -> None:
        assert summarize_properties_for_log(None) == {"count": 0, "keys": []}

    def test_mapping_collects_stringified_keys(self) -> None:
        summary = summarize_properties_for_log({1: "x", "powerState": "1"})
        assert summary == {"count": 2, "keys": ["1", "powerState"]}

    def test_sequence_collects_only_string_key_fields(self) -> None:
        summary = summarize_properties_for_log(
            [{"key": "powerState", "value": "1"}, {"key": 2, "value": "x"}, object()],
        )
        assert summary == {"count": 1, "keys": ["powerState"]}


class TestSafeErrorPlaceholder:
    """Tests for safe_error_placeholder."""

    def test_bool_code_does_not_render_code(self) -> None:
        err = RuntimeError("token=secret")
        err.code = True  # type: ignore[attr-defined]
        assert safe_error_placeholder(err) == "RuntimeError"

    def test_int_code_renders_marker(self) -> None:
        err = RuntimeError("boom")
        err.code = 401  # type: ignore[attr-defined]
        assert safe_error_placeholder(err) == "RuntimeError(code=401)"

    def test_str_code_renders_trimmed(self) -> None:
        err = RuntimeError("boom")
        err.code = " 401 "  # type: ignore[attr-defined]
        assert safe_error_placeholder(err) == "RuntimeError(code=401)"

    def test_empty_code_falls_back_to_name(self) -> None:
        err = RuntimeError("boom")
        err.code = " "  # type: ignore[attr-defined]
        assert safe_error_placeholder(err) == "RuntimeError"


class TestCoordinatorErrorMarkerValidation:
    """Tests for coordinator safe error marker validation."""

    def test_accepts_structured_marker(self) -> None:
        assert LiproDataUpdateCoordinator._is_safe_error_marker(
            "RuntimeError(code=401)",
        )

    def test_rejects_marker_with_whitespace(self) -> None:
        assert not LiproDataUpdateCoordinator._is_safe_error_marker(
            "RuntimeError(code=401) leaked",
        )

    def test_rejects_marker_with_wrong_inner_format(self) -> None:
        assert not LiproDataUpdateCoordinator._is_safe_error_marker(
            "RuntimeError(error=401)",
        )

    def test_rejects_marker_with_disallowed_code_char(self) -> None:
        assert not LiproDataUpdateCoordinator._is_safe_error_marker(
            "RuntimeError(code=401#)",
        )


class TestCoordinatorAuthPlaceholderSanitization:
    """Tests for coordinator auth placeholder sanitization logic."""

    def test_exception_value_is_sanitized(self) -> None:
        err = RuntimeError("access_token=secret")
        sanitized = LiproDataUpdateCoordinator._sanitize_auth_placeholders(
            {"error": err}
        )

        assert sanitized["error"] == "RuntimeError"
        assert "secret" not in sanitized["error"]

    def test_error_digits_allowed(self) -> None:
        sanitized = LiproDataUpdateCoordinator._sanitize_auth_placeholders(
            {"error": "401"}
        )
        assert sanitized["error"] == "401"

    def test_structured_error_marker_allowed(self) -> None:
        marker = "RuntimeError(code=401)"
        sanitized = LiproDataUpdateCoordinator._sanitize_auth_placeholders(
            {"error": marker}
        )
        assert sanitized["error"] == marker

    def test_unsafe_error_string_replaced_with_generic(self) -> None:
        sanitized = LiproDataUpdateCoordinator._sanitize_auth_placeholders(
            {"error": "boom 401"},
        )
        assert sanitized["error"] == "AuthError"

    def test_empty_values_are_dropped(self) -> None:
        sanitized = LiproDataUpdateCoordinator._sanitize_auth_placeholders(
            {"error": " ", "detail": "  "},
        )
        assert sanitized == {}

    def test_non_error_values_are_trimmed(self) -> None:
        sanitized = LiproDataUpdateCoordinator._sanitize_auth_placeholders(
            {"detail": "  hello  "},
        )
        assert sanitized == {"detail": "hello"}
