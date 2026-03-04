"""Log-safety helpers for sanitized diagnostics output."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import ipaddress
import re
from typing import Any, Final

_IPV4_CANDIDATE_RE: Final = re.compile(r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)")
_IPV6_CANDIDATE_RE: Final = re.compile(
    r"(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}(?![0-9A-Fa-f:])"
)


def mask_ip_addresses(text: str, *, placeholder: str = "[IP]") -> str:
    """Replace embedded IPv4/IPv6 literals with a placeholder."""
    if not text or not placeholder:
        return text

    def _mask_ipv4(match: re.Match[str]) -> str:
        candidate = match.group(0)
        try:
            ipaddress.IPv4Address(candidate)
        except ipaddress.AddressValueError:
            return candidate
        return placeholder

    def _mask_ipv6(match: re.Match[str]) -> str:
        candidate = match.group(0)
        try:
            ipaddress.IPv6Address(candidate)
        except ipaddress.AddressValueError:
            return candidate
        return placeholder

    result = _IPV4_CANDIDATE_RE.sub(_mask_ipv4, text)
    return _IPV6_CANDIDATE_RE.sub(_mask_ipv6, result)


def summarize_properties_for_log(
    properties: Mapping[str, Any] | Sequence[Mapping[str, Any] | object] | None,
) -> dict[str, int | list[str]]:
    """Return a log-safe properties summary containing only keys and count."""
    keys: list[str] = []

    if isinstance(properties, Mapping):
        keys = [str(key) for key in properties]
    elif isinstance(properties, Sequence):
        for item in properties:
            if not isinstance(item, Mapping):
                continue
            key = item.get("key")
            if isinstance(key, str):
                keys.append(key)

    return {
        "count": len(keys),
        "keys": keys,
    }


def safe_error_placeholder(err: BaseException) -> str:
    """Build a safe error marker without exposing original message content."""
    error_name = type(err).__name__
    code = getattr(err, "code", None)
    if isinstance(code, bool):
        return error_name
    if isinstance(code, (int, str)):
        normalized = str(code).strip()
        if normalized:
            return f"{error_name}(code={normalized})"
    return error_name
