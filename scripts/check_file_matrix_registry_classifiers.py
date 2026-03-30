"""Focused classifier rules for file-matrix registry paths."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.check_file_matrix_registry_shared import (
        ClassifierRule,
        ExactRuleFamily,
        FileGovernanceRow,
        PrefixRuleFamily,
        build_exact_rules,
        build_prefix_rules,
        row_for_path,
    )
elif __package__ in {None, ""}:
    from check_file_matrix_registry_shared import (
        ClassifierRule,
        ExactRuleFamily,
        FileGovernanceRow,
        PrefixRuleFamily,
        build_exact_rules,
        build_prefix_rules,
        row_for_path,
    )
else:
    from scripts.check_file_matrix_registry_shared import (
        ClassifierRule,
        ExactRuleFamily,
        FileGovernanceRow,
        PrefixRuleFamily,
        build_exact_rules,
        build_prefix_rules,
        row_for_path,
    )

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

_COMPONENT_EXACT_RULES: tuple[ClassifierRule, ...] = build_exact_rules(
    ExactRuleFamily(
        area="Protocol",
        owner_phase="Phase 2",
        fate="重构",
        residual_rows=(
            ("custom_components/lipro/core/api/diagnostics_api_ota.py", "OTA diagnostics outward helper home"),
            ("custom_components/lipro/core/api/diagnostics_api_ota_support.py", "OTA diagnostics mechanics support seam"),
        ),
    ),
    ExactRuleFamily(
        area="Protocol",
        owner_phase="Phase 7.1",
        residual_rows=(("custom_components/lipro/core/protocol/boundary/mqtt_decoder.py", "canonical MQTT topic/payload decode authority"),),
    ),
    ExactRuleFamily(
        area="Protocol",
        owner_phase="Phase 2.5",
        fate="重构",
        residual_rows=(("custom_components/lipro/core/mqtt/topics.py", "MQTT boundary-backed topic adapter"),),
    ),
    ExactRuleFamily(
        area="Assurance",
        owner_phase="Phase 7.3",
        residual_rows=(
            ("custom_components/lipro/core/telemetry/json_payloads.py", "telemetry helper home for JSON-safe payload builders"),
            ("custom_components/lipro/core/telemetry/outcomes.py", "telemetry helper home for outcome semantics"),
        ),
    ),
    ExactRuleFamily(
        area="Control",
        owner_phase="Phase 7.3",
        paths=("custom_components/lipro/control/telemetry_surface.py",),
    ),
    ExactRuleFamily(
        area="Control",
        owner_phase="Phase 3",
        residual_rows=(("custom_components/lipro/services/diagnostics/helper_support.py", "diagnostics service mechanics support seam"),),
    ),
    ExactRuleFamily(
        area="Control",
        owner_phase="Phase 103",
        residual_rows=(("custom_components/lipro/control/entry_root_support.py", "root-entry lazy-load / entry-auth / service-registry adapter support home"),),
    ),
    ExactRuleFamily(
        area="Control",
        owner_phase="Phase 104",
        residual_rows=(
            ("custom_components/lipro/control/service_router_command_handlers.py", "focused command handler family home for service-router callbacks"),
            ("custom_components/lipro/control/service_router_schedule_handlers.py", "focused schedule handler family home for service-router callbacks"),
            ("custom_components/lipro/control/service_router_share_handlers.py", "focused anonymous-share handler family home for service-router callbacks"),
            ("custom_components/lipro/control/service_router_diagnostics_handlers.py", "focused diagnostics/developer handler family home for service-router callbacks"),
            ("custom_components/lipro/control/service_router_maintenance_handlers.py", "focused maintenance handler family home for service-router callbacks"),
        ),
    ),
    ExactRuleFamily(
        area="Runtime",
        owner_phase="Phase 104",
        residual_rows=(("custom_components/lipro/core/coordinator/runtime/command_runtime_outcome_support.py", "command-runtime localized outcome support collaborator"),),
    ),
    ExactRuleFamily(
        area="Domain",
        owner_phase="Phase 4",
        fate="重构",
        residual_rows=(("custom_components/lipro/core/device/extras_support.py", "DeviceExtras payload / panel parsing support helper home"),),
    ),
)

_COMPONENT_PREFIX_RULES: tuple[ClassifierRule, ...] = build_prefix_rules(
    PrefixRuleFamily(area="Protocol", owner_phase="Phase 2", fate="重构", prefixes=("custom_components/lipro/core/api/",)),
    PrefixRuleFamily(area="Protocol", owner_phase="Phase 7.1", prefixes=("custom_components/lipro/core/protocol/boundary/",)),
    PrefixRuleFamily(area="Protocol", owner_phase="Phase 2.5", prefixes=("custom_components/lipro/core/protocol/",)),
    PrefixRuleFamily(area="Protocol", owner_phase="Phase 2.5", fate="重构", prefixes=("custom_components/lipro/core/mqtt/",)),
    PrefixRuleFamily(area="Protocol", owner_phase="Phase 2.6", prefixes=("custom_components/lipro/core/anonymous_share/",)),
    PrefixRuleFamily(area="Assurance", owner_phase="Phase 7.3", prefixes=("custom_components/lipro/core/telemetry/",)),
    PrefixRuleFamily(area="Control", owner_phase="Phase 3", prefixes=("custom_components/lipro/control/", "custom_components/lipro/services/", "custom_components/lipro/flow/")),
    PrefixRuleFamily(area="Domain", owner_phase="Phase 4", prefixes=("custom_components/lipro/core/capability/", "custom_components/lipro/entities/")),
    PrefixRuleFamily(area="Domain", owner_phase="Phase 4", fate="重构", prefixes=("custom_components/lipro/core/device/",)),
    PrefixRuleFamily(area="Runtime", owner_phase="Phase 5", fate="重构", prefixes=("custom_components/lipro/core/coordinator/",)),
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

_TEST_EXACT_RULES: tuple[ClassifierRule, ...] = build_exact_rules(
    ExactRuleFamily(area="Assurance", owner_phase="Phase 7.4", paths=("tests/meta/test_protocol_replay_assets.py",)),
    ExactRuleFamily(area="Assurance", owner_phase="Phase 8", paths=("tests/meta/test_evidence_pack_authority.py",)),
    ExactRuleFamily(
        area="Assurance",
        owner_phase="Phase 77",
        residual_rows=(("tests/meta/test_governance_bootstrap_smoke.py", "focused bootstrap smoke guard home"),),
    ),
    ExactRuleFamily(
        area="Assurance",
        owner_phase="Phase 79 / 105",
        residual_rows=(
            ("tests/meta/test_governance_route_handoff_smoke.py", "route-handoff gsd fast-path smoke guard home"),
            ("tests/meta/governance_followup_route_current_milestones.py", "governance-route contract + current/latest archive pointer-drift guard"),
        ),
    ),
    ExactRuleFamily(area="Assurance", owner_phase="Phase 77", residual_rows=(("tests/meta/governance_promoted_assets.py", "shared promoted-phase-asset helper home"),)),
    ExactRuleFamily(area="Assurance", owner_phase="Phase 79", residual_rows=(("tests/meta/test_governance_release_docs.py", "release/docs topic suite home"), ("tests/meta/test_governance_release_continuity.py", "release continuity/custody topic suite home"))),
    ExactRuleFamily(area="Assurance", owner_phase="Phase 6 / 77", residual_rows=(("tests/meta/test_version_sync.py", "version/runtime metadata sync guard home"),)),
    ExactRuleFamily(area="Assurance", owner_phase="Phase 8", paths=("tests/harness/__init__.py", "tests/integration/test_ai_debug_evidence_pack.py", "tests/integration/test_protocol_replay_harness.py")),
    ExactRuleFamily(area="Runtime", owner_phase="Phase 7.3", paths=("tests/integration/test_telemetry_exporter_integration.py",)),
    ExactRuleFamily(area="Protocol", owner_phase="Phase 7.4", paths=("tests/core/api/test_protocol_replay_rest.py", "tests/core/mqtt/test_protocol_replay_mqtt.py")),
    ExactRuleFamily(area="Control", owner_phase="Phase 27", paths=("tests/core/test_init_service_handlers.py",)),
    ExactRuleFamily(area="Control", owner_phase="Phase 3 / 7", paths=("tests/core/test_init.py",)),
    ExactRuleFamily(area="Cross-cutting", owner_phase="Phase 18", paths=("tests/core/test_auth_bootstrap.py",)),
    ExactRuleFamily(area="Assurance", owner_phase="Phase 6", paths=("tests/conftest.py", "tests/conftest_shared.py")),
    ExactRuleFamily(
        area="Assurance",
        owner_phase="Phase 103",
        residual_rows=(
            ("tests/coordinator_double.py", "shared coordinator double helper home"),
            ("tests/topicized_collection.py", "topicized thin-shell collection hook home"),
            ("tests/meta/test_phase103_root_thinning_guards.py", "focused predecessor guard home for Phase 103 root thinning / test topology / terminology normalization"),
        ),
    ),
    ExactRuleFamily(
        area="Assurance",
        owner_phase="Phase 104",
        residual_rows=(("tests/meta/test_phase104_service_router_runtime_split_guards.py", "focused predecessor guard home for Phase 104 service-router/runtime split"),),
    ),
    ExactRuleFamily(
        area="Assurance",
        owner_phase="Phase 105",
        residual_rows=(
            ("tests/meta/governance_followup_route_specs.py", "shared follow-up route spec + planning-doc snapshot helper home"),
            ("tests/meta/test_phase105_governance_freeze_guards.py", "focused latest-archived closeout guard home for Phase 105 governance freeze"),
        ),
    ),
    ExactRuleFamily(
        area="Assurance",
        owner_phase="Phase 107",
        residual_rows=(("tests/meta/test_phase107_rest_status_hotspot_guards.py", "focused predecessor guard home for Phase 107 REST/auth/status hotspot convergence"),),
    ),
    ExactRuleFamily(
        area="Assurance",
        owner_phase="Phase 108",
        residual_rows=(("tests/meta/test_phase108_mqtt_transport_de_friendization_guards.py", "focused predecessor guard home for Phase 108 MQTT transport-runtime de-friendization"),),
    ),
    ExactRuleFamily(
        area="Assurance",
        owner_phase="Phase 109",
        residual_rows=(("tests/meta/test_phase109_anonymous_share_manager_inward_decomposition_guards.py", "focused predecessor guard home for Phase 109 anonymous-share manager inward decomposition"),),
    ),
    ExactRuleFamily(
        area="Assurance",
        owner_phase="Phase 110",
        residual_rows=(("tests/meta/test_phase110_runtime_snapshot_closeout_guards.py", "focused active-route guard home for Phase 110 runtime snapshot surface reduction and milestone closeout"),),
    ),
)

_TEST_PREFIX_RULES: tuple[ClassifierRule, ...] = build_prefix_rules(
    PrefixRuleFamily(area="Assurance", owner_phase="Phase 6", prefixes=("tests/meta/", "tests/snapshots/", "tests/helpers/")),
    PrefixRuleFamily(area="Assurance", owner_phase="Phase 8", prefixes=("tests/harness/evidence_pack/",)),
    PrefixRuleFamily(area="Assurance", owner_phase="Phase 7.4", prefixes=("tests/harness/protocol/",)),
    PrefixRuleFamily(area="Protocol", owner_phase="Phase 2.5 / 6", prefixes=("tests/core/mqtt/",)),
    PrefixRuleFamily(area="Runtime", owner_phase="Phase 5 / 6", prefixes=("tests/core/coordinator/", "tests/integration/")),
    PrefixRuleFamily(area="Protocol", owner_phase="Phase 2", prefixes=("tests/core/api/",)),
    PrefixRuleFamily(area="Assurance", owner_phase="Phase 7.3", prefixes=("tests/core/telemetry/",)),
    PrefixRuleFamily(area="Domain", owner_phase="Phase 4", prefixes=("tests/core/capability/", "tests/core/device/", "tests/entities/", "tests/platforms/")),
    PrefixRuleFamily(area="Control", owner_phase="Phase 3 / 7", prefixes=("tests/services/", "tests/flows/")),
)

_SCRIPT_EXACT_RULES: tuple[ClassifierRule, ...] = build_exact_rules(
    ExactRuleFamily(area="Assurance", owner_phase="Phase 8", paths=("scripts/export_ai_debug_evidence_pack.py",)),
    ExactRuleFamily(
        area="Assurance",
        owner_phase="Phase 79 / 105",
        residual_rows=(
            ("scripts/check_file_matrix_registry_shared.py", "registry shared type + row/family builder home"),
            ("scripts/check_file_matrix_registry_overrides.py", "registry override-family home"),
            ("scripts/check_file_matrix_registry_classifiers.py", "registry classifier-rule home"),
        ),
    ),
)

_SCRIPT_PREFIX_RULES: tuple[ClassifierRule, ...] = build_prefix_rules(
    PrefixRuleFamily(area="Assurance", owner_phase="Phase 6 / 7", prefixes=("scripts/",)),
)


def _match_exact_rule(path: str, rules: Sequence[ClassifierRule]) -> FileGovernanceRow | None:
    for candidate, (area, owner_phase, fate, residual) in rules:
        if path == candidate:
            return row_for_path(path, area, owner_phase, fate, residual)
    return None


def _match_prefix_rule(path: str, rules: Sequence[ClassifierRule]) -> FileGovernanceRow | None:
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
