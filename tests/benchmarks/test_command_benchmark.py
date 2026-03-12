"""Benchmark coverage for command-result classification."""

from __future__ import annotations

from custom_components.lipro.core.command.result import classify_command_result_payload


def test_command_result_classifier_benchmark(benchmark) -> None:
    payload = {
        "code": 0,
        "message": "ok",
        "success": True,
        "msgSn": "abc123",
        "pushSuccess": True,
    }

    result = benchmark(classify_command_result_payload, payload)

    assert result == "confirmed"
