"""Focused bootstrap smoke guards for active-route and archive-transition truth."""

from __future__ import annotations

from .conftest import _DOCS_README, _ROOT
from .governance_contract_helpers import (
    _assert_latest_archived_route_truth,
    _assert_public_docs_hide_internal_route_story,
)
from .governance_current_truth import (
    CURRENT_MILESTONE_DEFAULT_NEXT,
    CURRENT_ROUTE,
    LATEST_ARCHIVED_EVIDENCE_PATH,
)


def test_active_route_bootstrap_contract_stays_current() -> None:
    project_text = (_ROOT / '.planning' / 'PROJECT.md').read_text(encoding='utf-8')
    roadmap_text = (_ROOT / '.planning' / 'ROADMAP.md').read_text(encoding='utf-8')
    state_text = (_ROOT / '.planning' / 'STATE.md').read_text(encoding='utf-8')
    verification_text = (
        _ROOT / '.planning' / 'baseline' / 'VERIFICATION_MATRIX.md'
    ).read_text(encoding='utf-8')

    _assert_latest_archived_route_truth(project_text, roadmap_text, state_text)

    assert CURRENT_ROUTE in project_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in project_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in roadmap_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in state_text
    assert '## Phase 76 Current-Route Activation Contract' in verification_text
    assert CURRENT_MILESTONE_DEFAULT_NEXT in verification_text
    assert f'**Latest archived pointer:** `{LATEST_ARCHIVED_EVIDENCE_PATH}`' in verification_text
    assert 'tests/meta/test_governance_bootstrap_smoke.py' in verification_text


def test_public_docs_keep_internal_bootstrap_story_hidden() -> None:
    docs_text = _DOCS_README.read_text(encoding='utf-8')
    _assert_public_docs_hide_internal_route_story(docs_text)
