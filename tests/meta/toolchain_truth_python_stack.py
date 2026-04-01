"""Python-version and toolchain stack truth guards."""

from __future__ import annotations

import json
from pathlib import Path
import tomllib

import yaml

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))

_PYPROJECT = _ROOT / "pyproject.toml"

_PRE_COMMIT = _ROOT / ".pre-commit-config.yaml"

_DEVCONTAINER = _ROOT / ".devcontainer.json"

_CI_WORKFLOW = _ROOT / ".github" / "workflows" / "ci.yml"

_RELEASE_WORKFLOW = _ROOT / ".github" / "workflows" / "release.yml"

_GOVERNANCE_REGISTRY = _ROOT / ".planning" / "baseline" / "GOVERNANCE_REGISTRY.json"

_SETUP_PYTHON = "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405"



def _load_pyproject():
    return tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))



def _load_yaml(path: Path):
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    if True in loaded and "on" not in loaded:
        loaded["on"] = loaded.pop(True)
    return loaded



def _load_devcontainer():
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
    release = _load_yaml(_RELEASE_WORKFLOW)
    registry = json.loads(_GOVERNANCE_REGISTRY.read_text(encoding="utf-8"))

    assert project["requires-python"] == ">=3.14.2"
    assert mypy["python_version"] == "3.14"
    assert ruff["target-version"] == "py314"
    assert pre_commit["default_language_version"]["python"] == "python3.14"
    assert devcontainer["image"].endswith("python:3.14")
    assert registry["python"]["minimum_version"] == "3.14.2"
    assert registry["python"]["requires_python"] == ">=3.14.2"
    assert registry["install"]["stable_paths"] == ["verified_release_assets"]
    assert registry["install"]["conditional_paths"] == ["HACS"]

    setup_python_versions: list[str] = []
    for workflow in (ci, release):
        jobs = workflow["jobs"]
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
