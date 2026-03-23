"""Phase 45 production-hotspot typed-budget guards for diagnostics/share/message hotspots."""

from __future__ import annotations

from pathlib import Path
import re
from typing import TypedDict

from scripts.check_file_matrix import repo_root

_ROOT = repo_root(Path(__file__))
_ANY_LINE_RE = re.compile(r"\bAny\b")
_BROAD_CATCH_LINE_RE = re.compile(r"except Exception|with suppress\(Exception\)")
_TARGET_ROOT = _ROOT / "custom_components" / "lipro"


class _AnyBudgetEntry(TypedDict):
    sanctioned_any: dict[str, int]
    backlog_any: dict[str, int]


class _BroadCatchBudgetEntry(TypedDict):
    expected_count: int
    semantic_markers: dict[str, int]


_TYPE_GUARD_TARGETS = {
    "core/api/diagnostics_api_service.py",
    "core/anonymous_share/share_client.py",
    "services/share.py",
    "core/mqtt/message_processor.py",
    "core/coordinator/runtime/mqtt/message_handler.py",
}

_ANY_BUDGET: dict[str, _AnyBudgetEntry] = {
    "core/mqtt/message_processor.py": {
        "sanctioned_any": {
            "from typing import TYPE_CHECKING, Any, Protocol, cast": 1,
            "parse_payload: Callable[[Any], dict[str, Any]],": 1,
            "on_message: Callable[[str, dict[str, Any]], None] | None,": 1,
        },
        "backlog_any": {},
    },
}

_BROAD_CATCH_BUDGET: dict[str, _BroadCatchBudgetEntry] = {
    "core/api/diagnostics_api_service.py": {
        "expected_count": 0,
        "semantic_markers": {},
    },
    "core/anonymous_share/share_client.py": {
        "expected_count": 0,
        "semantic_markers": {},
    },
    "services/share.py": {
        "expected_count": 0,
        "semantic_markers": {},
    },
    "core/mqtt/message_processor.py": {
        "expected_count": 0,
        "semantic_markers": {},
    },
    "core/coordinator/runtime/mqtt/message_handler.py": {
        "expected_count": 0,
        "semantic_markers": {},
    },
}


def _resolve_target(relative_path: str) -> Path:
    return _TARGET_ROOT / relative_path


def _count_matching_lines(path: Path, pattern: re.Pattern[str]) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if pattern.search(line))


def test_phase45_production_hotspot_any_budget_is_explicitly_classified() -> None:
    classified_paths = set(_ANY_BUDGET)

    for relative_path, budget in _ANY_BUDGET.items():
        path = _resolve_target(relative_path)
        text = path.read_text(encoding="utf-8")

        expected_count = 0
        for markers in (budget["sanctioned_any"], budget["backlog_any"]):
            for marker, expected in markers.items():
                assert text.count(marker) == expected, f"{relative_path} marker drift: {marker}"
                expected_count += expected

        assert _count_matching_lines(path, _ANY_LINE_RE) == expected_count

    for relative_path in sorted(_TYPE_GUARD_TARGETS - classified_paths):
        assert _count_matching_lines(_resolve_target(relative_path), _ANY_LINE_RE) == 0


def test_phase45_production_hotspot_broad_catch_budget_is_no_growth() -> None:
    for relative_path, budget in _BROAD_CATCH_BUDGET.items():
        path = _resolve_target(relative_path)
        text = path.read_text(encoding="utf-8")
        assert _count_matching_lines(path, _BROAD_CATCH_LINE_RE) == budget["expected_count"]
        for marker, expected in budget["semantic_markers"].items():
            assert text.count(marker) == expected, f"{relative_path} marker drift: {marker}"


def test_phase45_production_hotspot_files_remain_type_ignore_free() -> None:
    for relative_path in sorted(_TYPE_GUARD_TARGETS):
        path = _resolve_target(relative_path)
        assert "type: ignore" not in path.read_text(encoding="utf-8")
