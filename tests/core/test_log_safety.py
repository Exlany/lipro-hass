"""Tests for log-safety helpers and placeholder sanitization."""

from __future__ import annotations

from typing import Protocol, cast

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

    def test_invalid_ipv6_not_masked(self) -> None:
        # Matches regex, but is rejected by ipaddress.IPv6Address parsing (multiple '::').
        assert mask_ip_addresses("addr=fe80::1::2") == "addr=fe80::1::2"

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


class _SupportsCode(Protocol):
    """Typed view for exceptions that expose a dynamic ``code`` attribute."""

    code: object


class TestSafeErrorPlaceholder:
    """Tests for safe_error_placeholder."""

    def test_bool_code_does_not_render_code(self) -> None:
        err = RuntimeError("token=secret")
        coded_err = cast(_SupportsCode, err)
        coded_err.code = True
        assert safe_error_placeholder(err) == "RuntimeError"

    def test_int_code_renders_marker(self) -> None:
        err = RuntimeError("boom")
        coded_err = cast(_SupportsCode, err)
        coded_err.code = 401
        assert safe_error_placeholder(err) == "RuntimeError(code=401)"

    def test_str_code_renders_trimmed(self) -> None:
        err = RuntimeError("boom")
        coded_err = cast(_SupportsCode, err)
        coded_err.code = " 401 "
        assert safe_error_placeholder(err) == "RuntimeError(code=401)"

    def test_empty_code_falls_back_to_name(self) -> None:
        err = RuntimeError("boom")
        coded_err = cast(_SupportsCode, err)
        coded_err.code = " "
        assert safe_error_placeholder(err) == "RuntimeError"
