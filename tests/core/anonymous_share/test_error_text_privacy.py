"""Redact sensitive error text before limiting the report length."""

import pytest

from custom_components.lipro.core.anonymous_share.collector import (
    AnonymousShareCollector,
)
from custom_components.lipro.core.anonymous_share.sanitize import sanitize_string


@pytest.mark.parametrize(
    "message",
    [
        '{"password": "fictional-secret"}',
        'response={"accessToken": "fictional-secret',
        '{"password": "prefix\\"fictional-secret"}',
        '{"authorization": "Bearer fictional-secret"}',
        '{"clientSecret": "fictional-secret\\',
    ],
)
def test_error_string_redacts_json_secrets(message) -> None:
    assert "fictional-secret" not in sanitize_string(message)


def test_error_string_preserves_safe_json_metadata() -> None:
    message = '{"status": "bad response", "access_token_present": "yes"}'
    assert sanitize_string(message) == message


def test_error_string_redacts_numeric_identifier() -> None:
    assert sanitize_string('{"user_id": 987654}') == '{"user_id": "[REDACTED]"}'


@pytest.mark.parametrize("source", ["api", "parse", "command"])
def test_error_collection_redacts_before_truncation(source) -> None:
    collector = AnonymousShareCollector()
    collector.set_enabled(True)
    message = "ordinary text " * 13 + " " + "SyntheticToken0123456789" * 3
    if source == "api":
        collector.record_api_error("/test", 500, message)
    elif source == "parse":
        collector.record_parse_error("test", ValueError(message))
    else:
        collector.record_command_error("test", "light", 500, message)

    assert len(collector.errors) == 1
    assert "Synthetic" not in collector.errors[0].message
    assert "[TOKEN]" in collector.errors[0].message
