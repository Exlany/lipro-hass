"""Toolchain truth and local DX contract guards."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tomllib
from typing import Any

import yaml

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_PYPROJECT = _ROOT / "pyproject.toml"
_PRE_COMMIT = _ROOT / ".pre-commit-config.yaml"
_DEVCONTAINER = _ROOT / ".devcontainer.json"
_CI_WORKFLOW = _ROOT / ".github" / "workflows" / "ci.yml"
_DEVELOP_SCRIPT = _ROOT / "scripts" / "develop"
_SETUP_PYTHON = "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405"


def _load_pyproject() -> dict[str, Any]:
    return tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _load_devcontainer() -> dict[str, Any]:
    loaded = json.loads(_DEVCONTAINER.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_python_toolchain_truth_is_aligned_to_314() -> None:
    """pyproject, pre-commit, devcontainer, and CI should tell one Python story."""
    pyproject = _load_pyproject()
    project = pyproject["project"]
    assert isinstance(project, dict)
    mypy = pyproject["tool"]["mypy"]
    assert isinstance(mypy, dict)
    ruff = pyproject["tool"]["ruff"]
    assert isinstance(ruff, dict)
    pre_commit = _load_yaml(_PRE_COMMIT)
    devcontainer = _load_devcontainer()
    ci = _load_yaml(_CI_WORKFLOW)

    assert project["requires-python"] == ">=3.14.2"
    assert mypy["python_version"] == "3.14"
    assert ruff["target-version"] == "py314"
    assert pre_commit["default_language_version"]["python"] == "python3.14"
    assert devcontainer["image"].endswith("python:3.14")

    setup_python_versions: list[str] = []
    jobs = ci["jobs"]
    assert isinstance(jobs, dict)
    for job in jobs.values():
        assert isinstance(job, dict)
        steps = job.get("steps", [])
        assert isinstance(steps, list)
        for step in steps:
            if not isinstance(step, dict) or step.get("uses") != _SETUP_PYTHON:
                continue
            with_block = step.get("with")
            assert isinstance(with_block, dict)
            python_version = with_block.get("python-version")
            assert python_version == "3.14"
            setup_python_versions.append(python_version)

    assert setup_python_versions


def test_pytest_marker_contract_has_no_dead_declarations() -> None:
    """Only live pytest markers should remain declared in pyproject."""
    pyproject = _load_pyproject()
    tool = pyproject["tool"]
    assert isinstance(tool, dict)
    pytest_table = tool["pytest"]
    assert isinstance(pytest_table, dict)
    pytest_options = pytest_table["ini_options"]
    assert isinstance(pytest_options, dict)
    assert "markers" not in pytest_options


def test_develop_script_smoke_mode_preserves_other_integrations(
    tmp_path: Path,
) -> None:
    """The local development entrypoint should only refresh Lipro's integration."""
    fake_repo = tmp_path / "repo"
    scripts_dir = fake_repo / "scripts"
    source_lipro = fake_repo / "custom_components" / "lipro"
    keep_component = fake_repo / "config" / "custom_components" / "keep_me"
    fake_bin = tmp_path / "bin"
    fake_uv = fake_bin / "uv"
    copied_script = scripts_dir / "develop"

    scripts_dir.mkdir(parents=True)
    source_lipro.mkdir(parents=True)
    keep_component.mkdir(parents=True)
    fake_bin.mkdir(parents=True)
    (fake_repo / ".venv").mkdir()

    copied_script.write_text(
        _DEVELOP_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8"
    )
    copied_script.chmod(copied_script.stat().st_mode | stat.S_IXUSR)
    (source_lipro / "manifest.json").write_text(
        '{"domain": "lipro"}',
        encoding="utf-8",
    )
    (keep_component / "sentinel.txt").write_text("keep", encoding="utf-8")
    fake_uv.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    fake_uv.chmod(fake_uv.stat().st_mode | stat.S_IXUSR)

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env['PATH']}"
    env["LIPRO_DEVELOP_SMOKE_ONLY"] = "1"

    bash_executable = shutil.which("bash")
    assert bash_executable is not None

    result = subprocess.run(  # noqa: S603
        [bash_executable, str(copied_script)],
        cwd=fake_repo,
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert (
        fake_repo / "config" / "custom_components" / "keep_me" / "sentinel.txt"
    ).read_text(encoding="utf-8") == "keep"
    assert (
        fake_repo / "config" / "custom_components" / "lipro" / "manifest.json"
    ).exists()
    assert "Preserved other custom integrations" in result.stdout
    assert "Smoke-only mode" in result.stdout
    assert "rm -rf config/custom_components" not in _DEVELOP_SCRIPT.read_text(
        encoding="utf-8"
    )
