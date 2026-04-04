"""Phase 31 runtime typed-budget, repo-wide typing-bucket, and broad-catch guards."""

from __future__ import annotations

from pathlib import Path
import re
from typing import TypedDict

from scripts.check_file_matrix import repo_root

_ROOT = repo_root(Path(__file__))
_ANY_LINE_RE = re.compile(r"\bAny\b")
_BROAD_CATCH_LINE_RE = re.compile(r"except Exception|with suppress\(Exception\)")
_TYPE_IGNORE_LINE_RE = re.compile(r"type:[ ]ignore")
_TARGET_ROOT = _ROOT / "custom_components" / "lipro"
_TESTS_ROOT = _ROOT / "tests"
_META_ROOT = _TESTS_ROOT / "meta"


class _AnyBudgetEntry(TypedDict):
    sanctioned_any: dict[str, int]
    backlog_any: dict[str, int]


class _BroadCatchBudgetEntry(TypedDict):
    expected_count: int
    semantic_markers: dict[str, int]


_TYPE_GUARD_TARGETS = {
    "core/coordinator/coordinator.py",
    "core/coordinator/lifecycle.py",
    "core/coordinator/runtime/mqtt_runtime.py",
    "core/coordinator/mqtt_lifecycle.py",
    "core/coordinator/runtime/device/filter.py",
    "core/coordinator/runtime/state/updater.py",
    "core/coordinator/runtime/device_runtime.py",
    "core/coordinator/runtime/device/snapshot.py",
    "core/coordinator/services/command_service.py",
    "core/utils/background_task_manager.py",
    "services/diagnostics/helpers.py",
    "services/diagnostics/helper_support.py",
    "services/maintenance.py",
    "select.py",
    "sensor.py",
}

_ANY_BUDGET: dict[str, _AnyBudgetEntry] = {
    "core/coordinator/runtime/device/snapshot.py": {
        "sanctioned_any": {
            "from typing import TYPE_CHECKING, Any, Protocol, cast": 1,
        },
        "backlog_any": {
            "sync_mesh_group_extra_data(device, cast(dict[str, Any], row))": 1,
        },
    },
    "core/utils/background_task_manager.py": {
        "sanctioned_any": {
            "from typing import Any": 1,
            "create_task: Callable[[Coroutine[Any, Any, Any]], asyncio.Task[Any]],": 1,
            "self._tasks: set[asyncio.Task[Any]] = set()": 1,
            "def tasks(self) -> set[asyncio.Task[Any]]:": 1,
            "coro: Coroutine[Any, Any, Any],": 1,
            "Callable[[Coroutine[Any, Any, Any]], asyncio.Task[Any]] | None": 1,
            ") -> asyncio.Task[Any]:": 1,
            "def on_done(self, task: asyncio.Task[Any]) -> None:": 1,
        },
        "backlog_any": {},
    },
}

_BROAD_CATCH_BUDGET: dict[str, _BroadCatchBudgetEntry] = {
    "core/coordinator/lifecycle.py": {
        "expected_count": 0,
        "semantic_markers": {
            "failed during best-effort shutdown": 1,
            '_LOGGER.exception("Unexpected update failure")': 1,
        },
    },
    "core/coordinator/runtime/mqtt_runtime_support.py": {
        "expected_count": 0,
        "semantic_markers": {
            "MQTT %s failed": 1,
        },
    },
    "core/coordinator/mqtt_lifecycle.py": {
        "expected_count": 0,
        "semantic_markers": {
            'stage="message_bridge"': 1,
            "Failed to setup MQTT": 1,
        },
    },
    "core/coordinator/runtime/device_runtime.py": {
        "expected_count": 0,
        "semantic_markers": {
            "self._last_refresh_failure = self._classify_refresh_failure(": 1,
            "retaining last-known-good snapshot": 2,
        },
    },
    "core/coordinator/runtime/device/snapshot.py": {
        "expected_count": 0,
        "semantic_markers": {
            'stage="mesh_group_topology"': 1,
            'stage="fetch_page"': 1,
            'stage="parse_device"': 1,
        },
    },
    "services/diagnostics/helpers.py": {
        "expected_count": 0,
        "semantic_markers": {},
    },
    "services/diagnostics/helper_support.py": {
        "expected_count": 0,
        "semantic_markers": {
            "Skip one %s capability due to error (%s)": 1,
            "Skip one %s capability due to unexpected error (%s)": 2,
        },
    },
    "services/maintenance.py": {
        "expected_count": 0,
        "semantic_markers": {},
    },
}

_REPO_WIDE_PRODUCTION_ANY_EXPECTED = 208
_REPO_WIDE_TESTS_ANY_NON_META_EXPECTED = 162

_TESTS_TYPE_IGNORE_BUDGET = {}

_META_GUARD_ANY_LITERAL_BUDGET = {
    "tests/meta/test_phase31_runtime_budget_guards.py": 10,
    "tests/meta/test_phase45_hotspot_budget_guards.py": 6,
    "tests/meta/test_phase94_typed_boundary_guards.py": 16,
}

_META_SUPPORT_ANY_BUDGET = {
    "tests/meta/test_blueprints.py": 3,
    "tests/meta/test_evidence_pack_authority.py": 2,
    "tests/meta/public_surface_runtime_contracts.py": 1,
    "tests/meta/test_version_sync.py": 3,
}

_META_GUARD_TYPE_IGNORE_LITERAL_BUDGET = {
    "tests/meta/test_phase31_runtime_budget_guards.py": 1,
    "tests/meta/test_phase45_hotspot_budget_guards.py": 1,
    "tests/meta/test_phase50_rest_typed_budget_guards.py": 1,
    "tests/meta/test_phase61_formal_home_budget_guards.py": 1,
}


