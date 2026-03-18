"""Phase 31 runtime typed-budget and broad-catch no-growth guards."""

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
    "core/coordinator/coordinator.py",
    "core/coordinator/runtime/mqtt_runtime.py",
    "core/coordinator/mqtt_lifecycle.py",
    "core/coordinator/runtime/device/filter.py",
    "core/coordinator/runtime/state/updater.py",
    "core/coordinator/runtime/device_runtime.py",
    "core/coordinator/runtime/device/snapshot.py",
    "services/diagnostics/helpers.py",
    "services/maintenance.py",
    "select.py",
    "sensor.py",
}

_ANY_BUDGET: dict[str, _AnyBudgetEntry] = {
    "core/coordinator/runtime/mqtt_runtime.py": {
        "sanctioned_any": {
            "from typing import TYPE_CHECKING, Any, Protocol, TypeVar, cast": 1,
            "coro: Coroutine[Any, Any, Any],": 2,
            "create_task: Callable[[Coroutine[Any, Any, Any]], asyncio.Task[Any]] | None = None,": 1,
            ") -> asyncio.Task[Any]:": 1,
        },
        "backlog_any": {},
    },
    "core/coordinator/runtime/device/snapshot.py": {
        "sanctioned_any": {
            "from typing import TYPE_CHECKING, Any, Protocol, cast": 1,
        },
        "backlog_any": {
            "sync_mesh_group_extra_data(device, cast(dict[str, Any], row))": 1,
        },
    },
}

_BROAD_CATCH_BUDGET: dict[str, _BroadCatchBudgetEntry] = {
    "core/coordinator/coordinator.py": {
        "expected_count": 2,
        "semantic_markers": {
            "failed during best-effort shutdown": 1,
            '_LOGGER.exception("Unexpected update failure")': 1,
        },
    },
    "core/coordinator/runtime/mqtt_runtime.py": {
        "expected_count": 1,
        "semantic_markers": {
            "MQTT %s failed": 1,
        },
    },
    "core/coordinator/mqtt_lifecycle.py": {
        "expected_count": 2,
        "semantic_markers": {
            'stage="message_bridge"': 1,
            "Failed to setup MQTT": 1,
        },
    },
    "core/coordinator/runtime/device_runtime.py": {
        "expected_count": 2,
        "semantic_markers": {
            "self._last_refresh_failure = self._classify_refresh_failure(": 2,
            "retaining last-known-good snapshot": 2,
        },
    },
    "core/coordinator/runtime/device/snapshot.py": {
        "expected_count": 3,
        "semantic_markers": {
            'stage="mesh_group_topology"': 1,
            'stage="fetch_page"': 1,
            'stage="parse_device"': 1,
        },
    },
    "services/diagnostics/helpers.py": {
        "expected_count": 3,
        "semantic_markers": {
            "Skip one %s capability due to error (%s)": 2,
            "Skip one %s capability due to unexpected error (%s)": 1,
        },
    },
    "services/maintenance.py": {
        "expected_count": 1,
        "semantic_markers": {
            "Config entry reload failed after device registry update (%s, %s)": 1,
        },
    },
}


def _resolve_target(relative_path: str) -> Path:
    return _TARGET_ROOT / relative_path


def _count_matching_lines(path: Path, pattern: re.Pattern[str]) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if pattern.search(line))


def test_phase31_remaining_any_budget_is_explicitly_classified() -> None:
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


def test_phase31_broad_catch_budget_is_no_growth() -> None:
    classified_paths = set(_BROAD_CATCH_BUDGET)

    for relative_path, budget in _BROAD_CATCH_BUDGET.items():
        path = _resolve_target(relative_path)
        text = path.read_text(encoding="utf-8")
        assert _count_matching_lines(path, _BROAD_CATCH_LINE_RE) == budget["expected_count"]
        for marker, expected in budget["semantic_markers"].items():
            assert text.count(marker) == expected, f"{relative_path} marker drift: {marker}"

    for relative_path in sorted(_TYPE_GUARD_TARGETS - classified_paths):
        assert _count_matching_lines(_resolve_target(relative_path), _BROAD_CATCH_LINE_RE) == 0


def test_phase31_targeted_production_files_remain_type_ignore_free() -> None:
    for relative_path in sorted(_TYPE_GUARD_TARGETS):
        path = _resolve_target(relative_path)
        assert "type: ignore" not in path.read_text(encoding="utf-8")
