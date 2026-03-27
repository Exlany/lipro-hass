"""Phase 89 tooling-kernel decoupling regression guards."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_CHECKER = _ROOT / "scripts" / "check_architecture_policy.py"
_SCRIPT_ARCH = _ROOT / "scripts" / "lib" / "architecture_policy.py"
_SCRIPT_AST = _ROOT / "scripts" / "lib" / "ast_guard_utils.py"
_TEST_ARCH = _ROOT / "tests" / "helpers" / "architecture_policy.py"
_TEST_AST = _ROOT / "tests" / "helpers" / "ast_guard_utils.py"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase89_checker_consumes_script_owned_helpers_only() -> None:
    checker_text = _read_text(_CHECKER)

    assert "tests.helpers.architecture_policy" not in checker_text
    assert "tests.helpers.ast_guard_utils" not in checker_text
    assert "sys.path.insert" not in checker_text
    assert "from scripts.lib.architecture_policy import" in checker_text
    assert "from scripts.lib.ast_guard_utils import" in checker_text
    assert "from lib.architecture_policy import" in checker_text
    assert "from lib.ast_guard_utils import" in checker_text


def test_phase89_tests_helpers_are_thin_re_exports_only() -> None:
    architecture_helper_text = _read_text(_TEST_ARCH)
    ast_helper_text = _read_text(_TEST_AST)

    assert "from scripts.lib.architecture_policy import" in architecture_helper_text
    assert "from scripts.lib.ast_guard_utils import" in ast_helper_text
    assert "@dataclass" not in architecture_helper_text
    assert "def policy_root" not in architecture_helper_text
    assert "def load_structural_rules" not in architecture_helper_text
    assert "def iter_import_modules" not in ast_helper_text
    assert "ast.parse" not in ast_helper_text


def test_phase89_script_lib_is_the_real_helper_home() -> None:
    architecture_text = _read_text(_SCRIPT_ARCH)
    ast_text = _read_text(_SCRIPT_AST)

    assert "@dataclass(frozen=True, slots=True)" in architecture_text
    assert "def policy_root" in architecture_text
    assert "def load_structural_rules" in architecture_text
    assert "def iter_import_modules" in ast_text
    assert "def extract_all" in ast_text
