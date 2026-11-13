"""Unexpected upload failures must not format untrusted exception details."""

import logging

import pytest

from custom_components.lipro.core.anonymous_share.share_client_submit_outcomes import (
    build_unexpected_submit_outcome,
)


class _CustomError(ValueError):
    def __str__(self) -> str:
        return "fictional-custom-secret"


@pytest.mark.parametrize(
    "err",
    [
        OSError(5, "fictional-message-secret", "/fictional-filename-secret"),
        _CustomError("fictional-message-secret"),
        ValueError("fictional-message-secret"),
    ],
)
def test_unexpected_upload_does_not_log_exception_details(err, caplog) -> None:
    err.__cause__ = RuntimeError("fictional-cause-secret")
    err.add_note("fictional-note-secret")
    original_args = err.args
    with caplog.at_level(logging.ERROR):
        outcome = build_unexpected_submit_outcome(
            err,
            label="Anonymous share",
            logger=logging.getLogger(__name__),
            reason_code="unexpected_error",
            failure_category="unexpected",
            handling_policy="escalate",
        )

    assert "fictional-" not in caplog.text
    assert type(err).__name__ in caplog.text
    assert err.args == original_args
    assert outcome.failure_summary["error_type"] == type(err).__name__
    assert outcome.reason_code == "unexpected_error"
    assert outcome.failure_summary["handling_policy"] == "escalate"
