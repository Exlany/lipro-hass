# v1.18 Terminal Architecture Audit

**Date:** 2026-03-24
**Scope:** `lipro-hass` repo-wide终审（代码、文档、配置、治理与测试拓扑）
**Verdict:** `actionable / phase-routed`

## Executive Verdict

本轮终审结论明确：仓库整体已具备成熟 north-star 结构，正式 protocol/runtime/control 主链没有出现第二根回流；但 remaining debt 仍集中在少数“正确但偏厚”的 formal homes、archive/current truth 的边界漂移，以及治理 mega-tests 的 failure-localization 成本。

高优先级问题已收束为以下 5 个 concern families：

1. `runtime_access_support.py` 仍混合 explicit probing、telemetry coercion、runtime view build、device lookup 与 debug-mode 判定。
2. `share_client_flows.py` 仍把 token refresh、submit variants、submit outcome resolution 聚合在一个 formal home。
3. OTA query / dedupe / selection 逻辑仍横跨 `core/api/diagnostics_api_ota.py`、`core/ota/rows_cache.py`、`entities/firmware_update.py`。
4. archive/latest-evidence/version truth 仍有 current-doc / historical-doc 混线，导致 archive freeze 不够彻底。
5. `tests/meta` 仍存在 mega-test、phase-number shell、重复断言与职责交叉。

## Strengths

- north-star / governance / public-surface / authority-chain 已相当成熟，formal root 基本稳定。
- CI / release / security / SBOM / attestation / signature posture 明显高于普通 HA 集成项目。
- repo-wide meta/test/toolchain 体系已能持续阻断第二主链、public-surface drift 与 docs-governance 漂移。
- 多数热点已经沿“formal home + inward split”的路线处理过一轮，本轮是最后几处高密度 residual。

## High Findings

### 1. Runtime access 仍是半去反射状态
- 证据：`custom_components/lipro/control/runtime_access_support.py`
- 问题：explicit member probing、telemetry coercion、entry/coordinator read-model、device lookup 与 debug-mode 逻辑混居；`runtime_access.py` 虽维持 outward home，但 inward support 仍过厚。
- 风险：维护者难以快速判断“类型适配”与“runtime policy”边界，后续再变厚时难以及时定位。
- 处理路线：拆成更窄 helper clusters，保持 `runtime_access.py` 继续作为唯一 outward home。

### 2. Anonymous-share flow hotspot 仍偏厚
- 证据：`custom_components/lipro/core/anonymous_share/share_client_flows.py`
- 问题：refresh / submit / response-resolution 在一个模块内高度耦合；compat bool wrapper 仍共存于 public client。
- 风险：reason-code、token fallback、payload fallback 的 regression 难以局部验证。
- 处理路线：按 refresh flow / submit flow / attempt resolution inward split，保持 `share_client.py` outward contract 不变。

### 3. OTA query / selection truth 仍分散
- 证据：`custom_components/lipro/core/api/diagnostics_api_ota.py`, `custom_components/lipro/core/ota/rows_cache.py`, `custom_components/lipro/entities/firmware_update.py`
- 问题：query merge/dedupe 与 selection/retry/cache 在 diagnostics/entity 两侧重复编排。
- 风险：后续 OTA fallback 变更需要多点同步，容易出现“query 成功但 selection 语义漂移”。
- 处理路线：抽 shared OTA helper；entity 改走 shared selector，diagnostics 保留 outward API home。

### 4. Archive freeze 仍不够硬
- 证据：`tests/meta/test_version_sync.py`, `tests/meta/test_governance_milestone_archives.py`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- 问题：部分 version/doc guards 仍触碰 archived phase/evidence 文档；历史资产会被新版本 bump 间接牵连。
- 风险：archive 漂移、current truth 重复、历史 closeout 被反向改写。
- 处理路线：只让 current docs / registry / runbook 承担可变版本 truth；archive 只验证 frozen contract。

### 5. Governance mega-tests 仍有高重复与低定位
- 证据：`tests/meta/test_governance_release_contract.py`, `tests/meta/governance_followup_route_current_milestones.py`, `tests/meta/test_governance_milestone_archives.py`
- 问题：单测试吞多个 concern；重复断言多；release/archive/version/runbook 权责边界交叉。
- 风险：任何一处 drift 会放大成多文件连锁失败，审阅/维护成本持续上升。
- 处理路线：抽 shared assertion helpers，按 release/archive/version/current-route concern 再 topicize 一轮。

## Medium Findings

- `docs/README.md`、`SUPPORT.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md` 的 public first-hop / maintainer-only route 仍有语义噪音。
- `tests/meta/test_phase68_hotspot_budget_guards.py` 与 `tests/meta/test_phase69_support_budget_guards.py` 继续使用 phase-number naming；历史归档友好，但 domain discoverability 一般。
- `entry_root_wiring.py`、`runtime_infra.py`、`options_flow.py` 仍有 `object` / `Mapping[str, Any]` 级别 typing residual；本轮先不扩大 touched scope。

## Low Findings

- 少量 `legacy` / `shim` 文案仍存在于已收口 formal homes。
- `scripts/` 与 `.planning/reviews/` 仍有 discoverability improvement 空间，但不是当前主链 blocker。

## Phase 70 Routing

- `70-01`: 冻结审阅结论、建立 validation contract、补 phase-70 hotspot/governance guards。
- `70-02`: inward split `runtime_access_support.py`。
- `70-03`: inward split `share_client_flows.py` 并收敛 OTA shared helper / selector。
- `70-04`: topicize governance tests，冻结 archive/current version truth 边界。
- `70-05`: 回写 planning/baseline/review/docs truth，执行 final gate。

## Human Constraints Outside Code

以下问题可以被 honest documentation 记录，但不能由本轮代码修改“虚构修复”：

- 单维护者 `bus factor`
- 不存在的组织级 delegate / support SLA
- 未真实建立的双人 release ownership

这些问题若要真正解决，必须由维护者/组织层面补齐，而不是通过文案伪装成已完成。
