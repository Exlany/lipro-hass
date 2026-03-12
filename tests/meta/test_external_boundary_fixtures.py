"""Meta guards for external-boundary fixture families."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_FIXTURE_ROOT = _ROOT / "tests" / "fixtures" / "external_boundaries"

_EXPECTED_FIXTURES = {
    "share_worker/anonymous_share_report.canonical.json",
    "share_worker/developer_feedback_report.canonical.json",
    "share_worker/lite_report.canonical.json",
    "support_payload/developer_feedback_service.canonical.json",
    "support_payload/anonymous_share_preview_response.json",
    "support_payload/submit_anonymous_share_response.json",
    "firmware/remote_advisory.verified_versions.json",
    "firmware/remote_advisory.firmware_list.json",
    "diagnostics_capabilities/query_command_result.success.json",
    "diagnostics_capabilities/body_sensor_history.success.json",
    "diagnostics_capabilities/door_sensor_history.success.json",
}


def test_external_boundary_fixture_family_is_complete() -> None:
    existing = {
        str(path.relative_to(_FIXTURE_ROOT))
        for path in _FIXTURE_ROOT.rglob("*.json")
    }

    assert _EXPECTED_FIXTURES.issubset(existing)


def test_external_boundary_fixture_readme_documents_placeholders() -> None:
    readme = (_FIXTURE_ROOT / "README.md").read_text(encoding="utf-8")

    assert "__INTEGRATION_VERSION__" in readme
    assert "<generated_at>" in readme
    assert "<timestamp>" in readme


def test_phase_1_truth_fixtures_are_not_duplicated_in_external_boundary_dir() -> None:
    diagnostics_dir = _FIXTURE_ROOT / "diagnostics_capabilities"

    assert not (diagnostics_dir / "get_city.success.json").exists()
    assert not (diagnostics_dir / "query_user_cloud.success.json").exists()
