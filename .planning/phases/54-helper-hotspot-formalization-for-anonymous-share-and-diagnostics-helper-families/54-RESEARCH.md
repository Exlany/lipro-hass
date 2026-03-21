# Phase 54 Research — Helper-hotspot formalization

**Date:** 2026-03-21
**Requirement focus:** `HOT-13`

## Hotspot Inventory

### 1. `custom_components/lipro/core/anonymous_share/manager.py`
- ~536 lines，集中承载 scope registry/view、enable/config、磁盘缓存、recording、report build、submit gating、developer feedback submit。
- 已存在 `_ScopeState` 与 `report_builder.py` / `registry.py` 等支点，适合继续 inward decomposition，而不是创建第二 manager。
- 推荐切口：scope-state/cache、submit gating、aggregate report assembly、feedback submit bridge。

### 2. `custom_components/lipro/core/anonymous_share/share_client.py`
- ~438 lines，把 install-token 状态、refresh、submit、429/401/413 分支、lite payload fallback 与 typed outcomes 混在一个类里。
- 推荐切口：token lifecycle、attempt planning、HTTP outcome mapping、lite fallback/backoff clock。
- 关键要求：`ShareWorkerClient` surface 与 worker payload contract 不变。

### 3. `custom_components/lipro/services/diagnostics/helpers.py`
- ~409 lines，混合 service 参数解析、exporter/runtime report 收集、auth-aware capability 调用、feedback payload build、service response shaping。
- 推荐切口：report collection、feedback payload builder、optional capability executor、response shaping / sensor-history result。
- 关键要求：仍只是 control helper，不重定义 public service handler home。

### 4. `custom_components/lipro/core/api/request_policy.py`
- ~456 lines，同时存在 pure helper math、mutable pacing cache、busy retry orchestration。
- `RequestPolicy` formal truth 已在 `Phase 52` 锁定，但 companion seams 仍可继续 inward decomposition。
- residual 重点：`compute_exponential_retry_wait_time()` 的跨-family leak 已显式登记，Phase 54 需仲裁是 neutral shared backoff home 还是继续 deferred residual。

## Formal-Home Constraints

- `RequestPolicy` 仍是 protocol plane 下 `429` / busy / pacing 的 formal truth；不得把 mapping/auth-aware request orchestration 从 `request_gateway` / executor side 重新吸回它。
- diagnostics developer report 的 local debug view 与 upload projector 必须继续分家；feedback payload builder 不得回流成 public control story。
- anonymous-share 家族属于 protocol-adjacent support；aggregate/scoped public semantics 仍由 `AnonymousShareManager` 持有，不得复制一套 public share root。
- typed/broad-catch budgets 仍受 `tests/meta/test_phase31_runtime_budget_guards.py`、`tests/meta/test_phase45_hotspot_budget_guards.py` 与 `tests/meta/test_phase50_rest_typed_budget_guards.py` 约束。

## Recommended Wave Plan

### Wave 1 — Manager slimming
- Extract scope-state/cache and submit/report mechanics into support-only seams.
- Preserve `AnonymousShareManager` public behavior and aggregate/scoped story.
- Verify with anonymous-share manager/storage/observability suites.

### Wave 2 — Share client transport/outcome split
- Extract token refresh / attempt planner / HTTP outcome mapping / lite fallback mechanics.
- Preserve `ShareWorkerClient` surface.
- Verify with share client suites and manager submission boundary coverage.

### Wave 3 — Diagnostics helper family topicization
- Split report collection, feedback payload, optional-capability execution, and response shaping.
- Preserve control-plane public handler home.
- Verify with diagnostics/share service suites and init share-report handlers.

### Wave 4 — Request-policy companion closure + truth freeze
- Separate pure math/backoff helpers, pacing cache state access, and policy-owned async decisions.
- Update residual/baseline/meta truth depending on backoff leak disposition.
- Verify with request-policy tests + meta guards + file matrix check.

## Non-Goals
- No runtime/entry-root refactor here.
- No mega-test or typing-metric work here.
- No second public share/diagnostics/request root.
