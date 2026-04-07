# Phase 120: terminal audit closure, contract hardening, and governance truth slimming - Context

**Status:** planning-ready
**Milestone:** `v1.34 Terminal Audit Closure, Contract Hardening & Governance Truth Slimming`
**Current route:** `v1.34 active milestone route / starting from latest archived baseline = v1.33`
**Default next command:** `$gsd-plan-phase 120`

## Phase Boundary

**In scope**
- tighten `runtime_types.py` / `runtime_access.py` / `services/command.py` to a more explicit single-source contract story
- harden `flow/login.py` / `flow/submission.py` error taxonomy and aligned translations/tests
- collapse `scripts/check_file_matrix.py` import entry semantics to one truth and de-brittle related meta guards
- replace `scripts/lint` `phase113_*` changed-surface hard-coding with reusable data-driven assurance metadata
- move `docs/developer_architecture.md` historical appendix out of current docs and convert runbook / PR template to stable current-route or latest-archived pointers
- codify maintainer continuity freeze posture / custody restoration honesty without inventing a delegate

**Out of scope**
- introducing new product features, new public services, or second control/runtime/protocol roots
- changing `Coordinator` public home or rewriting archived milestone assets/history
- solving repo-external continuity blockers outside repo-visible contracts

## Implementation Decisions

### Locked decisions
- `Coordinator` public runtime home remains `custom_components/lipro/coordinator_entry.py`; only contract truth, tooling truth, and docs truth may tighten.
- `Phase 120` is the only delivery phase in `v1.34`; all touched requirements must map to it exactly once.
- maintainer continuity may only be tightened as honest freeze posture / custody-restoration wording; no hidden delegate, mirror, or private fallback may be implied.
- current docs must prefer stable pointers or latest-archived pointers over version-pinned `.planning/vX_*` references.

### the agent's Discretion
- choose the narrowest typed aliases / helpers that remove loose mapping folklore without introducing a second truth carrier
- decide whether `send_command` strictness lives in schema validators, normalization helpers, or both, as long as the outward truth is single-source
- choose the smallest viable guard strategy (AST / helper-based / behavior-based) that removes brittle string containment checks
- pick the appropriate archive-facing home for the developer-architecture appendix so current docs stay slim and history remains reachable

## Canonical References

### North-star and governance truth
- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`

### Runtime / flow / tooling hotspots
- `custom_components/lipro/runtime_types.py`
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/services/command.py`
- `custom_components/lipro/services/contracts.py`
- `custom_components/lipro/flow/login.py`
- `custom_components/lipro/flow/submission.py`
- `scripts/check_file_matrix.py`
- `scripts/lint`
- `docs/developer_architecture.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `.github/pull_request_template.md`

### Focused guards / tests
- `tests/meta/test_runtime_contract_truth.py`
- `tests/core/test_runtime_access.py`
- `tests/services/test_service_resilience.py`
- `tests/flows/test_config_flow_user.py`
- `tests/flows/test_config_flow_reauth.py`
- `tests/flows/test_config_flow_reconfigure.py`
- `tests/flows/test_flow_submission.py`
- `tests/meta/toolchain_truth_checker_paths.py`
- `tests/meta/test_phase89_tooling_decoupling_guards.py`
- `tests/meta/test_governance_release_docs.py`

## Specific Ideas

- `120-01` 应优先把 runtime/service contract tightening 与 runtime-access fallback normalization 放在同一束里，避免 `runtime_types`、`runtime_access`、`services/contracts`、`services/command` 再分裂成多套 truth。
- `120-02` 应把 flow error taxonomy 与 stored-entry validation 一次性讲清：invalid-entry、invalid-response 与 unexpected-error 必须有各自 translation / regression，不要只在日志里区分。
- `120-03` 应统一 toolchain/docs/governance truth：`check_file_matrix` import 单一入口、meta guards 更结构化、`scripts/lint` 去 phase literal、docs/runbook/template 指向稳定 current-route family 或 latest archived pointer。

## Deferred Ideas

- repo-external delegate onboarding、non-GitHub mirror continuity、private fallback implementation：本 phase 只允许诚实记录，不负责仓外闭环。
- `.planning/PROJECT.md` / `.planning/ROADMAP.md` 全量历史瘦身：本轮以 current-route correctness 为主，不做大规模历史重写。
- any new product-facing behavior or UX expansion unrelated to audit follow-through.

*Phase: 120-terminal-audit-contract-hardening-and-governance-truth-slimming*
