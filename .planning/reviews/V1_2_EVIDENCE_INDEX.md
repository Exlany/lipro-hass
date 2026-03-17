# v1.2 Evidence Index

**Purpose:** 为 `v1.2 Host-Neutral Core & Replay Completion` 提供机器友好的 closeout / release / audit 入口，集中列出 host-neutral、headless proof、remaining-family completion、replay/observability 以及 milestone closeout 的正式证据指针。
**Status:** Pull-only closeout index
**Updated:** 2026-03-16

## Pull Contract

- 本文件只索引正式真源、phase verification/summaries 与 milestone closeout assets；它不是新的 authority source。
- maintainer release flow、milestone audit 与后续 handoff 只能从这里继续 pull 已登记证据，不得重新扫描仓库拼装第二套事实。
- `failure_summary` / `failure_entries` 只是 shared contract projection；canonical authority 仍在 telemetry / baseline / review truth 中。
- `v1.3-HANDOFF.md` 是下一轮 seed asset，不替代当前 closeout truth。

## Evidence Families

| Family | Upstream truth | Stable home | Core verify command | Phase owner | Closeout note |
|--------|----------------|-------------|---------------------|-------------|---------------|
| Host-neutral nucleus | `custom_components/lipro/core/auth/bootstrap.py`, shared capability/device homes, `.planning/phases/18-host-neutral-boundary-nucleus-extraction/18-VERIFICATION.md` | `.planning/phases/18-host-neutral-boundary-nucleus-extraction/` | `uv run python scripts/check_architecture_policy.py --check && uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py` | `18` | single-chain host-neutral extraction；不引入第二 root |
| Headless consumer proof | `custom_components/lipro/headless/boot.py`, `tests/harness/headless_consumer.py`, `.planning/phases/19-headless-consumer-proof-adapter-demotion/19-VERIFICATION.md` | `.planning/phases/19-headless-consumer-proof-adapter-demotion/` | `uv run pytest -q tests/integration/test_headless_consumer_proof.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py` | `19` | proof-only consumer，non-authority / non-second-root |
| Remaining boundary family completion | boundary inventory + `tests/fixtures/{api_contracts,protocol_boundary,protocol_replay}/`, `.planning/phases/20-remaining-boundary-family-completion/20-VERIFICATION.md` | `.planning/phases/20-remaining-boundary-family-completion/` | `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/meta/test_protocol_replay_assets.py` | `20` | remaining families 全部进入 formal boundary / replay chain |
| Replay / exception taxonomy hardening | shared telemetry taxonomy, replay driver/report, `.planning/phases/21-replay-exception-taxonomy-hardening/21-VERIFICATION.md` | `.planning/phases/21-replay-exception-taxonomy-hardening/` | `uv run pytest -q tests/core/api/test_protocol_replay_rest.py tests/core/mqtt/test_protocol_replay_mqtt.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/meta/test_protocol_replay_assets.py tests/meta/test_evidence_pack_authority.py` | `21` | replay / evidence 对 remaining families 显式覆盖，failure taxonomy freeze 完成 |
| Observability consumer convergence | diagnostics/system-health/developer/evidence consumers, `.planning/phases/22-observability-surface-convergence-and-signal-exposure/22-VERIFICATION.md` | `.planning/phases/22-observability-surface-convergence-and-signal-exposure/` | `uv run pytest -q tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_control_plane.py tests/services/test_services_diagnostics.py tests/services/test_services_share.py tests/integration/test_ai_debug_evidence_pack.py` | `22` | shared `failure_summary` vocabulary 进入 control/service/evidence 消费面 |
| Governance / contributor / release evidence closeout | `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`, baseline/review ledgers, maintainer/public docs, `.planning/phases/23-governance-convergence-contributor-docs-and-release-evidence-closure/23-VERIFICATION.md` | `.planning/phases/23-governance-convergence-contributor-docs-and-release-evidence-closure/` | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py tests/meta/test_evidence_pack_authority.py` | `23` | contributor docs / templates / runbook / testing-map drift guards 讲同一条故事；supply-chain defer boundary 显式登记 |
| Milestone audit / archive-ready / handoff bundle | `.planning/v1.2-MILESTONE-AUDIT.md`, `.planning/MILESTONES.md`, `.planning/v1.3-HANDOFF.md`, `.planning/phases/24-final-milestone-audit-archive-readiness-and-v1-3-handoff-prep/24-VERIFICATION.md` | `.planning/phases/24-final-milestone-audit-archive-readiness-and-v1-3-handoff-prep/`, `.planning/` | `uv run python scripts/check_architecture_policy.py --check && uv run python scripts/check_file_matrix.py --check && uv run pytest -q tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py && uv run ruff check . && uv run mypy && uv run pytest -q tests/core/test_control_plane.py::test_find_runtime_entry_for_coordinator_prefers_bound_entry` | `24` | archive-ready / handoff-ready closeout bundle revalidated 2026-03-17 |

## Phase Evidence Ledger

| Phase | Locked truth | Summary / verification | Pullable outputs |
|------|--------------|------------------------|------------------|
| `18` | host-neutral nucleus / adapter demotion | `18-01~18-03-SUMMARY.md`, `18-VERIFICATION.md` | shared auth bootstrap, adapter-only platform projection, host-neutral guards |
| `19` | headless proof / non-second-root contract | `19-01~19-04-SUMMARY.md`, `19-VERIFICATION.md` | headless boot seam, proof harness, second-root guards |
| `20` | remaining boundary family completion | `20-01~20-03-SUMMARY.md`, `20-VERIFICATION.md` | registry-backed boundary families, replay/inventory closeout |
| `21` | replay coverage / failure taxonomy | `21-01~21-03-SUMMARY.md`, `21-VERIFICATION.md` | explicit replay assurance, shared failure taxonomy, typed exception arbitration |
| `22` | observability consumer convergence | `22-01~22-03-SUMMARY.md`, `22-VERIFICATION.md` | diagnostics/system-health/developer/evidence shared failure vocabulary |
| `23` | governance/docs/release evidence convergence | `23-01~23-08-SUMMARY.md`, `23-VERIFICATION.md` | unified lifecycle truth, public-entry docs sync, testing-map drift guard, explicit release defer ledger |
| `24` | final audit / milestone bundle / handoff | `24-01~24-05-SUMMARY.md`, `24-VERIFICATION.md` | final repo audit, closeout gate recovery, v1.2 milestone audit, v1.3 handoff |

## Release / Closeout Pull Boundary

- Maintainer release issues must start from `docs/MAINTAINER_RELEASE_RUNBOOK.md` and this index, not from ad-hoc file hunting.
- `archive-ready` 判断以 `.planning/v1.2-MILESTONE-AUDIT.md` 为 verdict home；本索引只负责把证据指针收在一起，fresh gate rerun 记录则落在 `24-VERIFICATION.md`。
- 若后续 `v1.3` 继续推进 typed hardening / residual cleanup，只能在新 phase 中登记，不得回改 `v1.2` closeout history。


## Phase 23 Explicit Defer Boundary

- Shipped in this closeout: default installer guidance stays on `ARCHIVE_TAG=latest`, CI reuse remains mandatory for release, tagged builds verify version truth, and release assets publish `SHA256SUMS`.
- Explicitly deferred beyond this phase: `provenance`, published `SBOM`, release artifact `signing`, making `code scanning` a hard release gate, and richer firmware manifest metadata.
- Firmware certification truth remains localized to `custom_components/lipro/firmware_support_manifest.json`; later metadata expansion must land in a new phase, not as silent drift.
