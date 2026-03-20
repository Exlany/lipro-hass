# v1.6 Evidence Index

**Purpose:** 为 `v1.6 Delivery Trust Hardening, Runtime Boundary Decoupling & Maintainability Closure` 提供机器友好的 `archive-ready / shipped` closeout 入口，集中列出 delivery trust hardening、typed runtime read-model、governance identity convergence、hotspot typed-failure semantics 与 milestone archive promotion 的正式证据指针。
**Status:** Pull-only archived closeout index (`archive-ready / shipped`)
**Updated:** 2026-03-20

## Pull Contract

- 本文件只索引正式真源、phase verification / summaries、milestone audit 与 archive snapshots；它不是新的 authority source。
- maintainer release flow、下一里程碑启动与后续审计只能从这里继续 pull 已登记证据，不得重新扫描仓库拼装第二套事实。
- `.planning/v1.6-MILESTONE-AUDIT.md` 是 `v1.6` 的 verdict home；`.planning/milestones/v1.6-ROADMAP.md` 与 `.planning/milestones/v1.6-REQUIREMENTS.md` 只保留历史快照，不反向定义活跃治理真相。
- `42-SUMMARY.md` / `42-VERIFICATION.md`、`43-SUMMARY.md` / `43-VERIFICATION.md`、`44-SUMMARY.md` / `44-VERIFICATION.md`、`45-SUMMARY.md` / `45-VERIFICATION.md` 是 promoted closeout evidence；`V1_6_EVIDENCE_INDEX.md` 是当前最新的 pull-only closeout pointer。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Delivery trust / release hardening | `.github/workflows/{ci,release}.yml`, `SUPPORT.md`, `SECURITY.md`, `CONTRIBUTING.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `42-VERIFICATION.md` | `.github/workflows/`, repo root docs, `docs/`, `.planning/phases/42-delivery-trust-gates-and-validation-hardening/` | `uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` | `42` | continuity truth、artifact install smoke、dual coverage gate 与 compatibility preview lane 讲同一条 guarded story |
| Control / runtime / service boundary | `custom_components/lipro/control/runtime_access.py`, `custom_components/lipro/control/service_router_support.py`, `custom_components/lipro/runtime_infra.py`, `43-VERIFICATION.md` | `custom_components/lipro/control/`, `custom_components/lipro/services/`, `custom_components/lipro/` | `uv run pytest -q tests/core/test_control_plane.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/services/test_device_lookup.py tests/services/test_maintenance.py` | `43` | `RuntimeAccess` typed read-model、control-owned bridge 与 runtime infra ownership 不再分裂成第二条 boundary story |
| Governance identity / terminology / contributor routing | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`, `.planning/reviews/PROMOTED_PHASE_ASSETS.md`, `README*.md`, `docs/README.md`, `44-VERIFICATION.md` | `.planning/`, repo root docs, `docs/`, `.planning/phases/44-governance-asset-pruning-and-terminology-convergence/` | `uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_phase_history_runtime.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py` | `44` | execution-trace boundary、façade-era terminology 与 contributor fast-path / bilingual boundary 已收口成低噪声 current story |
| Hotspot decomposition / typed failure / benchmark no-regression | `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py`, `custom_components/lipro/core/api/diagnostics_api_service.py`, `custom_components/lipro/core/anonymous_share/share_client.py`, `custom_components/lipro/core/mqtt/message_processor.py`, `tests/benchmarks/benchmark_baselines.json`, `45-VERIFICATION.md` | `custom_components/lipro/core/`, `custom_components/lipro/services/`, `tests/benchmarks/`, `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/` | `uv run python scripts/check_benchmark_baseline.py .benchmarks/_all_shape.json --manifest tests/benchmarks/benchmark_baselines.json && uv run pytest -q tests/meta/test_phase45_hotspot_budget_guards.py tests/meta/test_governance_release_contract.py tests/meta/test_toolchain_truth.py` | `45` | typed result / reason-code semantics 与 benchmark baseline compare 成为可审计 anti-regression truth |
| Milestone closeout / archive promotion | `.planning/v1.6-MILESTONE-AUDIT.md`, `.planning/MILESTONES.md`, `.planning/milestones/v1.6-*.md`, `42-VERIFICATION.md`, `43-VERIFICATION.md`, `44-VERIFICATION.md`, `45-VERIFICATION.md` | `.planning/`, `.planning/milestones/`, `.planning/reviews/` | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_governance_closeout_guards.py tests/meta/test_governance_phase_history.py tests/meta/test_governance_phase_history_runtime.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py` | `42 -> 45` | archived / evidence-ready promotion completed; archive snapshots are historical only, and the milestone audit remains the verdict home |

## Release / Closeout Pull Boundary

- Maintainer release issues must start from `docs/MAINTAINER_RELEASE_RUNBOOK.md` and this index, not from ad-hoc file hunting.
- `archive-ready / shipped` 判断以 `.planning/v1.6-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起。
- release-trust posture 继续显式保留 `SHA256SUMS`、`SBOM`、`provenance`、`signing`、`code scanning`、release artifact install smoke 与 release identity manifest 等证据关键字；`firmware manifest metadata` 仍明确记为 deferred truth。
- `v1.6` archive snapshots 是历史记录，不取代 `.planning/ROADMAP.md` / `.planning/REQUIREMENTS.md` / `.planning/STATE.md` 的活跃治理角色。
