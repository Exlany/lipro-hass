"""Focused predecessor guards for Phase 101 anonymous-share and REST-boundary freeze."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_contract_helpers import assert_testing_inventory_snapshot
from .governance_current_truth import CURRENT_MILESTONE_DEFAULT_NEXT, CURRENT_ROUTE

_ROOT = repo_root(Path(__file__))
_PROJECT = _ROOT / ".planning" / "PROJECT.md"
_ROADMAP = _ROOT / ".planning" / "ROADMAP.md"
_REQUIREMENTS = _ROOT / ".planning" / "REQUIREMENTS.md"
_STATE = _ROOT / ".planning" / "STATE.md"
_MILESTONES = _ROOT / ".planning" / "MILESTONES.md"
_AUDIT = _ROOT / ".planning" / "v1.27-MILESTONE-AUDIT.md"
_VERIFICATION_MATRIX = _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
_PUBLIC_SURFACES = _ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md"
_DEPENDENCY_MATRIX = _ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_TESTING = _ROOT / ".planning" / "codebase" / "TESTING.md"
_CONCERNS = _ROOT / ".planning" / "codebase" / "CONCERNS.md"
_DEV_ARCH = _ROOT / "docs" / "developer_architecture.md"
_MANAGER = _ROOT / "custom_components" / "lipro" / "core" / "anonymous_share" / "manager.py"
_MANAGER_SUBMISSION = _ROOT / "custom_components" / "lipro" / "core" / "anonymous_share" / "manager_submission.py"
_MANAGER_SUPPORT = _ROOT / "custom_components" / "lipro" / "core" / "anonymous_share" / "manager_support.py"
_MQTT_API_SERVICE = _ROOT / "custom_components" / "lipro" / "core" / "api" / "mqtt_api_service.py"
_REST_DECODER_SUPPORT = _ROOT / "custom_components" / "lipro" / "core" / "protocol" / "boundary" / "rest_decoder_support.py"
_REST_DECODER = _ROOT / "custom_components" / "lipro" / "core" / "protocol" / "boundary" / "rest_decoder.py"
_REST_FACADE_ENDPOINT_METHODS = _ROOT / "custom_components" / "lipro" / "core" / "api" / "rest_facade_endpoint_methods.py"
_PHASE101_DIR = (
    _ROOT
    / ".planning"
    / "phases"
    / "101-anonymous-share-manager-and-rest-decoder-hotspot-decomposition-freeze"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase101_previous_archived_docs_and_closeout_bundle_align() -> None:
    project_text = _read(_PROJECT)
    roadmap_text = _read(_ROADMAP)
    requirements_text = _read(_REQUIREMENTS)
    state_text = _read(_STATE)
    milestones_text = _read(_MILESTONES)
    audit_text = _read(_AUDIT)
    verification_text = _read(_VERIFICATION_MATRIX)
    dev_arch_text = _read(_DEV_ARCH)
    phase101_summary = _read(_PHASE101_DIR / "101-03-SUMMARY.md")

    for text in (
        project_text,
        roadmap_text,
        requirements_text,
        state_text,
        milestones_text,
        verification_text,
    ):
        assert CURRENT_ROUTE in text
        assert CURRENT_MILESTONE_DEFAULT_NEXT in text

    assert "Final Carry-Forward Eradication & Route Reactivation" in audit_text
    assert "v1.27 active route / Phase 101 complete / latest archived baseline = v1.26" in audit_text
    assert "$gsd-complete-milestone v1.27" not in audit_text
    assert "[To be planned]" not in roadmap_text
    assert "**Plans:** 0 plans" not in roadmap_text
    assert "run /gsd:plan-phase 101 to break down" not in roadmap_text
    assert "Phase 101 Anonymous-share Manager / REST Decoder Hotspot Decomposition Freeze Note" in dev_arch_text
    assert "Phase 101" in phase101_summary


def test_phase101_maps_and_ledgers_project_previous_archived_hotspot_truth() -> None:
    file_matrix_text = _read(_FILE_MATRIX)
    testing_text = _read(_TESTING)
    verification_text = _read(_VERIFICATION_MATRIX)
    concerns_text = _read(_CONCERNS)
    public_surfaces_text = _read(_PUBLIC_SURFACES)
    dependency_text = _read(_DEPENDENCY_MATRIX)

    assert "tests/meta/test_phase101_anonymous_share_rest_boundary_guards.py" in file_matrix_text
    assert "focused predecessor guard home for Phase 101 anonymous-share / REST-boundary hotspot decomposition / governance freeze" in file_matrix_text
    assert_testing_inventory_snapshot(testing_text)
    assert "tests/meta/test_phase101_anonymous_share_rest_boundary_guards.py" in verification_text
    assert "## Phase 101 Anonymous-share Manager / REST Decoder Hotspot Decomposition Freeze" in verification_text
    assert "Phase 101 已把 `anonymous_share/manager.py` 收窄到 435 行 formal manager home" in concerns_text
    assert "manager_submission.py`、`share_client_{flows,ports,refresh,submit}.py`" in public_surfaces_text
    assert "manager_submission.py` 只是 inward collaborator" in dependency_text


def test_phase101_anonymous_share_and_rest_boundary_formal_homes_preserve_single_route() -> None:
    manager_text = _read(_MANAGER)
    manager_submission_text = _read(_MANAGER_SUBMISSION)
    manager_support_text = _read(_MANAGER_SUPPORT)
    rest_decoder_support_text = _read(_REST_DECODER_SUPPORT)
    rest_decoder_text = _read(_REST_DECODER)
    mqtt_api_service_text = _read(_MQTT_API_SERVICE)
    endpoint_methods_text = _read(_REST_FACADE_ENDPOINT_METHODS)

    assert "get_anonymous_share_manager" not in manager_text
    assert "_get_root_manager" not in manager_text
    assert "def _submit_share_payload_with_outcome(" not in manager_text
    assert "def _async_submit_share_payload(" not in manager_text
    assert "def _has_pending_report_data(" not in manager_text
    assert "def _should_skip_report_submission(" not in manager_text
    assert "_aggregate_submit_outcome" in manager_text
    assert "def _primary_manager(" in manager_text
    assert "def _submit_child_managers(" in manager_submission_text
    assert "def configure_scope_state(" in manager_support_text
    assert "def load_reported_device_keys_for_state(" in manager_support_text
    assert "def _normalize_pagination_offset(" in rest_decoder_support_text
    assert "def _should_include_fallback_property(" in rest_decoder_support_text
    assert "_FALLBACK_PROPERTY_EXCLUDED_KEYS" in rest_decoder_support_text
    assert "_build_schedule_json_fingerprint(" in rest_decoder_text
    assert "from importlib import import_module" in mqtt_api_service_text
    assert "custom_components.lipro.core.protocol.boundary" in mqtt_api_service_text
    assert "decode_mqtt_config_payload" in mqtt_api_service_text
    assert "child-facing typed" in endpoint_methods_text
