# v1.12 Evidence Index

**Purpose:** 为 `v1.12 Verification Localization & Governance Guard Topicization` 提供机器友好的 `archive-ready / evidence-ready` closeout 入口，集中列出 localized meta-guard truth、`device_refresh` focused suite topology、current-story freeze 与 milestone archive promotion 的正式证据指针。
**Status:** Pull-only archived closeout index (`archive-ready / evidence-ready`)
**Updated:** 2026-03-22

## Pull Contract

- 本文件只索引正式真源、phase verification / summaries、milestone audit 与 archive snapshots；它不是新的 authority source。
- maintainer closeout、下一 milestone 路由与后续审计只能从这里继续 pull 已登记证据，不得重新扫描仓库拼装第二套 verification / governance 故事。
- `.planning/v1.12-MILESTONE-AUDIT.md` 是 `v1.12` 的 verdict home；`.planning/milestones/v1.12-ROADMAP.md` 与 `.planning/milestones/v1.12-REQUIREMENTS.md` 只保留历史快照，不反向定义活跃 current story。
- `59-SUMMARY.md` / `59-VERIFICATION.md` 是 promoted closeout evidence；`59-VALIDATION.md` 维持 execution-trace 身份，不额外升级为长期治理 allowlist。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Public-surface / governance guard topicization | `tests/meta/test_public_surface_guards.py`, `tests/meta/test_governance_phase_history.py`, `tests/meta/test_governance_followup_route.py`, `tests/meta/public_surface_*.py`, `tests/meta/governance_*current_milestones.py`, `59-VERIFICATION.md` | `tests/meta/`, `.planning/phases/59-verification-localization-and-governance-guard-topicization/` | `uv run pytest -q tests/meta/test_public_surface_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_followup_route.py tests/meta/test_dependency_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_version_sync.py` | `59` | megaguards 已退成 thin shell runnable roots，真正断言按 truth family 分散到命名清晰的 topic modules |
| `device_refresh` focused topology | `tests/core/test_device_refresh_parsing.py`, `tests/core/test_device_refresh_filter.py`, `tests/core/test_device_refresh_snapshot.py`, `tests/core/test_device_refresh_runtime.py`, `59-VERIFICATION.md` | `tests/core/`, `.planning/phases/59-verification-localization-and-governance-guard-topicization/` | `uv run pytest -q tests/core/test_device_refresh_parsing.py tests/core/test_device_refresh_filter.py tests/core/test_device_refresh_snapshot.py tests/core/test_device_refresh_runtime.py` | `59` | giant bucket 已退场，focused suites 以 parsing / filter / snapshot / runtime concern boundary 承担日常 proof |
| Current-story / file-governance truth freeze | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`, `.planning/baseline/VERIFICATION_MATRIX.md`, `.planning/codebase/TESTING.md`, `.planning/reviews/{FILE_MATRIX,PROMOTED_PHASE_ASSETS,RESIDUAL_LEDGER,KILL_LIST}.md`, `59-VERIFICATION.md` | `.planning/`, `.planning/baseline/`, `.planning/reviews/` | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_version_sync.py` | `59` | localized verification route、ownership boundary 与 no-growth story 已冻结回 current truth，而不是只存在于 phase prose |
| Milestone closeout / archive promotion | `.planning/v1.12-MILESTONE-AUDIT.md`, `.planning/reviews/V1_12_EVIDENCE_INDEX.md`, `.planning/MILESTONES.md`, `.planning/milestones/v1.12-*.md`, `59-SUMMARY.md`, `59-VERIFICATION.md` | `.planning/`, `.planning/milestones/`, `.planning/reviews/` | `uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_followup_route.py tests/meta/test_version_sync.py` | `59` | archived / evidence-ready promotion completed；`V1_12_EVIDENCE_INDEX.md` 成为 pull-only closeout pointer |

## Release / Closeout Pull Boundary

- 后续 route 仲裁必须从 `.planning/v1.12-MILESTONE-AUDIT.md` 与本索引出发，而不是从 phase 目录重新拼装 closeout 事实。
- `archive-ready / evidence-ready` 判断以 `.planning/v1.12-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- `v1.12` archive snapshots 是历史记录，不取代 `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` / `.planning/STATE.md` 的活跃治理角色。
