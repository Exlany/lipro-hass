# Phase 70: Support-seam slimming, OTA resolver consolidation, and governance test topicization - Context

Date: 2026-03-24
Mode: Active current milestone route for `v1.18`

## Phase Boundary

本 phase 只处理 `v1.17` 归档后终极审阅锁定的高杠杆 residual：runtime-access inward split、anonymous-share submit flow decomposition、OTA shared helper convergence、archive freeze / version-guard decoupling、治理 mega-tests topicization。目标是在不重开第二主链、不发明新 public root 的前提下，把这些 formal homes 再收一轮。

In scope:
- `custom_components/lipro/control/runtime_access_support.py` inward split
- `custom_components/lipro/core/anonymous_share/share_client_flows.py` decomposition
- `custom_components/lipro/core/api/diagnostics_api_ota.py` 与 `custom_components/lipro/entities/firmware_update.py` 的 OTA shared helper / selector convergence
- `tests/meta/test_version_sync.py`、`tests/meta/test_governance_release_contract.py`、`tests/meta/test_governance_milestone_archives.py` 的 archive/current concern rebalancing
- `PROJECT / ROADMAP / REQUIREMENTS / STATE / review ledgers / docs` 的 current-story sync

Out of scope:
- 重开 `Phase 69` 已关闭的 schedule/service de-protocolization route
- 仓库级 `Any`/`object` 债务清零
- 虚构 maintainer delegate / org custody / support SLA
- 广泛 public API 重命名或重新设计 protocol/runtime roots

## Implementation Decisions

### Locked Decisions

1. `runtime_access.py` 继续作为唯一 outward runtime home；任何 helper split 都只能发生在 inward support family 内部。
2. `share_client.py` outward contract 保持稳定；submit/refresh/outcome 逻辑只做 inward decomposition。
3. `diagnostics_api_ota.py` 继续是 OTA diagnostics outward home；query/merge/selection 的 shared mechanics 下沉到更窄 helper，不引入第二 API root。
4. 历史 evidence / archived phase 文档不得继续承担版本同步义务；版本可变真源只允许 current docs / registry / runbook / package metadata。
5. 治理测试必须继续 topicization：一条测试只表达一个 concern family，重复断言优先抽 helper/parameterization。

### the agent's Discretion

- 允许决定 runtime-access helper 的最佳拆分粒度，但必须保持 `runtime_access.py` outward API 不变。
- 允许决定 anonymous-share submit/refresh helper 的最优分层，只要 outward client contract 不漂移。
- 允许决定 archive freeze guards 的最优测试归属，只要 release / archive / version 的权责边界更清楚。

## Canonical References

### Governance / north-star truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/reviews/V1_18_TERMINAL_AUDIT.md`

### Starting baseline
- `.planning/v1.17-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_17_EVIDENCE_INDEX.md`
- `.planning/milestones/v1.17-ROADMAP.md`
- `.planning/milestones/v1.17-REQUIREMENTS.md`
- `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-SUMMARY.md`
- `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-VERIFICATION.md`
- `.planning/phases/69-residual-read-model-quality-balance-and-open-source-contract-closure/69-VALIDATION.md`

### Hotspot homes
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/runtime_access_support.py`
- `custom_components/lipro/core/anonymous_share/share_client.py`
- `custom_components/lipro/core/anonymous_share/share_client_flows.py`
- `custom_components/lipro/core/api/diagnostics_api_ota.py`
- `custom_components/lipro/core/ota/rows_cache.py`
- `custom_components/lipro/entities/firmware_update.py`

### Governance / test families
- `tests/meta/test_phase68_hotspot_budget_guards.py`
- `tests/meta/test_phase69_support_budget_guards.py`
- `tests/meta/test_version_sync.py`
- `tests/meta/test_governance_release_contract.py`
- `tests/meta/test_governance_milestone_archives.py`
- `tests/meta/governance_followup_route_current_milestones.py`
- `docs/README.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `SUPPORT.md`
- `SECURITY.md`

## Specific Ideas

- 把 explicit member probing、telemetry coercion、view builders、device/debug helpers 从 `runtime_access_support.py` 中拆开。
- 给 anonymous-share 的 refresh / submit / outcome mapping 建立更窄 helper modules，并让 `share_client_flows.py` 退成 orchestration home。
- 让 OTA selection 改走 shared selector helper，避免 `firmware_update.py` 重复 `arbitrate_rows()` / retry-without-cache choreography。
- 让 `test_version_sync.py` 只守 current mutable version truth，把 archive frozen assertions 回收给 milestone/archive family。
- 把 release / archive / version 断言中的重复块抽到 shared test helper。

## Deferred Ideas

- `entry_root_wiring.py` / `runtime_infra.py` 的进一步 typed-port 收紧
- repo-wide `Any` budget 清零
- `options/config` 语义统一化
- 历史 phase-number test 文件名重命名
