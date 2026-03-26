"""Protocol and command-contract dependency-story guards."""
from __future__ import annotations

from .dependency_guard_helpers import _ROOT


def test_phase_52_request_policy_and_protocol_root_dependency_story_is_explicit() -> (
    None
):
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    request_policy_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "request_policy.py"
    ).read_text(encoding="utf-8")
    request_gateway_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "request_gateway.py"
    ).read_text(encoding="utf-8")
    transport_executor_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "transport_executor.py"
    ).read_text(encoding="utf-8")
    transport_retry_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "api" / "transport_retry.py"
    ).read_text(encoding="utf-8")
    protocol_rest_methods_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "protocol"
        / "protocol_facade_rest_methods.py"
    ).read_text(encoding="utf-8")

    assert (
        "## Phase 52 Request-Policy / Protocol-Root Clarifications" in dependency_text
    )
    assert "protocol_facade_rest_methods.py" in dependency_text
    assert "RequestPolicy" in dependency_text
    assert "RestRequestGateway" in dependency_text
    assert "RestTransportExecutor" in dependency_text
    assert "explicit policy-owned pacing" in request_policy_text
    assert "localized collaborator, not a second" in request_gateway_text
    assert "policy-owned 429 decisions" in transport_executor_text
    assert "policy-owned rate-limit decisions" in transport_retry_text
    assert (
        "support-only rest child-facing method surface"
        in protocol_rest_methods_text.lower()
    )
    assert "compute_exponential_retry_wait_time()" in residual_text

def test_phase_57_typed_command_result_dependency_story_is_explicit() -> None:
    dependency_text = (
        _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
    ).read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(
        encoding="utf-8"
    )
    result_policy_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "command" / "result_policy.py"
    ).read_text(encoding="utf-8")
    result_text = (
        _ROOT / "custom_components" / "lipro" / "core" / "command" / "result.py"
    ).read_text(encoding="utf-8")
    sender_text = (
        _ROOT
        / "custom_components"
        / "lipro"
        / "core"
        / "coordinator"
        / "runtime"
        / "command"
        / "sender.py"
    ).read_text(encoding="utf-8")
    diagnostics_types_text = (
        _ROOT / "custom_components" / "lipro" / "services" / "diagnostics" / "types.py"
    ).read_text(encoding="utf-8")

    assert "## Phase 57 Typed Command-Result Contract Clarifications" in dependency_text
    assert "result_policy.py` 与 `custom_components/lipro/core/command/result.py` 共同组成 command-result formal contract family" in dependency_text
    assert "sender.py` 只能经 `custom_components/lipro/core/command/result.py` 读取 shared typed command-result contract" in dependency_text
    assert "Command-result stringly-typed outcome contract" in residual_text
    assert "已在 Phase 57 关闭" in residual_text
    assert "is_terminal_command_result_state" in result_policy_text
    assert "COMMAND_VERIFICATION_RESULT_TIMEOUT" in result_text
    assert "COMMAND_VERIFICATION_RESULT_TIMEOUT" in sender_text
    assert "CommandResultPollingState" in diagnostics_types_text
