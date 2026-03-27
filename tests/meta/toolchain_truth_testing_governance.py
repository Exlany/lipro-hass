"""Testing-map and derived-governance topology truth guards."""

from __future__ import annotations

from pathlib import Path
import re

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))

_CODEBASE_DIR = _ROOT / ".planning" / "codebase"

_TESTING_MAP = _ROOT / ".planning" / "codebase" / "TESTING.md"



_TESTING_COUNTS_RE = re.compile(
    r"Repository counts from current scanning: `\d+` Python files under `tests`, `(?P<total>\d+)` runnable `test_\*\.py` files, `(?P<meta>\d+)` meta suites, `(?P<integration>\d+)` integration suites, `(?P<snapshot>\d+)` snapshot suites, `(?P<benchmark>\d+)` benchmark suites, and `(?P<fixture_readmes>\d+)` fixture family READMEs\."
)



def _count_testing_inventory() -> dict[str, int]:
    tests_root = _ROOT / "tests"
    test_files = sorted(tests_root.rglob("test_*.py"))
    fixture_readmes = sorted((tests_root / "fixtures").glob("*/README.md"))
    return {
        "total": len(test_files),
        "meta": sum(
            1 for path in test_files if path.is_relative_to(tests_root / "meta")
        ),
        "integration": sum(
            1 for path in test_files if path.is_relative_to(tests_root / "integration")
        ),
        "benchmark": sum(
            1 for path in test_files if path.is_relative_to(tests_root / "benchmarks")
        ),
        "snapshot": sum(
            1 for path in test_files if path.is_relative_to(tests_root / "snapshots")
        ),
        "fixture_readmes": len(fixture_readmes),
    }



def test_testing_map_counts_and_script_boundary_notes_match_repo_facts() -> None:
    """Derived testing map should track current counts and explicit script/test boundary notes."""
    testing_text = _TESTING_MAP.read_text(encoding="utf-8")
    match = _TESTING_COUNTS_RE.search(testing_text)
    assert match is not None

    documented = {key: int(value) for key, value in match.groupdict().items()}
    assert documented == _count_testing_inventory()
    assert "scripts/check_architecture_policy.py" in testing_text
    assert "scripts/check_file_matrix.py" in testing_text
    assert "tests/conftest.py" in testing_text
    assert "tests/core/test_init.py" in testing_text
    assert "tests/meta/test_dependency_guards.py" in testing_text
    assert "tests/meta/test_governance_milestone_archives.py" in testing_text
    assert "tests/meta/test_governance_release_contract.py" in testing_text
    assert "tests/meta/toolchain_truth_docs_fast_path.py" in testing_text
    assert "tests/meta/test_phase89_tooling_decoupling_guards.py" in testing_text
    assert "script-owned helper truth" in testing_text
    assert "focused `tests/meta` guards" in testing_text



def test_codebase_maps_publish_snapshot_freshness_and_authority_boundaries() -> None:
    for path in sorted(_CODEBASE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")

        assert "Snapshot:" in text, path.as_posix()
        assert "Freshness:" in text, path.as_posix()
        assert "Derived collaboration map" in text, path.as_posix()

        if path.name == "README.md":
            assert "Authority order:" in text, path.as_posix()
            assert "Conflict rule:" in text, path.as_posix()
            assert "不得自称当前治理真源" in text, path.as_posix()
            continue

        assert "Authority:" in text, path.as_posix()
        assert "不得反向充当当前治理真源" in text, path.as_posix()
