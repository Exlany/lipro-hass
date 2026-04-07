# Phase 70 Research

Date: 2026-03-24
Phase: `70`

## Confirmed Findings

### Runtime access hotspot
- `runtime_access_support.py` 当前约 `478` 行，贴近 `tests/meta/test_phase69_support_budget_guards.py` 上限 `480`。
- 它同时负责：explicit member probing、telemetry JSON narrowing、runtime coordinator / entry read-model、device lookup、debug-mode gating。
- 最优策略不是扩写 `runtime_access.py`，而是把 support family inward split，保持 outward API 完全不变。

### Anonymous-share hotspot
- `share_client_flows.py` 当前约 `519` 行，贴近 `tests/meta/test_phase68_hotspot_budget_guards.py` 上限 `540`。
- 热点函数集中在：`refresh_install_token_with_outcome()`、`submit_share_payload_with_outcome()`、`_resolve_submit_attempt_outcome()`。
- outward home 仍应维持在 `share_client.py`；最优路线是拆 submit/refresh/outcome helpers。

### OTA helper drift
- `diagnostics_api_ota.py` 仍承担 query/fallback/dedupe/outcome。
- `firmware_update.py` 仍手工做 `arbitrate_rows()` + `retry_without_cache` choreography，尽管 `rows_cache.py` 已提供 `async_select_row_with_shared_cache()`。
- 最优路线：抽 shared OTA helper / selector，并让 entity 改走 shared selector；diagnostics outward API 保持不动。

### Governance / archive freeze
- `test_version_sync.py` 仍直接触碰 archived phase/evidence 资产，导致 archive freeze 不彻底。
- `test_governance_release_contract.py`、`test_governance_milestone_archives.py`、`governance_followup_route_current_milestones.py` 仍有重复断言与 giant-test concern mixing。
- 最优路线：current mutable truth 留给 `version_sync` / release docs；archive freeze 留给 milestone/archive guards；重复断言抽 helper。

## Selected Strategy

1. 先建立 `Phase 70` validation + hotspot/governance guards。
2. inward split `runtime_access_support.py`。
3. inward split `share_client_flows.py` 并收 OTA shared selector。
4. topicize governance tests，冻结 archive/current version truth 边界。
5. 回写 planning/review/baseline/docs truth，并执行 full gate。

## Risks and Controls

- **Risk:** helper split 引发 circular import。
  - **Control:** 新 helper 只被原 formal home 反向 import；不让 outward callers直接接触新模块。
- **Risk:** archive/version guards 重新分配后产生 coverage gap。
  - **Control:** 在 `70-VALIDATION.md` 中明确 current-vs-archive guard owner。
- **Risk:** OTA selector 收口改变缓存/重试语义。
  - **Control:** 优先复用 `rows_cache.async_select_row_with_shared_cache()`；补 focused entity/OTA tests。
