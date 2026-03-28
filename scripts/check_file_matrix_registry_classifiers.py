"""Focused classifier rules for file-matrix registry paths."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.check_file_matrix_registry_shared import (
        FileGovernanceRow,
        row_for_path,
    )
elif __package__ in {None, ""}:
    from check_file_matrix_registry_shared import FileGovernanceRow, row_for_path
else:
    from scripts.check_file_matrix_registry_shared import (
        FileGovernanceRow,
        row_for_path,
    )


type ExactRule = tuple[str, tuple[str, str, str, str]]
type PrefixRule = tuple[str, tuple[str, str, str, str]]

_COMPONENT_CONTROL_ROOT_FILES = {
    "custom_components/lipro/__init__.py",
    "custom_components/lipro/diagnostics.py",
    "custom_components/lipro/system_health.py",
    "custom_components/lipro/config_flow.py",
    "custom_components/lipro/runtime_infra.py",
    "custom_components/lipro/coordinator_entry.py",
}

_COMPONENT_DOMAIN_PLATFORM_FILES = {
    "custom_components/lipro/binary_sensor.py",
    "custom_components/lipro/climate.py",
    "custom_components/lipro/cover.py",
    "custom_components/lipro/fan.py",
    "custom_components/lipro/helpers/platform.py",
    "custom_components/lipro/light.py",
    "custom_components/lipro/select.py",
    "custom_components/lipro/sensor.py",
    "custom_components/lipro/switch.py",
    "custom_components/lipro/update.py",
}

_COMPONENT_EXACT_RULES: tuple[ExactRule, ...] = (
    ("custom_components/lipro/core/api/diagnostics_api_ota.py", ("Protocol", "Phase 2", "重构", "OTA diagnostics outward helper home")),
    ("custom_components/lipro/core/api/diagnostics_api_ota_support.py", ("Protocol", "Phase 2", "重构", "OTA diagnostics mechanics support seam")),
    ("custom_components/lipro/core/protocol/boundary/mqtt_decoder.py", ("Protocol", "Phase 7.1", "保留", "canonical MQTT topic/payload decode authority")),
    ("custom_components/lipro/core/mqtt/topics.py", ("Protocol", "Phase 2.5", "重构", "MQTT boundary-backed topic adapter")),
    ("custom_components/lipro/core/telemetry/json_payloads.py", ("Assurance", "Phase 7.3", "保留", "telemetry helper home for JSON-safe payload builders")),
    ("custom_components/lipro/core/telemetry/outcomes.py", ("Assurance", "Phase 7.3", "保留", "telemetry helper home for outcome semantics")),
    ("custom_components/lipro/control/telemetry_surface.py", ("Control", "Phase 7.3", "保留", "-")),
    ("custom_components/lipro/services/diagnostics/helper_support.py", ("Control", "Phase 3", "保留", "diagnostics service mechanics support seam")),
    ("custom_components/lipro/control/entry_root_support.py", ("Control", "Phase 103", "保留", "root-entry lazy-load / entry-auth / service-registry adapter support home")),
    ("custom_components/lipro/core/device/extras_support.py", ("Domain", "Phase 4", "重构", "DeviceExtras payload / panel parsing support helper home")),
)

_COMPONENT_PREFIX_RULES: tuple[PrefixRule, ...] = (
    ("custom_components/lipro/core/api/", ("Protocol", "Phase 2", "重构", "-")),
    ("custom_components/lipro/core/protocol/boundary/", ("Protocol", "Phase 7.1", "保留", "-")),
    ("custom_components/lipro/core/protocol/", ("Protocol", "Phase 2.5", "保留", "-")),
    ("custom_components/lipro/core/mqtt/", ("Protocol", "Phase 2.5", "重构", "-")),
    ("custom_components/lipro/core/anonymous_share/", ("Protocol", "Phase 2.6", "保留", "-")),
    ("custom_components/lipro/core/telemetry/", ("Assurance", "Phase 7.3", "保留", "-")),
    ("custom_components/lipro/control/", ("Control", "Phase 3", "保留", "-")),
    ("custom_components/lipro/services/", ("Control", "Phase 3", "保留", "-")),
    ("custom_components/lipro/flow/", ("Control", "Phase 3", "保留", "-")),
    ("custom_components/lipro/core/capability/", ("Domain", "Phase 4", "保留", "-")),
    ("custom_components/lipro/core/device/", ("Domain", "Phase 4", "重构", "-")),
    ("custom_components/lipro/entities/", ("Domain", "Phase 4", "保留", "-")),
    ("custom_components/lipro/core/coordinator/", ("Runtime", "Phase 5", "重构", "-")),
)

_RUNTIME_TEST_FILES = {
    "tests/core/test_coordinator.py",
    "tests/core/test_coordinator_integration.py",
}

_DOMAIN_TEST_PREFIXES = (
    "tests/core/capability/",
    "tests/core/device/",
    "tests/entities/",
    "tests/platforms/",
)

_CONTROL_TEST_PREFIXES = ("tests/services/", "tests/flows/")

_TEST_EXACT_RULES: tuple[ExactRule, ...] = (
    ("tests/meta/test_protocol_replay_assets.py", ("Assurance", "Phase 7.4", "保留", "-")),
    ("tests/meta/test_evidence_pack_authority.py", ("Assurance", "Phase 8", "保留", "-")),
    ("tests/meta/test_governance_bootstrap_smoke.py", ("Assurance", "Phase 77", "保留", "focused bootstrap smoke guard home")),
    ("tests/meta/test_governance_route_handoff_smoke.py", ("Assurance", "Phase 79", "保留", "route-handoff gsd fast-path smoke guard home")),
("tests/meta/governance_followup_route_current_milestones.py", ("Assurance", "Phase 77 / 79", "保留", "governance-route contract + current/latest archive pointer-drift guard")),
    ("tests/meta/governance_promoted_assets.py", ("Assurance", "Phase 77", "保留", "shared promoted-phase-asset helper home")),
    ("tests/meta/test_governance_closeout_guards.py", ("Assurance", "Phase 27 / 44 / 49 / 77 / 79", "保留", "closeout + promoted-asset manifest smoke anchor")),
    ("tests/meta/test_governance_release_contract.py", ("Assurance", "Phase 33 / 77 / 79", "保留", "release/governance workflow anchor suite")),
    ("tests/meta/test_governance_release_docs.py", ("Assurance", "Phase 79", "保留", "release/docs topic suite home")),
    ("tests/meta/test_governance_release_continuity.py", ("Assurance", "Phase 79", "保留", "release continuity/custody topic suite home")),
    ("tests/meta/test_version_sync.py", ("Assurance", "Phase 6 / 77", "保留", "version/runtime metadata sync guard home")),
    ("tests/harness/__init__.py", ("Assurance", "Phase 7.4", "保留", "-")),
    ("tests/integration/test_ai_debug_evidence_pack.py", ("Assurance", "Phase 8", "保留", "-")),
    ("tests/integration/test_telemetry_exporter_integration.py", ("Runtime", "Phase 7.3", "保留", "-")),
    ("tests/integration/test_protocol_replay_harness.py", ("Assurance", "Phase 7.4", "保留", "-")),
    ("tests/core/api/test_protocol_replay_rest.py", ("Protocol", "Phase 7.4", "保留", "-")),
    ("tests/core/mqtt/test_protocol_replay_mqtt.py", ("Protocol", "Phase 7.4", "保留", "-")),
    ("tests/core/test_init_service_handlers.py", ("Control", "Phase 27", "保留", "-")),
    ("tests/core/test_init.py", ("Control", "Phase 3 / 7", "保留", "-")),
    ("tests/core/test_auth_bootstrap.py", ("Cross-cutting", "Phase 18", "保留", "-")),
    ("tests/conftest.py", ("Assurance", "Phase 6", "保留", "-")),
    ("tests/conftest_shared.py", ("Assurance", "Phase 6", "保留", "-")),
    ("tests/coordinator_double.py", ("Assurance", "Phase 103", "保留", "shared coordinator double helper home")),
    ("tests/topicized_collection.py", ("Assurance", "Phase 103", "保留", "topicized thin-shell collection hook home")),
    ("tests/meta/test_phase103_root_thinning_guards.py", ("Assurance", "Phase 103", "保留", "focused active-route guard home for Phase 103 root thinning / test topology / terminology normalization")),
)

_TEST_PREFIX_RULES: tuple[PrefixRule, ...] = (
    ("tests/meta/", ("Assurance", "Phase 6", "保留", "-")),
    ("tests/harness/evidence_pack/", ("Assurance", "Phase 8", "保留", "-")),
    ("tests/harness/protocol/", ("Assurance", "Phase 7.4", "保留", "-")),
    ("tests/snapshots/", ("Assurance", "Phase 6", "保留", "-")),
    ("tests/core/mqtt/", ("Protocol", "Phase 2.5 / 6", "保留", "-")),
    ("tests/core/coordinator/", ("Runtime", "Phase 5 / 6", "保留", "-")),
    ("tests/integration/", ("Runtime", "Phase 5 / 6", "保留", "-")),
    ("tests/core/api/", ("Protocol", "Phase 2", "保留", "-")),
    ("tests/core/telemetry/", ("Assurance", "Phase 7.3", "保留", "-")),
    ("tests/core/capability/", ("Domain", "Phase 4", "保留", "-")),
    ("tests/core/device/", ("Domain", "Phase 4", "保留", "-")),
    ("tests/entities/", ("Domain", "Phase 4", "保留", "-")),
    ("tests/platforms/", ("Domain", "Phase 4", "保留", "-")),
    ("tests/services/", ("Control", "Phase 3 / 7", "保留", "-")),
    ("tests/flows/", ("Control", "Phase 3 / 7", "保留", "-")),
    ("tests/helpers/", ("Assurance", "Phase 6", "保留", "-")),
)

_SCRIPT_EXACT_RULES: tuple[ExactRule, ...] = (
    ("scripts/export_ai_debug_evidence_pack.py", ("Assurance", "Phase 8", "保留", "-")),
    ("scripts/check_file_matrix_registry_shared.py", ("Assurance", "Phase 79", "保留", "registry shared type + row builder home")),
    ("scripts/check_file_matrix_registry_overrides.py", ("Assurance", "Phase 79", "保留", "registry override-family home")),
    ("scripts/check_file_matrix_registry_classifiers.py", ("Assurance", "Phase 79", "保留", "registry classifier-rule home")),
)

_SCRIPT_PREFIX_RULES: tuple[PrefixRule, ...] = (
    ("scripts/", ("Assurance", "Phase 6 / 7", "保留", "-")),
)


def _match_exact_rule(path: str, rules: Sequence[ExactRule]) -> FileGovernanceRow | None:
    for candidate, (area, owner_phase, fate, residual) in rules:
        if path == candidate:
            return row_for_path(path, area, owner_phase, fate, residual)
    return None


def _match_prefix_rule(path: str, rules: Sequence[PrefixRule]) -> FileGovernanceRow | None:
    for prefix, (area, owner_phase, fate, residual) in rules:
        if path.startswith(prefix):
            return row_for_path(path, area, owner_phase, fate, residual)
    return None


def classify_component_path(path: str) -> FileGovernanceRow | None:
    """Classify one production-component path into its governed registry row."""
    if (row := _match_exact_rule(path, _COMPONENT_EXACT_RULES)) is not None:
        return row
    if (row := _match_prefix_rule(path, _COMPONENT_PREFIX_RULES)) is not None:
        return row
    if path in _COMPONENT_CONTROL_ROOT_FILES:
        return row_for_path(path, "Control", "Phase 3")
    if path in _COMPONENT_DOMAIN_PLATFORM_FILES:
        return row_for_path(path, "Domain", "Phase 4")
    return None


def classify_test_path(path: str) -> FileGovernanceRow | None:
    """Classify one test path into its governed registry row."""
    if (row := _match_exact_rule(path, _TEST_EXACT_RULES)) is not None:
        return row
    if path in _RUNTIME_TEST_FILES:
        return row_for_path(path, "Runtime", "Phase 5 / 6")
    if path.startswith(_DOMAIN_TEST_PREFIXES):
        return row_for_path(path, "Domain", "Phase 4")
    if path.startswith(_CONTROL_TEST_PREFIXES):
        return row_for_path(path, "Control", "Phase 3 / 7")
    return _match_prefix_rule(path, _TEST_PREFIX_RULES)


def classify_script_path(path: str) -> FileGovernanceRow | None:
    """Classify one governance or tooling script path into its registry row."""
    if (row := _match_exact_rule(path, _SCRIPT_EXACT_RULES)) is not None:
        return row
    return _match_prefix_rule(path, _SCRIPT_PREFIX_RULES)
