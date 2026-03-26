"""Phase 74 cleanup and closeout guards."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

from .governance_current_truth import LEGACY_ARCHIVED_CLOSEOUT_POINTER_LABEL
from .test_governance_closeout_guards import (
    _assert_public_docs_hide_internal_route_story,
)

_ROOT = repo_root(Path(__file__))


def test_phase74_removed_service_registration_compat_shell() -> None:
    assert not (
        _ROOT / "custom_components" / "lipro" / "services" / "registrations.py"
    ).exists()


def test_phase74_gitignore_drops_phase12_special_case() -> None:
    text = (_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "Phase 12" not in text
    assert "!.planning/phases/*/*.md" in text


def test_phase74_docs_index_keeps_internal_route_private() -> None:
    text = (_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    _assert_public_docs_hide_internal_route_story(
        text,
        LEGACY_ARCHIVED_CLOSEOUT_POINTER_LABEL,
    )


def test_phase74_retired_stubs_fail_fast_honestly() -> None:
    for relative_path in ("scripts/agent_worker.py", "scripts/orchestrator.py"):
        text = (_ROOT / relative_path).read_text(encoding="utf-8")
        assert "return 2" in text
        assert "exit successfully" not in text
        assert "历史重构档案不再保留在仓库中" not in text


def test_phase74_topicized_thin_shells_use_collection_guard() -> None:
    text = (_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")

    assert "pytest_ignore_collect" in text
    assert "tests/core/test_share_client.py" in text
    assert "tests/core/coordinator/runtime/test_command_runtime.py" in text
