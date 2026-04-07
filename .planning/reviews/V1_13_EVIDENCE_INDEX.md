# v1.13 Evidence Index

**Purpose:** 为 `v1.13 Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence` 提供机器友好的 `archived / evidence-ready` closeout 入口，集中索引 tooling truth decomposition、formal-home slimming、naming/discoverability governance 与 milestone archive promotion 的正式证据指针。
**Status:** Pull-only archived closeout index (`archived / evidence-ready`)
**Updated:** 2026-03-22

## Pull Contract

- 本文件只索引正式真源、phase summaries / verifications、milestone audit 与 archive snapshots；它不是新的 authority source。
- 后续 `$gsd-new-milestone`、milestone audit 与 route arbitration 必须从这里继续 pull 已登记证据，不得重新扫描仓库拼装第二套 closeout / governance 故事。
- `.planning/v1.13-MILESTONE-AUDIT.md` 是 `v1.13` 的 verdict home；`.planning/milestones/v1.13-ROADMAP.md` 与 `.planning/milestones/v1.13-REQUIREMENTS.md` 只保留历史快照，不反向定义活跃 current story。
- `60-SUMMARY.md` / `60-VERIFICATION.md`、`61-SUMMARY.md` / `61-VERIFICATION.md`、`62-SUMMARY.md` / `62-VERIFICATION.md` 是 promoted closeout evidence；各 phase 的 `*-VALIDATION.md` 继续维持 execution-trace 身份。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Tooling truth decomposition | `scripts/check_file_matrix.py`, `scripts/check_file_matrix_{inventory,registry,markdown,validation}.py`, `tests/meta/test_toolchain_truth.py`, `tests/meta/toolchain_truth_*.py`, `60-VERIFICATION.md` | `scripts/`, `tests/meta/`, `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/` | `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_governance_guards.py tests/meta/test_dependency_guards.py tests/meta/test_version_sync.py && uv run python scripts/check_file_matrix.py --check` | `60` | checker / guard giant roots 已退成 thin roots + truth-family modules，tooling topology 现可被 closeout-ready baseline 稳定引用 |
| Formal-home slimming | `custom_components/lipro/core/anonymous_share/*`, `custom_components/lipro/services/diagnostics/*`, `custom_components/lipro/core/ota/{candidate.py,candidate_support.py}`, `custom_components/lipro/{select.py,select_internal/gear.py}`, `tests/platforms/test_select_behavior.py`, `61-VERIFICATION.md` | `custom_components/lipro/`, `tests/platforms/`, `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/` | `uv run pytest -q tests/core/anonymous_share/test_manager_recording.py tests/core/anonymous_share/test_manager_submission.py tests/services/test_services_diagnostics.py tests/core/ota/test_ota_candidate.py tests/platforms/test_select_behavior.py tests/platforms/test_select_models.py tests/meta/test_phase61_formal_home_budget_guards.py` | `61` | outward roots 保持稳定，厚重路径只沿 honest collaborator seams inward split |
| Naming / discoverability convergence | `custom_components/lipro/core/device/{extras_support.py,extras_payloads.py,extras_features.py}`, `README.md`, `README_zh.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `docs/README.md`, `tests/meta/test_phase62_naming_discoverability_guards.py`, `62-VERIFICATION.md` | `custom_components/lipro/core/device/`, repo root docs, `.planning/phases/62-naming-clarity-support-seam-governance-and-public-discoverability/` | `uv run pytest -q tests/core/device/test_extras_payloads.py tests/core/device/test_extras_features.py tests/platforms/test_light_model_and_commands.py tests/platforms/test_switch_behavior.py tests/platforms/test_select_models.py tests/meta/test_governance_guards.py tests/meta/test_governance_followup_route.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_phase62_naming_discoverability_guards.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | `62` | 只落地低扇出 rename，并把 public first hop / current-story wording 冻结到同一条命名故事 |
| Milestone closeout / archive promotion | `.planning/v1.13-MILESTONE-AUDIT.md`, `.planning/reviews/V1_13_EVIDENCE_INDEX.md`, `.planning/milestones/v1.13-*.md`, `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`, `60-VERIFICATION.md`, `61-VERIFICATION.md`, `62-VERIFICATION.md` | `.planning/`, `.planning/milestones/`, `.planning/reviews/` | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_followup_route.py tests/meta/test_public_surface_guards.py tests/meta/test_dependency_guards.py tests/meta/test_phase62_naming_discoverability_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | `60-62` | `v1.13` closeout 已完成；后续里程碑必须从 archived evidence 而非 conversation memory 起步 |

## Release / Closeout Pull Boundary

- 后续 route 仲裁必须从 `.planning/v1.13-MILESTONE-AUDIT.md` 与本索引出发，而不是从 phase 目录重新拼装 closeout 事实。
- `archived / evidence-ready` 判断以 `.planning/v1.13-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- `v1.13` archive snapshots 是历史记录，不取代 `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` / `.planning/STATE.md` 的活跃治理角色。
