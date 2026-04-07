"""Phase 89 docs/metadata/governance route convergence guards."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_README = _ROOT / "README.md"
_README_ZH = _ROOT / "README_zh.md"
_DOCS = _ROOT / "docs" / "README.md"
_MANIFEST = _ROOT / "custom_components" / "lipro" / "manifest.json"
_REGISTRY = _ROOT / ".planning" / "baseline" / "GOVERNANCE_REGISTRY.json"
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_RESIDUAL_LEDGER = _ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md"
_KILL_LIST = _ROOT / ".planning" / "reviews" / "KILL_LIST.md"
_BUG = _ROOT / ".github" / "ISSUE_TEMPLATE" / "bug.yml"
_FEATURE = _ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml"


def _load_yaml(path: Path) -> dict[str, object]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_phase89_entry_surfaces_keep_docs_first_story_aligned() -> None:
    docs_text = _DOCS.read_text(encoding="utf-8")
    readme_text = _README.read_text(encoding="utf-8")
    readme_zh_text = _README_ZH.read_text(encoding="utf-8")

    for text in (readme_text, readme_zh_text):
        assert "docs/README.md" in text
        assert "SUPPORT.md" in text
        assert "SECURITY.md" in text
        assert "private-access" in text or "私有" in text

    assert "First-Hop Matrix" in docs_text
    assert "Current access-mode truth" in docs_text
    assert "conditional follow-up surfaces" in docs_text
    assert "SUPPORT.md" in docs_text
    assert "SECURITY.md" in docs_text


def test_phase89_manifest_and_registry_route_bug_support_honestly() -> None:
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    registry = json.loads(_REGISTRY.read_text(encoding="utf-8"))
    bug_template = _load_yaml(_BUG)
    feature_template = _load_yaml(_FEATURE)

    assert manifest["documentation"].endswith('/docs/README.md')
    assert manifest["issue_tracker"].endswith('/SUPPORT.md')
    assert registry["support"]["documentation_route"] == 'docs/README.md'
    assert registry["support"]["usage_route"] == 'docs/TROUBLESHOOTING.md -> SUPPORT.md'
    assert 'GitHub Issues (conditional)' in registry["support"]["bug_route"]
    assert 'GitHub Discussions (conditional)' in registry["support"]["feature_route"]

    bug_text = json.dumps(bug_template, ensure_ascii=False)
    feature_text = json.dumps(feature_template, ensure_ascii=False)
    assert 'docs/TROUBLESHOOTING.md' in bug_text
    assert 'SUPPORT.md' in bug_text
    assert 'SUPPORT.md' in feature_text


def test_phase89_retired_stub_governance_keeps_delete_gate_explicit() -> None:
    registry = json.loads(_REGISTRY.read_text(encoding="utf-8"))
    file_matrix_text = _FILE_MATRIX.read_text(encoding="utf-8")
    residual_text = _RESIDUAL_LEDGER.read_text(encoding="utf-8")
    kill_list_text = _KILL_LIST.read_text(encoding="utf-8")
    delete_gate = registry["tooling"]["compatibility_stub_delete_gate"]

    assert registry["tooling"]["compatibility_stub_role"] == "retired fail-fast migration hint only"
    assert delete_gate in kill_list_text
    assert "retired fail-fast migration stub only" in file_matrix_text
    assert "not the runtime orchestrator" in file_matrix_text
    assert "migration hint" in residual_text
