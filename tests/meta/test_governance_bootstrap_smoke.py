"""Focused bootstrap smoke guards for the active route and archive-transition truth."""

from __future__ import annotations

from .conftest import _DOCS_README, _ISSUE_CONFIG, _ROOT, _load_yaml
from .governance_contract_helpers import (
    _assert_current_route_truth,
    _assert_public_docs_hide_internal_route_story,
    assert_docs_readme_public_contract,
    assert_issue_docs_entry_contact_link,
)
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_ROUTE,
    LATEST_ARCHIVED_EVIDENCE_PATH,
)


def test_active_route_bootstrap_contract_stays_current() -> None:
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    verification_text = (
        _ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md"
    ).read_text(encoding="utf-8")

    _assert_current_route_truth(project_text, roadmap_text, state_text)

    assert CURRENT_ROUTE in project_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in project_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in roadmap_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in state_text
    assert CURRENT_ROUTE in verification_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in verification_text
    assert (
        f"**Latest archived pointer:** `{LATEST_ARCHIVED_EVIDENCE_PATH}`"
        in verification_text
    )
    assert "tests/meta/test_governance_bootstrap_smoke.py" in verification_text
    assert "tests/meta/test_governance_route_handoff_smoke.py" in verification_text
    assert "tests/meta/test_phase94_typed_boundary_guards.py" in verification_text
    assert (
        "tests/meta/test_phase95_hotspot_decomposition_guards.py" in verification_text
    )
    assert "tests/meta/test_phase96_sanitizer_burndown_guards.py" in verification_text
    assert (
        "tests/meta/test_phase97_governance_assurance_freeze_guards.py"
        in verification_text
    )
    assert "tests/meta/test_phase98_route_reactivation_guards.py" in verification_text
    assert "tests/meta/test_phase99_runtime_hotspot_support_guards.py" in verification_text


def test_public_docs_keep_internal_bootstrap_story_hidden() -> None:
    docs_text = _DOCS_README.read_text(encoding="utf-8")
    _assert_public_docs_hide_internal_route_story(docs_text)


def test_docs_entry_contract_stays_in_sync_with_issue_documentation_link() -> None:
    docs_text = _DOCS_README.read_text(encoding="utf-8")
    issue_config = _load_yaml(_ISSUE_CONFIG)

    assert_docs_readme_public_contract(docs_text)
    assert_issue_docs_entry_contact_link(issue_config)
