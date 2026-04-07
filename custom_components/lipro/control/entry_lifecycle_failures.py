"""Typed lifecycle failure contracts for config-entry orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

type LifecycleStage = Literal["setup", "unload", "reload"]
type LifecycleHandlingPolicy = Literal[
    "cleanup_and_raise",
    "log_and_continue",
    "propagate",
]
type LifecycleContractName = Literal[
    "setup_auth_failed",
    "setup_failed",
    "setup_not_ready",
    "unload_shutdown_degraded",
    "reload_auth_failed",
    "reload_failed",
    "reload_not_ready",
]
type SetupLifecycleFailure = (
    ConfigEntryAuthFailed
    | ConfigEntryNotReady
    | RuntimeError
    | OSError
    | TimeoutError
    | ValueError
)
type ReloadLifecycleFailure = SetupLifecycleFailure
type UnloadLifecycleFailure = RuntimeError | OSError | TimeoutError | ValueError

DEGRADABLE_UNLOAD_EXCEPTIONS = (
    RuntimeError,
    OSError,
    TimeoutError,
    ValueError,
)

SETUP_FAILURE_EXCEPTIONS = (
    ConfigEntryAuthFailed,
    ConfigEntryNotReady,
    RuntimeError,
    OSError,
    TimeoutError,
    ValueError,
)

RELOAD_FAILURE_EXCEPTIONS = SETUP_FAILURE_EXCEPTIONS


@dataclass(frozen=True, slots=True)
class LifecycleFailureContract:
    """Named lifecycle failure contract for one control-plane branch."""

    stage: LifecycleStage
    contract_name: LifecycleContractName
    handling_policy: LifecycleHandlingPolicy
    error_type: str


def classify_setup_failure(error: SetupLifecycleFailure) -> LifecycleFailureContract:
    """Classify one setup failure into a named arbitration contract."""
    if isinstance(error, ConfigEntryAuthFailed):
        contract_name: LifecycleContractName = "setup_auth_failed"
    elif isinstance(error, ConfigEntryNotReady):
        contract_name = "setup_not_ready"
    else:
        contract_name = "setup_failed"
    return LifecycleFailureContract(
        stage="setup",
        contract_name=contract_name,
        handling_policy="cleanup_and_raise",
        error_type=type(error).__name__,
    )


def classify_unload_failure(error: UnloadLifecycleFailure) -> LifecycleFailureContract:
    """Classify one unload degradation into a named arbitration contract."""
    return LifecycleFailureContract(
        stage="unload",
        contract_name="unload_shutdown_degraded",
        handling_policy="log_and_continue",
        error_type=type(error).__name__,
    )


def classify_reload_failure(error: ReloadLifecycleFailure) -> LifecycleFailureContract:
    """Classify one reload failure into a named arbitration contract."""
    if isinstance(error, ConfigEntryAuthFailed):
        contract_name: LifecycleContractName = "reload_auth_failed"
    elif isinstance(error, ConfigEntryNotReady):
        contract_name = "reload_not_ready"
    else:
        contract_name = "reload_failed"
    return LifecycleFailureContract(
        stage="reload",
        contract_name=contract_name,
        handling_policy="propagate",
        error_type=type(error).__name__,
    )


__all__ = [
    "DEGRADABLE_UNLOAD_EXCEPTIONS",
    "RELOAD_FAILURE_EXCEPTIONS",
    "SETUP_FAILURE_EXCEPTIONS",
    "LifecycleFailureContract",
    "ReloadLifecycleFailure",
    "SetupLifecycleFailure",
    "UnloadLifecycleFailure",
    "classify_reload_failure",
    "classify_setup_failure",
    "classify_unload_failure",
]
