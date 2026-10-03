"""Exercise the local coverage resolver against real, isolated Git histories."""

import os
from pathlib import Path
import shutil
import subprocess

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "lint"


def _run(repo: Path, command: list[str]) -> str:
    return subprocess.run(  # noqa: S603 - fixed tools and generated local repository fixtures
        command,
        cwd=repo,
        env={
            **os.environ,
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
        },
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def _git(repo: Path, *args: str) -> str:
    executable = shutil.which("git")
    assert executable is not None
    return _run(
        repo,
        [
            executable,
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "core.hooksPath=/dev/null",
            *args,
        ],
    )


def _commit_file(repo: Path, filename: str) -> None:
    (repo / filename).write_text("fixture\n")
    _git(repo, "add", filename)
    _git(repo, "commit", "-m", "fixture")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-b", "main")
    _commit_file(tmp_path, "baseline.py")
    _git(tmp_path, "update-ref", "refs/remotes/origin/main", "HEAD")
    return tmp_path


def _surface(repo: Path, tmp_path_factory) -> set[str]:
    script = _SCRIPT.read_text()
    function = script.split("resolve_changed_coverage_surface() {", 1)[1].split(
        "\nfull_mode=0", 1
    )[0]
    output = tmp_path_factory.mktemp("surface") / "changed"
    bash = shutil.which("bash")
    assert bash is not None
    _run(
        repo,
        [
            bash,
            "-c",
            "set -euo pipefail\n"
            "unset GITHUB_EVENT_NAME GITHUB_REF_NAME\n"
            "resolve_changed_coverage_surface() {"
            + function
            + '\nresolve_changed_coverage_surface "$1"',
            "lint-surface-test",
            str(output),
        ],
    )
    return set(output.read_text().splitlines())


def test_feature_branch_includes_all_commits(repo, tmp_path_factory) -> None:
    _git(repo, "switch", "-c", "feature")
    _commit_file(repo, "first.py")
    _commit_file(repo, "second.py")
    assert _surface(repo, tmp_path_factory) == {"first.py", "second.py"}


def test_main_merge_includes_complete_pr(repo, tmp_path_factory) -> None:
    _git(repo, "switch", "-c", "feature")
    _commit_file(repo, "first.py")
    _commit_file(repo, "second.py")
    _git(repo, "switch", "main")
    _git(repo, "merge", "--no-ff", "feature", "-m", "merge fixture")
    assert _surface(repo, tmp_path_factory) == {"first.py", "second.py"}


def test_local_changes_include_staged_unstaged_and_new_files(
    repo, tmp_path_factory
) -> None:
    _git(repo, "switch", "-c", "feature")
    (repo / "baseline.py").write_text("changed\n")
    (repo / "staged.py").write_text("staged\n")
    _git(repo, "add", "staged.py")
    (repo / "new file.py").write_text("new\n")
    assert _surface(repo, tmp_path_factory) == {
        "baseline.py",
        "staged.py",
        "new file.py",
    }


def test_main_linear_commit_uses_previous_commit(repo, tmp_path_factory) -> None:
    _commit_file(repo, "first.py")
    _commit_file(repo, "second.py")
    assert _surface(repo, tmp_path_factory) == {"second.py"}


def test_initial_commit_includes_tracked_files(repo, tmp_path_factory) -> None:
    _git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    assert _surface(repo, tmp_path_factory) == {"baseline.py"}


def test_unborn_repository_includes_new_files(tmp_path, tmp_path_factory) -> None:
    _git(tmp_path, "init", "-b", "main")
    (tmp_path / "first.py").write_text("fixture\n")
    assert _surface(tmp_path, tmp_path_factory) == {"first.py"}


def test_non_repository_has_no_git_surface(tmp_path, tmp_path_factory) -> None:
    assert _surface(tmp_path, tmp_path_factory) == set()
