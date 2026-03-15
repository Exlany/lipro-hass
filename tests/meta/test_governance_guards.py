"""Governance guards for file-matrix coverage and architecture-policy hygiene."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import yaml

from scripts.check_architecture_policy import (
    run_checks as run_architecture_policy_checks,
)
from scripts.check_file_matrix import (
    extract_reported_total,
    iter_python_files,
    parse_file_matrix_paths,
    repo_root,
    run_checks,
)
from tests.helpers.architecture_policy import load_structural_rules, load_targeted_bans

_ROOT = repo_root(Path(__file__))
_FILE_MATRIX = _ROOT / ".planning" / "reviews" / "FILE_MATRIX.md"
_DOCS_README = _ROOT / "docs" / "README.md"
_README = _ROOT / "README.md"
_README_ZH = _ROOT / "README_zh.md"
_AGENTS = _ROOT / "AGENTS.md"
_CONTRIBUTING = _ROOT / "CONTRIBUTING.md"
_SUPPORT = _ROOT / "SUPPORT.md"
_SECURITY = _ROOT / "SECURITY.md"
_CODE_OF_CONDUCT = _ROOT / "CODE_OF_CONDUCT.md"
_CODEOWNERS = _ROOT / ".github" / "CODEOWNERS"
_MANIFEST = _ROOT / "custom_components" / "lipro" / "manifest.json"
_QUALITY_SCALE = _ROOT / "custom_components" / "lipro" / "quality_scale.yaml"
_DEVCONTAINER = _ROOT / ".devcontainer.json"
_PR_TEMPLATE = _ROOT / ".github" / "pull_request_template.md"
_CI_WORKFLOW = _ROOT / ".github" / "workflows" / "ci.yml"
_RELEASE_WORKFLOW = _ROOT / ".github" / "workflows" / "release.yml"
_ISSUE_CONFIG = _ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml"


def test_file_matrix_covers_workspace_python_inventory() -> None:
    inventory = iter_python_files(_ROOT)
    matrix_text = _FILE_MATRIX.read_text(encoding="utf-8")

    assert extract_reported_total(matrix_text) == len(inventory)
    assert parse_file_matrix_paths(matrix_text) == inventory


def _load_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(?P<frontmatter>.*?)\n---\n", text, flags=re.DOTALL)
    assert match is not None
    loaded = yaml.safe_load(match.group("frontmatter"))
    assert isinstance(loaded, dict)
    return loaded


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    if True in loaded and "on" not in loaded:
        loaded["on"] = loaded.pop(True)
    return loaded


def _load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _extract_markdown_section(text: str, heading_fragment: str) -> str:
    match = re.search(
        rf"^#{{2,}} [^\n]*{re.escape(heading_fragment)}[^\n]*\n(?P<body>.*?)(?=^#{{2,}} |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match, f"Missing section containing heading: {heading_fragment}"
    return match.group("body")


def _extract_labeled_bullets(section_text: str) -> dict[str, str]:
    bullets: dict[str, str] = {}
    for line in section_text.splitlines():
        match = re.match(r"- \*\*(?P<label>[^*]+)\*\*[:：]\s*(?P<body>.+)", line.strip())
        if match:
            bullets[match.group("label").strip()] = match.group("body").strip()
    return bullets


def _extract_checklist_labels(text: str) -> dict[str, str]:
    items: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"- \[ \] `(?P<label>[^`]+)`:\s*(?P<body>.+)", line.strip())
        if match:
            items[match.group("label").strip()] = match.group("body").strip()
    return items


def _count_numbered_markdown_items(section_text: str) -> int:
    return len(re.findall(r"^\d+\. ", section_text, flags=re.MULTILINE))


def _parse_codeowners_handles(text: str) -> list[str]:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("* "):
            return stripped.split()[1:]
    raise AssertionError("Missing wildcard CODEOWNERS entry")


def _assert_current_mode_tracks_phase_lifecycle(state_text: str) -> None:
    assert re.search(
        r"\*\*Current mode:\*\* `Phase \d+(?:\.\d+)? [a-z][a-z0-9_ -]+`",
        state_text,
    )


def test_governance_checker_reports_no_drift() -> None:
    assert run_checks(_ROOT) == []



def test_architecture_policy_checker_reports_no_drift() -> None:
    assert run_architecture_policy_checks(_ROOT) == []



def test_architecture_policy_rule_inventory_is_stable() -> None:
    assert set(load_structural_rules(_ROOT)) == {
        "ENF-IMP-ENTITY-PROTOCOL-INTERNALS",
        "ENF-IMP-CONTROL-NO-BYPASS",
        "ENF-IMP-BOUNDARY-LOCALITY",
        "ENF-GOV-DEPENDENCY-POLICY-REF",
        "ENF-GOV-PUBLIC-SURFACE-POLICY-REF",
        "ENF-GOV-AUTHORITY-POLICY-REF",
        "ENF-GOV-VERIFICATION-POLICY-REF",
        "ENF-GOV-CI-FAIL-FAST",
        "ENF-GOV-RELEASE-CI-REUSE",
        "ENF-IMP-API-LEGACY-SPINE-LOCALITY",
        "ENF-IMP-MQTT-TRANSPORT-LOCALITY",
        "ENF-IMP-ASSURANCE-NO-PRODUCTION-BACKFLOW",
    }
    assert set(load_targeted_bans(_ROOT)) == {
        "ENF-SURFACE-COORDINATOR-ENTRY",
        "ENF-SURFACE-API-EXPORTS",
        "ENF-SURFACE-PROTOCOL-EXPORTS",
        "ENF-BACKDOOR-COORDINATOR-PROPERTIES",
        "ENF-BACKDOOR-SERVICE-AUTH",
        "ENF-COMPAT-ROOT-NO-LEGACY-CLIENT",
        "ENF-COMPAT-CONFIG-FLOW-NO-LEGACY-CLIENT",
        "ENF-COMPAT-CORE-PACKAGE-NO-LEGACY-CLIENTS",
        "ENF-COMPAT-MQTT-PACKAGE-NO-LEGACY-CLIENT",
    }


def test_phase_asset_identity_is_documented_consistently() -> None:
    docs_bullets = _extract_labeled_bullets(
        _extract_markdown_section(
            _DOCS_README.read_text(encoding="utf-8"),
            "Phase 资产身份与开源治理",
        )
    )
    agents_bullets = _extract_labeled_bullets(
        _extract_markdown_section(
            _AGENTS.read_text(encoding="utf-8"),
            "Phase 资产身份与开源治理",
        )
    )

    for bullets in (docs_bullets, agents_bullets):
        assert {"默认身份", "提升条件", "发布门禁", "对外入口"} <= set(bullets)
        assert ".planning/phases/**" in bullets["默认身份"]
        assert ".planning/ROADMAP.md" in bullets["提升条件"]
        assert ".planning/baseline/VERIFICATION_MATRIX.md" in bullets["提升条件"]
        assert ".github/workflows/ci.yml" in bullets["发布门禁"]
        assert ".github/workflows/release.yml" in bullets["发布门禁"]
        assert "CONTRIBUTING.md" in bullets["对外入口"]
        assert "SECURITY.md" in bullets["对外入口"]


def test_ci_and_release_workflows_share_governance_and_version_gates() -> None:
    ci_workflow = _load_yaml(_CI_WORKFLOW)
    release_workflow = _load_yaml(_RELEASE_WORKFLOW)

    assert "workflow_call" in ci_workflow["on"]

    governance_steps = ci_workflow["jobs"]["governance"]["steps"]
    governance_runs = "\n".join(step.get("run", "") for step in governance_steps)
    assert "tests/meta/test_governance_guards.py" in governance_runs
    assert "tests/meta/test_version_sync.py" in governance_runs

    validate_job = release_workflow["jobs"]["validate"]
    assert validate_job["uses"] == "./.github/workflows/ci.yml"
    assert validate_job["secrets"] == "inherit"

    build_job = release_workflow["jobs"]["build"]
    assert build_job["needs"] == "validate"
    step_names = {step["name"] for step in build_job["steps"]}
    assert "Verify tag matches project version" in step_names
    version_guard = next(
        step["run"]
        for step in build_job["steps"]
        if step.get("name") == "Verify tag matches project version"
    )
    assert "pyproject.toml" in version_guard
    assert "RELEASE_TAG" in version_guard


def test_contributor_contract_matches_ci_language() -> None:
    contributing_bullets = _extract_labeled_bullets(
        _extract_markdown_section(
            _CONTRIBUTING.read_text(encoding="utf-8"),
            "CI Contract / CI 契约",
        )
    )
    pr_checklist = _extract_checklist_labels(_PR_TEMPLATE.read_text(encoding="utf-8"))

    assert {"lint", "governance", "test", "benchmark", "validate", "release"} <= set(
        contributing_bullets
    )
    assert {"lint", "governance", "test", "benchmark"} <= set(pr_checklist)
    assert "tests/meta/test_governance_guards.py" in contributing_bullets["governance"]
    assert "tests/meta/test_version_sync.py" in contributing_bullets["governance"]
    assert "--ignore=tests/benchmarks" in contributing_bullets["test"]
    assert "tests/benchmarks/" in contributing_bullets["benchmark"]


def test_security_disclosure_path_is_present() -> None:
    security_text = _SECURITY.read_text(encoding="utf-8")
    issue_config = _load_yaml(_ISSUE_CONFIG)
    contact_urls = {link["url"] for link in issue_config["contact_links"]}

    assert "/security/advisories/new" in security_text
    assert "public GitHub issue" in security_text
    assert "https://github.com/Exlany/lipro-hass/security/policy" in contact_urls



def test_v1_1_closeout_assets_exist_and_are_pull_only() -> None:
    evidence_index = _ROOT / ".planning" / "reviews" / "V1_1_EVIDENCE_INDEX.md"
    phase_summary = _ROOT / ".planning" / "phases" / "07.5-integration-governance-verification-closeout" / "07.5-SUMMARY.md"
    plan_01_summary = _ROOT / ".planning" / "phases" / "07.5-integration-governance-verification-closeout" / "07.5-01-SUMMARY.md"
    plan_02_summary = _ROOT / ".planning" / "phases" / "07.5-integration-governance-verification-closeout" / "07.5-02-SUMMARY.md"
    verification = _ROOT / ".planning" / "phases" / "07.5-integration-governance-verification-closeout" / "07.5-VERIFICATION.md"

    assert evidence_index.exists()
    assert phase_summary.exists()
    assert plan_01_summary.exists()
    assert plan_02_summary.exists()
    assert verification.exists()

    evidence_text = evidence_index.read_text(encoding="utf-8")
    assert "## Pull Contract" in evidence_text
    assert "07.3-runtime-telemetry-exporter" in evidence_text
    assert "07.4-protocol-replay-simulator-harness" in evidence_text
    assert "Phase 8 Pull Boundary" in evidence_text



def test_governance_truth_registers_v1_1_closeout_assets() -> None:
    authority_text = (_ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md").read_text(encoding="utf-8")
    verification_text = (_ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(encoding="utf-8")

    assert "runtime telemetry exporter family" in authority_text
    assert "v1.1 closeout evidence index" in authority_text
    assert "| 7.5 |" in verification_text
    assert "V1_1_EVIDENCE_INDEX.md" in verification_text
    assert "## Phase 07.5 Residual Delta" in residual_text
    assert "de-scope" in residual_text
    assert "## Phase 07.5 Status Update" in kill_text



def test_phase_7_5_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    validation_text = (_ROOT / ".planning" / "phases" / "07.5-integration-governance-verification-closeout" / "07.5-VALIDATION.md").read_text(encoding="utf-8")

    assert "| 7.5 Governance & Verification | v1.1 | 2/2 | Complete | 2026-03-13 |" in roadmap_text
    assert "| GOV-06 | Phase 7.5 | Complete |" in requirements_text
    assert "| GOV-07 | Phase 7.5 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "status: passed" in validation_text
    assert "- [x] `.planning/reviews/V1_1_EVIDENCE_INDEX.md`" in validation_text
    assert "- [x] All tasks have automated verify or Wave 0 dependencies" in validation_text



def test_phase_8_planning_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    validation_text = (_ROOT / ".planning" / "phases" / "08-ai-debug-evidence-pack" / "08-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (_ROOT / ".planning" / "phases" / "08-ai-debug-evidence-pack" / "08-VERIFICATION.md").read_text(encoding="utf-8")

    assert "| 8 AI Debug Evidence Pack | v1.1 | 2/2 | Complete | 2026-03-13 |" in roadmap_text
    assert "| AID-01 | Phase 8 | Complete |" in requirements_text
    assert "| AID-02 | Phase 8 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "status: passed" in validation_text
    assert "nyquist_compliant: true" in validation_text
    assert "wave_0_complete: true" in validation_text
    assert "status: passed" in verification_text



def test_phase_9_governance_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    validation_text = (_ROOT / ".planning" / "phases" / "09-residual-surface-closure" / "09-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (_ROOT / ".planning" / "phases" / "09-residual-surface-closure" / "09-VERIFICATION.md").read_text(encoding="utf-8")
    uat_text = (_ROOT / ".planning" / "phases" / "09-residual-surface-closure" / "09-UAT.md").read_text(encoding="utf-8")
    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(encoding="utf-8")
    authority_text = (_ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(encoding="utf-8")

    assert '- [x] 09-01: 收窄 protocol root surface 与 compat exports' in roadmap_text
    assert '| RSC-01 | Phase 9 | Complete |' in requirements_text
    assert '| RSC-04 | Phase 9 | Complete |' in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert 'status: passed' in validation_text
    assert 'status: passed' in verification_text
    assert '## Automated UAT Verdict' in uat_text
    assert 'services/wiring.py' not in public_text
    assert 'runtime supplemental state primitives' in authority_text
    assert residual_text.count('## Phase 09 Residual Delta') == 1
    assert kill_text.count('## Phase 09 Status Update') == 1
    for seam in (
        'core.api.LiproClient',
        'LiproProtocolFacade.get_device_list',
        'LiproMqttFacade.raw_client',
    ):
        assert seam in residual_text
        assert seam in kill_text



def test_phase_11_execution_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(encoding="utf-8")
    research_text = (_ROOT / ".planning" / "phases" / "11-control-router-formalization-wiring-residual-demotion" / "11-RESEARCH.md").read_text(encoding="utf-8")
    audit_frontmatter = _load_frontmatter(_ROOT / ".planning" / "v1.1-MILESTONE-AUDIT.md")

    assert "| 11 Control Router Formalization & Wiring Residual Demotion | v1.1 | 8/8 | Complete | 2026-03-14 |" in roadmap_text
    assert "| SURF-01 | Phase 11 | Complete |" in requirements_text
    assert "| CTRL-04 | Phase 11 | Complete |" in requirements_text
    assert "| RUN-01 | Phase 11 | Complete |" in requirements_text
    assert "| ENT-01 | Phase 11 | Complete |" in requirements_text
    assert "| ENT-02 | Phase 11 | Complete |" in requirements_text
    assert "| GOV-08 | Phase 11 | Complete |" in requirements_text
    assert "services/wiring.py" not in public_text
    assert "custom_components/lipro/services/wiring.py" not in file_matrix_text
    assert "11-04 ~ 11-08 addendum plans" in research_text
    assert audit_frontmatter["status"] == "superseded_snapshot"
    assert audit_frontmatter["snapshot_scope"] == "phase_11_complete_pre_closeout"
    scores = audit_frontmatter["scores"]
    assert isinstance(scores, dict)
    assert scores["requirements"] == "30/30"


def test_readme_exposes_community_and_governance_entrypoints() -> None:
    for readme_path in (_README, _README_ZH):
        readme_text = readme_path.read_text(encoding="utf-8")
        for asset in (
            "CONTRIBUTING.md",
            "SUPPORT.md",
            "SECURITY.md",
            "CODE_OF_CONDUCT.md",
            "custom_components/lipro/quality_scale.yaml",
            ".devcontainer.json",
        ):
            assert asset in readme_text


def test_manifest_codeowners_match_repo_codeowners() -> None:
    manifest = _load_json(_MANIFEST)
    assert manifest.get("codeowners") == _parse_codeowners_handles(
        _CODEOWNERS.read_text(encoding="utf-8")
    )


def test_support_and_issue_routing_are_consistent() -> None:
    support_text = _SUPPORT.read_text(encoding="utf-8")
    contributing_text = _CONTRIBUTING.read_text(encoding="utf-8")
    issue_config = _load_yaml(_ISSUE_CONFIG)
    contact_urls = [link["url"] for link in issue_config.get("contact_links", [])]

    assert "SUPPORT.md" in contributing_text
    assert "SECURITY.md" in contributing_text
    assert any("discussions" in url.lower() for url in contact_urls)
    assert any("security/policy" in url.lower() for url in contact_urls)
    assert "Discussion" in support_text or "讨论" in support_text
    assert "SECURITY.md" in support_text


def test_quality_scale_and_devcontainer_truth_are_in_sync() -> None:
    quality_scale = _load_yaml(_QUALITY_SCALE)
    known_limitations_comment = quality_scale["rules"]["docs-known-limitations"]["comment"]
    match = re.search(r"(\d+) known limitations", known_limitations_comment)
    assert match is not None
    expected_known_limitations = int(match.group(1))

    readme_section = _extract_markdown_section(
        _README.read_text(encoding="utf-8"),
        "Known Limitations",
    )
    assert _count_numbered_markdown_items(readme_section) == expected_known_limitations
    assert "tests/flows/test_config_flow.py" in quality_scale["rules"]["config-flow-test-coverage"]["comment"]
    assert (_ROOT / "tests" / "flows" / "test_config_flow.py").exists()

    devcontainer = _load_json(_DEVCONTAINER)
    settings = devcontainer["customizations"]["vscode"]["settings"]
    assert settings["python.defaultInterpreterPath"].endswith("/.venv/bin/python")




def test_phase_14_execution_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "14-legacy-stack-final-closure-api-spine-demolition-governance-truth-consolidation"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(encoding="utf-8")
    architecture_policy_text = (_ROOT / ".planning" / "baseline" / "ARCHITECTURE_POLICY.md").read_text(encoding="utf-8")
    verification_matrix_text = (_ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(encoding="utf-8")
    structure_text = (_ROOT / ".planning" / "codebase" / "STRUCTURE.md").read_text(encoding="utf-8")
    research_text = (phase_root / "14-RESEARCH.md").read_text(encoding="utf-8")
    prd_text = (phase_root / "14-PRD.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "14-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "14-VERIFICATION.md").read_text(encoding="utf-8")

    assert "### 9. Phase 14 旧 API Spine 终局收口与治理真源归一已完成" in project_text
    assert (
        "| 14 Legacy Stack Final Closure, API Spine Demolition & Governance Truth Consolidation | v1.1 | 4/4 | Complete | 2026-03-15 |"
        in roadmap_text
    )
    assert "**Requirements**: RUN-04, HOT-02, CTRL-05, RUN-05, GOV-12" in roadmap_text
    assert "| RUN-04 | Phase 14 | Complete |" in requirements_text
    assert "| GOV-12 | Phase 14 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "CoordinatorProtocolService" in prd_text
    assert "4 plans / 3 waves" in research_text
    assert "status: passed" in validation_text
    assert "status: passed" in verification_text
    assert "## Phase 14 Surface Closure Notes" in public_text
    assert "## Phase 14 Exit Contract" in verification_matrix_text
    assert "## Phase 14 Residual Delta" in residual_text
    assert "## Phase 14 Status Update" in kill_text
    assert "ENF-IMP-API-LEGACY-SPINE-LOCALITY" in architecture_policy_text
    assert "ENF-GOV-RELEASE-CI-REUSE" in architecture_policy_text
    assert "custom_components/lipro/control/developer_router_support.py" in file_matrix_text
    assert "custom_components/lipro/core/api/status_fallback.py" in file_matrix_text
    assert "custom_components/lipro/core/coordinator/services/protocol_service.py" in file_matrix_text
    assert "client.py              # compat shell" not in structure_text
    assert "LiproMqttClient compat shell" not in public_text

    for artifact_name in (
        "14-01-PLAN.md",
        "14-02-PLAN.md",
        "14-03-PLAN.md",
        "14-04-PLAN.md",
        "14-01-SUMMARY.md",
        "14-02-SUMMARY.md",
        "14-03-SUMMARY.md",
        "14-04-SUMMARY.md",
        "14-VALIDATION.md",
        "14-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()

def test_phase_13_execution_truth_is_consistent() -> None:
    phase_root = (
        _ROOT
        / ".planning"
        / "phases"
        / "13-explicit-domain-surface-governance-guard-hardening-hotspot-boundary-decomposition"
    )
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(encoding="utf-8")
    file_matrix_text = (_ROOT / ".planning" / "reviews" / "FILE_MATRIX.md").read_text(encoding="utf-8")
    research_text = (phase_root / "13-RESEARCH.md").read_text(encoding="utf-8")
    prd_text = (phase_root / "13-PRD.md").read_text(encoding="utf-8")
    validation_text = (phase_root / "13-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (phase_root / "13-VERIFICATION.md").read_text(encoding="utf-8")

    assert "### 8. Phase 13 显式领域表面 / 治理守卫 / 热点边界收口已完成" in project_text
    assert (
        "| 13 Explicit Domain Surface, Governance Guard Hardening & Hotspot Boundary Decomposition | v1.1 | 3/3 | Complete | 2026-03-14 |"
        in roadmap_text
    )
    assert "| DOM-01 | Phase 13 | Complete |" in requirements_text
    assert "| GOV-11 | Phase 13 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "`__getattr__`" in prd_text
    assert "3 plans / 2 waves" in research_text
    assert "status: passed" in validation_text
    assert "status: passed" in verification_text
    assert "device_delegation.py" not in file_matrix_text
    assert "Domain dynamic delegation" in residual_text
    assert "## Phase 13 Residual Delta" in residual_text
    assert "## Phase 13 Status Update" in kill_text
    assert "## Phase 13 Surface Closure Notes" in public_text


def test_phase_12_execution_truth_is_consistent() -> None:
    phase_root = _ROOT / ".planning" / "phases" / "12-type-contract-alignment-residual-cleanup-and-governance-hygiene"
    project_text = (_ROOT / ".planning" / "PROJECT.md").read_text(encoding="utf-8")
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(encoding="utf-8")
    research_text = (phase_root / "12-RESEARCH.md").read_text(encoding="utf-8")
    prd_text = (phase_root / "12-PRD.md").read_text(encoding="utf-8")

    assert "**Status:** Active" in project_text
    assert "### 7. Phase 12 Type / Residual / Governance 收口已完成" in project_text
    assert "| 12 Type Contract Alignment, Residual Cleanup & Governance Hygiene | v1.1 | 5/5 | Complete | 2026-03-14 |" in roadmap_text
    assert "**Requirements**: TYP-01, TYP-02, CMP-01, CMP-02, HOT-01, GOV-09, GOV-10" in roadmap_text
    assert "| TYP-01 | Phase 12 | Complete |" in requirements_text
    assert "| GOV-10 | Phase 12 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "Already Fixed / Must Not Be Replanned" in prd_text
    assert "5 plans / 3 waves" in research_text
    active_residual_text = _extract_markdown_section(residual_text, "Active Residual Families")
    assert "## Phase 12 Surface Closure Notes" in public_text
    assert "## Phase 12 Residual Delta" in residual_text
    assert "## Phase 12 Status Update" in kill_text
    assert '`core.api.LiproClient` compat shell 已删除' in public_text
    assert '`LiproProtocolFacade.get_device_list` compat wrapper 已删除' in public_text
    assert '`LiproMqttFacade.raw_client` compat seam 已删除' in public_text
    assert '`DeviceCapabilities` compat alias' in public_text
    assert '已关闭（Phase 12：compat shell removed）' in kill_text
    assert '已关闭（Phase 12：compat seam removed）' in kill_text
    assert '已关闭（Phase 12：compat alias removed）' in kill_text
    for seam in (
        'core.api.LiproClient',
        'LiproProtocolFacade.get_device_list',
        'LiproMqttFacade.raw_client',
        'DeviceCapabilities',
    ):
        assert seam in public_text
        assert seam in kill_text
        assert seam not in active_residual_text
    for artifact_name in (
        "12-01-PLAN.md",
        "12-02-PLAN.md",
        "12-03-PLAN.md",
        "12-04-PLAN.md",
        "12-05-PLAN.md",
        "12-01-SUMMARY.md",
        "12-02-SUMMARY.md",
        "12-03-SUMMARY.md",
        "12-04-SUMMARY.md",
        "12-05-SUMMARY.md",
        "12-VALIDATION.md",
        "12-VERIFICATION.md",
    ):
        assert (phase_root / artifact_name).exists()


def test_phase_10_governance_truth_is_consistent() -> None:
    roadmap_text = (_ROOT / ".planning" / "ROADMAP.md").read_text(encoding="utf-8")
    requirements_text = (_ROOT / ".planning" / "REQUIREMENTS.md").read_text(encoding="utf-8")
    state_text = (_ROOT / ".planning" / "STATE.md").read_text(encoding="utf-8")
    validation_text = (_ROOT / ".planning" / "phases" / "10-api-drift-isolation-core-boundary-prep" / "10-VALIDATION.md").read_text(encoding="utf-8")
    verification_text = (_ROOT / ".planning" / "phases" / "10-api-drift-isolation-core-boundary-prep" / "10-VERIFICATION.md").read_text(encoding="utf-8")
    uat_text = (_ROOT / ".planning" / "phases" / "10-api-drift-isolation-core-boundary-prep" / "10-UAT.md").read_text(encoding="utf-8")
    public_text = (_ROOT / ".planning" / "baseline" / "PUBLIC_SURFACES.md").read_text(encoding="utf-8")
    dependency_text = (_ROOT / ".planning" / "baseline" / "DEPENDENCY_MATRIX.md").read_text(encoding="utf-8")
    authority_text = (_ROOT / ".planning" / "baseline" / "AUTHORITY_MATRIX.md").read_text(encoding="utf-8")
    verification_matrix_text = (_ROOT / ".planning" / "baseline" / "VERIFICATION_MATRIX.md").read_text(encoding="utf-8")
    residual_text = (_ROOT / ".planning" / "reviews" / "RESIDUAL_LEDGER.md").read_text(encoding="utf-8")
    kill_text = (_ROOT / ".planning" / "reviews" / "KILL_LIST.md").read_text(encoding="utf-8")

    for summary_name in (
        "10-01-SUMMARY.md",
        "10-02-SUMMARY.md",
        "10-03-SUMMARY.md",
        "10-04-SUMMARY.md",
    ):
        assert (_ROOT / ".planning" / "phases" / "10-api-drift-isolation-core-boundary-prep" / summary_name).exists()

    assert "| 10 API Drift Isolation & Core Boundary Prep | v1.1 | 4/4 | Complete | 2026-03-14 |" in roadmap_text
    assert "| ISO-01 | Phase 10 | Complete |" in requirements_text
    assert "| ISO-04 | Phase 10 | Complete |" in requirements_text
    _assert_current_mode_tracks_phase_lifecycle(state_text)
    assert "status: passed" in validation_text
    assert "tests/meta/test_governance_guards.py" in validation_text
    assert "status: passed" in verification_text
    assert "AuthSessionSnapshot" in verification_text
    assert "## Automated UAT Verdict" in uat_text
    assert "4/4 通过" in uat_text
    assert "AuthSessionSnapshot" in public_text
    assert "`Coordinator` 不再从这里导出" in public_text
    assert "runtime_access.get_entry_runtime_coordinator()" in public_text
    assert "entry.runtime_data.coordinator" in dependency_text
    assert "rest.device-list@v1" in authority_text
    assert "rest.device-status@v1" in authority_text
    assert "rest.mesh-group-status@v1" in authority_text
    assert "AuthSessionSnapshot" in authority_text
    assert "| `ISO-*` |" in verification_matrix_text
    assert "## Phase 10 Exit Contract" in verification_matrix_text
    assert residual_text.count("## Phase 10 Residual Delta") == 1
    assert kill_text.count("## Phase 10 Status Update") == 1
    for seam in (
        "core.api.LiproClient",
        "LiproProtocolFacade.get_device_list",
        "LiproMqttFacade.raw_client",
    ):
        assert seam in residual_text
        assert seam in kill_text
