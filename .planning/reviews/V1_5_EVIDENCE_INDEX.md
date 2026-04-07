# v1.5 Evidence Index

**Purpose:** 为 `v1.5 Governance Truth Consolidation & Control-Surface Finalization` 提供机器友好的 shipped / archived closeout 入口，集中列出 governance truth、registry-backed release/support/install story、runtime-access read-model convergence 与 shared service execution contract 的正式证据指针。
**Status:** Pull-only shipped archive index
**Updated:** 2026-03-19

## Pull Contract

- 本文件只索引正式真源、phase verification/summaries、milestone audit 与 archive snapshots；它不是新的 authority source。
- maintainer release flow、下一里程碑启动与后续审计只能从这里继续 pull 已登记证据，不得重新扫描仓库拼装第二套事实。
- `.planning/v1.5-MILESTONE-AUDIT.md` 是 `v1.5` 的 verdict home；`.planning/milestones/v1.5-ROADMAP.md` 与 `.planning/milestones/v1.5-REQUIREMENTS.md` 只保留历史快照，不反向定义活跃治理真相。
- `40-SUMMARY.md` 与 `40-VERIFICATION.md` 是 promoted closeout evidence；`40-VALIDATION.md` 维持 execution-trace 身份，不额外升级为长期治理 allowlist。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Governance truth / archive identity | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`, `docs/README.md`, `40-VERIFICATION.md` | `.planning/`, `docs/`, `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/` | `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` | `40` | active truth, archive evidence, promoted phase assets, and continuity order share one current-story contract |
| Registry-backed release / support / install truth | `.planning/baseline/GOVERNANCE_REGISTRY.json`, `README*.md`, `SUPPORT.md`, `SECURITY.md`, `docs/TROUBLESHOOTING.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/bug.yml` | `.planning/baseline/`, repo root docs, `.github/` | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` | `40` | `latest` install default, `SHA256SUMS` / `SBOM` / `provenance` / `signing` / `code scanning` posture, break-glass verify-only, and non-publish rehearsal remain one guarded story; `firmware manifest metadata` stays explicitly deferred |
| Runtime access read-model convergence | `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/control/diagnostics_surface.py`, `custom_components/lipro/services/{device_lookup,maintenance}.py`, `40-VERIFICATION.md` | `custom_components/lipro/control/`, `custom_components/lipro/services/` | `uv run pytest -q tests/core/test_control_plane.py tests/core/test_diagnostics.py tests/services/test_device_lookup.py tests/services/test_maintenance.py` | `40` | control/services consumers no longer maintain parallel runtime traversal or device-lookup stories |
| Shared service execution contract | `custom_components/lipro/services/execution.py`, `custom_components/lipro/services/schedule.py`, `40-VERIFICATION.md` | `custom_components/lipro/services/` | `uv run pytest -q tests/services/test_execution.py tests/services/test_services_schedule.py` | `40` | schedule services reuse the formal shared auth/error executor and keep one translated error taxonomy |
| Milestone closeout / archive promotion | `.planning/v1.5-MILESTONE-AUDIT.md`, `.planning/MILESTONES.md`, `.planning/milestones/v1.5-*.md`, `40-SUMMARY.md`, `40-VERIFICATION.md` | `.planning/`, `.planning/milestones/`, `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/` | `uv run ruff check . && uv run mypy && uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance*.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` | `40` | shipped / archived promotion completed; `V1_5_EVIDENCE_INDEX.md` is the latest pull-only closeout pointer |

## Release / Closeout Pull Boundary

- Maintainer release issues must start from `docs/MAINTAINER_RELEASE_RUNBOOK.md` and this index, not from ad-hoc file hunting.
- `archive-ready / shipped` 判断以 `.planning/v1.5-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- `v1.5` archive snapshots 是历史记录，不取代 `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` / `.planning/STATE.md` 的活跃治理角色。