def _resolve_target(relative_path: str) -> Path:
    return _TARGET_ROOT / relative_path


def _resolve_repo_path(relative_path: str) -> Path:
    return _ROOT / relative_path


def _count_matching_lines(path: Path, pattern: re.Pattern[str]) -> int:
    return sum(
        1
        for line in path.read_text(encoding="utf-8").splitlines()
        if pattern.search(line)
    )


def _iter_python_files_under(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*.py") if "__pycache__" not in path.parts
    )


def _count_matching_lines_in_files(paths: list[Path], pattern: re.Pattern[str]) -> int:
    return sum(_count_matching_lines(path, pattern) for path in paths)


def _assert_literal_budget(budget: dict[str, int], pattern: re.Pattern[str]) -> None:
    for relative_path, expected in budget.items():
        path = _resolve_repo_path(relative_path)
        assert _count_matching_lines(path, pattern) == expected, relative_path


def test_phase31_remaining_any_budget_is_explicitly_classified() -> None:
    classified_paths = set(_ANY_BUDGET)

    for relative_path, budget in _ANY_BUDGET.items():
        path = _resolve_target(relative_path)
        text = path.read_text(encoding="utf-8")

        expected_count = 0
        for markers in (budget["sanctioned_any"], budget["backlog_any"]):
            for marker, expected in markers.items():
                assert text.count(marker) == expected, (
                    f"{relative_path} marker drift: {marker}"
                )
                expected_count += expected

        assert _count_matching_lines(path, _ANY_LINE_RE) == expected_count

    for relative_path in sorted(_TYPE_GUARD_TARGETS - classified_paths):
        assert _count_matching_lines(_resolve_target(relative_path), _ANY_LINE_RE) == 0


def test_phase31_broad_catch_budget_is_no_growth() -> None:
    classified_paths = set(_BROAD_CATCH_BUDGET)

    for relative_path, budget in _BROAD_CATCH_BUDGET.items():
        path = _resolve_target(relative_path)
        text = path.read_text(encoding="utf-8")
        assert (
            _count_matching_lines(path, _BROAD_CATCH_LINE_RE)
            == budget["expected_count"]
        )
        for marker, expected in budget["semantic_markers"].items():
            assert text.count(marker) == expected, (
                f"{relative_path} marker drift: {marker}"
            )

    for relative_path in sorted(_TYPE_GUARD_TARGETS - classified_paths):
        assert (
            _count_matching_lines(_resolve_target(relative_path), _BROAD_CATCH_LINE_RE)
            == 0
        )


def test_phase31_targeted_production_files_remain_type_ignore_free() -> None:
    for relative_path in sorted(_TYPE_GUARD_TARGETS):
        path = _resolve_target(relative_path)
        assert "type: ignore" not in path.read_text(encoding="utf-8")


def test_repo_wide_production_any_bucket_is_explicit() -> None:
    production_files = _iter_python_files_under(_TARGET_ROOT)
    assert (
        _count_matching_lines_in_files(production_files, _ANY_LINE_RE)
        == _REPO_WIDE_PRODUCTION_ANY_EXPECTED
    )


def test_repo_wide_production_type_ignore_bucket_remains_zero() -> None:
    production_files = _iter_python_files_under(_TARGET_ROOT)
    assert _count_matching_lines_in_files(production_files, _TYPE_IGNORE_LINE_RE) == 0


def test_repo_wide_tests_any_non_meta_bucket_is_explicit() -> None:
    test_files = [
        path
        for path in _iter_python_files_under(_TESTS_ROOT)
        if path.relative_to(_TESTS_ROOT).parts[0] != "meta"
    ]
    assert (
        _count_matching_lines_in_files(test_files, _ANY_LINE_RE)
        == _REPO_WIDE_TESTS_ANY_NON_META_EXPECTED
    )


def test_repo_wide_tests_type_ignore_bucket_is_explicit() -> None:
    _assert_literal_budget(_TESTS_TYPE_IGNORE_BUDGET, _TYPE_IGNORE_LINE_RE)

    actual_files = {
        str(path.relative_to(_ROOT))
        for path in _iter_python_files_under(_TESTS_ROOT)
        if path.relative_to(_TESTS_ROOT).parts[0] != "meta"
        and _count_matching_lines(path, _TYPE_IGNORE_LINE_RE)
    }
    assert actual_files == set(_TESTS_TYPE_IGNORE_BUDGET)


def test_repo_wide_meta_any_buckets_are_explicit() -> None:
    _assert_literal_budget(_META_GUARD_ANY_LITERAL_BUDGET, _ANY_LINE_RE)
    _assert_literal_budget(_META_SUPPORT_ANY_BUDGET, _ANY_LINE_RE)

    actual_files = {
        str(path.relative_to(_ROOT))
        for path in _iter_python_files_under(_META_ROOT)
        if _count_matching_lines(path, _ANY_LINE_RE)
    }
    expected_files = set(_META_GUARD_ANY_LITERAL_BUDGET) | set(_META_SUPPORT_ANY_BUDGET)
    assert actual_files == expected_files


def test_repo_wide_meta_guard_type_ignore_literals_are_explicit() -> None:
    _assert_literal_budget(_META_GUARD_TYPE_IGNORE_LITERAL_BUDGET, _TYPE_IGNORE_LINE_RE)

    actual_files = {
        str(path.relative_to(_ROOT))
        for path in _iter_python_files_under(_META_ROOT)
        if _count_matching_lines(path, _TYPE_IGNORE_LINE_RE)
    }
    assert actual_files == set(_META_GUARD_TYPE_IGNORE_LITERAL_BUDGET)
