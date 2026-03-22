"""Release workflow and identity-evidence truth guards."""

from __future__ import annotations

from pathlib import Path

import yaml

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))

_RELEASE_WORKFLOW = _ROOT / ".github" / "workflows" / "release.yml"

_CODEQL_WORKFLOW = _ROOT / ".github" / "workflows" / "codeql.yml"

_README = _ROOT / "README.md"

_README_ZH = _ROOT / "README_zh.md"



def _load_yaml(path: Path):
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    if True in loaded and "on" not in loaded:
        loaded["on"] = loaded.pop(True)
    return loaded



def test_release_workflow_keeps_identity_evidence_tools_in_sync() -> None:
    release = _load_yaml(_RELEASE_WORKFLOW)
    codeql = _load_yaml(_CODEQL_WORKFLOW)

    build_job = release["jobs"]["build"]
    steps = build_job["steps"]
    step_names = {step["name"] for step in steps}

    assert "Generate artifact attestation" in step_names
    assert "Verify generated artifact attestations" in step_names
    assert "Write release identity manifest" in step_names
    assert "Install cosign" in step_names
    assert "Sign release assets" in step_names
    assert "Verify release signatures" in step_names

    codeql_on = codeql["on"]
    assert isinstance(codeql_on, dict)
    assert "workflow_dispatch" in codeql_on
    assert "push" in codeql_on
    assert "v*" in codeql_on["push"]["tags"]
    assert codeql["permissions"]["security-events"] == "write"
    analyze_job = codeql["jobs"]["analyze"]
    analyze_step_names = {step["name"] for step in analyze_job["steps"]}
    assert "Initialize CodeQL" in analyze_step_names
    assert "Perform CodeQL Analysis" in analyze_step_names



def test_release_identity_manifest_keeps_current_trust_stack_explicit() -> None:
    release = _load_yaml(_RELEASE_WORKFLOW)
    build_job = release["jobs"]["build"]
    steps = build_job["steps"]
    assert isinstance(steps, list)

    manifest_step = next(
        step
        for step in steps
        if isinstance(step, dict)
        and step.get("name") == "Write release identity manifest"
    )
    run_block = manifest_step["run"]
    assert isinstance(run_block, str)

    for token in (
        "identity_evidence=SHA256SUMS",
        "identity_evidence=SBOM",
        "identity_evidence=GitHub artifact attestation",
        "identity_evidence=cosign keyless signature bundle",
        "provenance=GitHub artifact attestation",
        "identity_verification=gh attestation verify",
        "signing=cosign keyless sign-blob",
        "signing_verification=cosign verify-blob --bundle",
        "code_scanning=GitHub CodeQL hard gate",
        "code_scanning_verification=tagged ref analysis required + zero open alerts",
    ):
        assert token in run_block



def test_bilingual_readmes_capture_release_asset_identity_truth() -> None:
    readme_text = _README.read_text(encoding="utf-8")
    readme_zh_text = _README_ZH.read_text(encoding="utf-8")

    for text in (readme_text, readme_zh_text):
        for token in (
            "SHA256SUMS",
            "SBOM",
            "attestation",
            "provenance",
            "cosign",
            "CodeQL",
        ):
            assert token in text

    assert "Contributor Fast Path" in readme_text
    assert "docs/README.md" in readme_text
    assert "贡献快速路径" in readme_zh_text
    assert "docs/README.md" in readme_zh_text
    assert "single-maintainer model" not in readme_text
    assert "单维护者模型" not in readme_zh_text
