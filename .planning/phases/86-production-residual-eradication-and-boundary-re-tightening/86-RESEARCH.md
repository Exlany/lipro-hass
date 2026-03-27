# Phase 86: Production residual eradication and boundary re-tightening - Research

**Researched:** 2026-03-27
**Domain:** production residual cleanup / boundary re-tightening / truthful closeout
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- 本 phase 只覆盖 `HOT-37` 与 `ARC-22`，目标是清掉 `Phase 85` terminal audit 明确路由过来的 production residual，同时保持 formal roots 不漂移。
- `custom_components/lipro/core/anonymous_share/share_client.py` 仍是 anonymous-share worker client 的正式 home；允许删除 compat shell，但不得把 formal ownership 挪到新 root。
- `custom_components/lipro/runtime_infra.py` 仍是 runtime infra 的正式 home；允许做 inward split，但不得重定根、不得新增 public backdoor、不得让 helper 反向定义 public truth。
- code / adjacent tests / ledgers 必须同 phase 同步；不能留下“代码改了但 governance 还在讲旧故事”的半收口状态。
- `Phase 87` 的 giant assurance topicization 与 `Phase 88` 的 governance freeze / milestone closeout 不得提前偷跑。
- 用户明确偏好：有收益才拆；能提升代码质量与后续维护便利性的拆分要做，但不要为了拆而拆。

### the agent's Discretion
- `runtime_infra.py` inward split 的 helper 颗粒度可在实施时微调，但必须保持 `runtime_infra.py` 作为唯一 outward import home。
- 若删除 compat shell 后，相邻测试命名/断言仍可进一步收紧为 outcome-native 语义，可一并完成。
- ledger / file-matrix / review truth 的 closeout 形式可自由设计，但必须 machine-checkable。

### Deferred Ideas (OUT OF SCOPE)
- `tests/core/api/test_api_diagnostics_service.py`、`tests/core/api/test_protocol_contract_matrix.py`、`tests/core/coordinator/runtime/test_mqtt_runtime.py` 的 giant-suite topicization 留给 `Phase 87`。
- milestone closeout、archived baseline freeze、repo-wide quality-proof promotion 留给 `Phase 88`。
- 任何新 feature、public API redesign、或跨 plane 的重新分层都不属于本 phase。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HOT-37 | audit 确认的 production residual / hotspot carriers 必须被删除、拆薄或压回 formal/local helper home；正式目录中不得继续保留 empty shell、stale alias 或 compat folklore。 | `## ShareWorkerClient residual findings`、`## runtime_infra hotspot findings`、`## Recommended Plan Decomposition` |
| ARC-22 | residual eradication 过程中，protocol / runtime / control / domain 仍各自保持单一正式主链；不得引入 second root、backdoor 或 helper-owned public truth。 | `## Boundary constraints that must stay true`、`## Common Pitfalls`、`## Recommended Plan Decomposition` |
</phase_requirements>

## Summary

`Phase 86` 的最佳策略不是“大拆所有热点”，而是把 `Phase 85` 已经裁决为 **production-path residual** 的两个具体目标一次收干净，并同步关闭对应 governance debt。当前证据显示，这两个目标都具备“边界清晰、收益明确、可局部验证”的特征：

1. `ShareWorkerClient` 的 residual 只剩两个 symbol-level compat seams：`_safe_read_json()` backward alias 与 bool-only `submit_share_payload()` shim。production truth 已经以 `safe_read_json()` 与 `submit_share_payload_with_outcome()` 为正式语义，manager/submit flow 也早已围绕 `OperationOutcome` 建立；因此这里最优解是 **直接删除 compat seam，并把 tests 一次性收口到 outcome-native contract**。
2. `runtime_infra.py` 仍是正确的 formal home，但它已经成为 listener / reload scheduling / pending task bookkeeping / shared-lock bootstrap 的密集载体。当前文件长度 `433` 行，虽然仍在 `440` 行 guard 内，但维护负担已经体现在 concern density，而不是表层行数超标。这里最优解不是迁 root，而是 **在 formal home 内做 inward split，把 device-registry reload mechanics 与 bootstrap bookkeeping 拆成 local helper modules，同时保留 `runtime_infra.py` 作为唯一 outward truth**。
3. 若只改代码不关 ledger，本 phase 会再次制造 route drift。`KILL_LIST.md`、`RESIDUAL_LEDGER.md`、`FILE_MATRIX.md` 与 `V1_23_TERMINAL_AUDIT.md` 已明确把这两个条目路由到 `Phase 86`；因此 closeout 必须与代码同 phase 完成，并通过 meta guards / scripts 固化。

**Primary recommendation:** 用四段式执行：`86-01` 删除 `ShareWorkerClient` compat seams 并更新测试；`86-02` inward split `runtime_infra.py` 但保持其 formal home；`86-03` 先关闭 routed review ledgers；`86-04` 再冻结 current-route / baseline / follow-up guard truth，并显式把 giant assurance topicization 继续留在 `Phase 87`。

## Standard Stack

| Tool / Asset | Verified | Purpose | Why Standard Here |
|--------------|----------|---------|-------------------|
| current truth chain | repo docs | 裁决 ownership / route / phase boundary | `NORTH_STAR -> PROJECT/ROADMAP/REQUIREMENTS/STATE -> baseline/reviews` 已明确 `Phase 86` 边界 |
| `share_client_flows.py` / `share_client_support.py` | code | 承接 typed submit/refresh/JSON helper truth | 说明 `share_client.py` 已具备删除 compat seam 的正式支点 |
| `runtime_infra.py` + existing tests/meta guards | code + tests | 锁定 formal runtime infra home | 允许 inward split，但禁止 ownership 漂移 |
| `scripts/check_file_matrix.py` / `scripts/check_architecture_policy.py` | tooling | closeout 后校验 governance truth | 保证不是 conversation-only completion |

## ShareWorkerClient residual findings

### Finding 1: `_safe_read_json()` 是纯 backward alias，使用面已缩到单个测试

- `_safe_read_json()` 只在 `custom_components/lipro/core/anonymous_share/share_client.py` 定义，并仅在 `tests/core/test_share_client_primitives.py` 中被调用一次。
- 正式 JSON reader 早已是 `safe_read_json()`，其真实实现位于 `custom_components/lipro/core/anonymous_share/share_client_flows.py` 的 `safe_read_json()` flow。
- `custom_components/lipro/core/anonymous_share/share_client_refresh.py` 与 `share_client_submit.py` 都通过 `client.safe_read_json(...)` 读取 Worker payload，没有任何 production caller 依赖 `_safe_read_json()`。

**Conclusion:** 这是标准的 delete-now residual，不需要 adapter，不需要过渡壳；删掉 alias 并改掉唯一测试即可。

### Finding 2: bool `submit_share_payload()` shim 已经不是 production truth

- `ShareWorkerClient.submit_share_payload_with_outcome()` 已明确以 `OperationOutcome` 作为正式提交 contract。
- `custom_components/lipro/core/anonymous_share/manager.py` 的核心提交路径已经围绕 `_submit_share_payload_with_outcome()` 运作；bool 返回只保留在 manager 自己的 scope helper 中，不再决定 share-client formal truth。
- `rg` 结果显示 `ShareWorkerClient.submit_share_payload(...)` 的直接使用面几乎全在 `tests/core/test_share_client_submit.py`；production 代码没有新的 direct caller 把它当主链。
- `RESIDUAL_LEDGER.md` 也明确写明：production/tests 应只承认 outcome-native path。

**Conclusion:** 删除 `ShareWorkerClient.submit_share_payload()` compat shim 的风险低、收益高；测试应迁移到 `submit_share_payload_with_outcome()` 并直接断言 `is_success` / `reason_code` / `http_status` 等 typed semantics。

## runtime_infra hotspot findings

### Finding 3: `runtime_infra.py` 是 formal home，但具备明确 inward split 价值

- `custom_components/lipro/runtime_infra.py` 当前长度 `433` 行，距离 `tests/meta/test_phase69_support_budget_guards.py` / `tests/meta/test_phase72_runtime_bootstrap_route_guards.py` 中的 `440` 行预算只剩很小余量。
- 关键 outward API 很少且边界清楚：`async_setup_device_registry_listener()`、`setup_device_registry_listener()`、`remove_device_registry_listener()`、`get_runtime_infra_lock()`、`async_ensure_runtime_infra()`、`has_other_runtime_entries()`。
- production import locality 也非常干净：`custom_components/lipro.runtime_infra` 在 production 侧只由 `custom_components/lipro/__init__.py` 直接导入；control 路径通过 dependency injection 消费这些函数，而不是到处直接 import。
- 因此真正的问题不是“根放错了”，而是一个 formal home 同时承载了：
  - device-registry update 解析与 reload plan 生成
  - pending reload task bookkeeping / done-callback 收口
  - listener setup / teardown
  - shared lock/bootstrap orchestration

**Conclusion:** 最佳处理方式是在 `runtime_infra.py` 内保持 outward root 身份不变，把上述 concern inward split 到 one-hop local helpers / support modules，并同步更新 import-locality meta guards。这样能降低维护密度，同时不产生 second root。

### Finding 4: `runtime_infra` 拆分必须与 meta guards 同步设计

`Phase 86` 如果新增 helper modules，至少会影响以下 guard families：

- `tests/meta/test_phase69_support_budget_guards.py`：当前只知道 `runtime_infra.py` 这一个 runtime-infra production module，需要补充新 internal helper module 的 locality truth。
- `tests/meta/test_phase72_runtime_bootstrap_route_guards.py`：当前 line/function budget 与 locality 只覆盖现状；若拆出 helper，必须把 allowed importers 和 line budgets 写实。
- `tests/meta/dependency_guards_service_runtime.py`：runtime/service boundary 目前要求 listener truth 仍归 `runtime_infra.py`；拆分后要确保 outward prose 仍指向 `runtime_infra.py`，而不是让 helper 抢走“正式 home”的描述。

**Conclusion:** `86-02` 不能只是代码抽取；它本身就必须包含 meta/no-regrowth 更新。

## Boundary constraints that must stay true

1. `ShareWorkerClient` 继续是 anonymous-share worker client 的唯一正式 outward home；不得把 typed submit contract 再移去其它模块，只能删除 compat seam。
2. `runtime_infra.py` 继续是 runtime infra 的正式 outward home；新 helper 只能 inward/localized，不得被 `__init__.py` 或 control plane 直接公开。
3. `__init__.py -> runtime_infra.py -> local helper(s)` 可以存在，但不得演化成 `__init__.py -> new helper root -> runtime_infra shim` 的反向依赖。
4. `Phase 86` 只关闭当前两个 production targets 的 residual；不得顺手把 `Phase 87` assurance giants 或 `Phase 88` governance freeze 混入本 phase。

## Common Pitfalls

### Pitfall 1: 把 `runtime_infra.py` inward split 做成 second root

**What goes wrong:** 新 helper 文件变成真正的 outward import home，而 `runtime_infra.py` 退化成 compat shell。  
**How to avoid:** 所有 outward imports 继续锚定 `runtime_infra.py`，helper 只允许被 `runtime_infra.py` 本地使用。  
**Warning signs:** `__init__.py` / control modules 开始直接 import 新 helper。

### Pitfall 2: Share-client 只删方法，不收测试语义

**What goes wrong:** production 删除 bool/alias seam，但 tests 继续围绕 bool-only contract 断言，导致 residual debt 只是换了位置。  
**How to avoid:** 同 phase 把测试断言迁到 `OperationOutcome`，直接检查 typed semantics。  
**Warning signs:** 新增 adapter fixture，或测试通过 `is_success` 间接模拟旧 bool API。

### Pitfall 3: ledger 关闭先于真实代码完成

**What goes wrong:** `KILL_LIST` / `RESIDUAL_LEDGER` 被提前标 closed，但 production/tests 仍保留旧 seam。  
**How to avoid:** 让 `86-03` 依赖 `86-01` 与 `86-02`，closeout 只在代码与 focused verification 全部通过后发生。  
**Warning signs:** 文档措辞出现“should be gone / planned removal”，但仓库里符号仍在。

## Recommended Plan Decomposition

| Plan | Wave | Depends on | Scope | Output |
|------|------|------------|-------|--------|
| `86-01` anonymous-share compat seam deletion | Wave 1 | none | 删除 `_safe_read_json()` 与 bool `submit_share_payload()`；tests 完整迁到 outcome-native contract | `share_client.py` 更薄、share-client tests 不再承认 legacy shim |
| `86-02` runtime-infra inward split | Wave 1 | none | 拆出 listener/reload local helper，保留 `runtime_infra.py` formal home | 更薄的 `runtime_infra.py` + 更新后的 runtime meta guards |
| `86-03` review-ledger closeout | Wave 2 | `86-01`, `86-02` | 关闭 Phase 85 路由来的 delete gates / hotspot review entries | updated `RESIDUAL_LEDGER` / `KILL_LIST` / `FILE_MATRIX` / `V1_23_TERMINAL_AUDIT` |
| `86-04` route / baseline / follow-up freeze | Wave 3 | `86-03` | 冻结 current-route doc chain、baseline boundary docs 与 focused follow-up guards | updated current docs / baseline docs / governance helpers |

**Why this is optimal:** `86-01` 与 `86-02` 文件集基本独立，可并行推进；`86-03` 只做 review closeout；`86-04` 再冻结 current-route 与 baseline truth，既满足 Nyquist/closeout 要求，也避免单 plan 过胖。

## Minimal Sufficient Validation Checklist

- `uv run pytest -q tests/core/test_share_client_primitives.py tests/core/test_share_client_submit.py tests/core/test_share_client_refresh.py`
- `uv run pytest -q tests/core/test_runtime_infra.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init.py`
- `uv run pytest -q tests/meta/test_phase61_formal_home_budget_guards.py tests/meta/test_phase69_support_budget_guards.py tests/meta/test_phase70_governance_hotspot_guards.py tests/meta/test_phase72_runtime_bootstrap_route_guards.py tests/meta/dependency_guards_service_runtime.py tests/meta/test_phase85_terminal_audit_route_guards.py tests/meta/test_governance_route_handoff_smoke.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run python scripts/check_architecture_policy.py --check`

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest` via `uv run pytest` |
| Lint / static | `uv run ruff check .` |
| Governance checks | `uv run python scripts/check_file_matrix.py --check` + `uv run python scripts/check_architecture_policy.py --check` |
| Full regression fallback | `uv run pytest -q` |

### Requirement → Verification Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HOT-37 | compat shell 被真实删除，hotspot 继续 inward slimming，而非 route-next 漂移 | focused unit + meta | `uv run pytest -q tests/core/test_share_client_primitives.py tests/core/test_share_client_submit.py tests/core/test_runtime_infra.py tests/core/test_init_runtime_setup_entry.py` | ✅ |
| ARC-22 | formal roots / public surfaces / file-ownership truth 不被 helper 反客为主 | meta + scripts | `uv run pytest -q tests/meta/test_phase69_support_budget_guards.py tests/meta/test_phase72_runtime_bootstrap_route_guards.py tests/meta/dependency_guards_service_runtime.py tests/meta/test_phase85_terminal_audit_route_guards.py tests/meta/test_governance_route_handoff_smoke.py` + `uv run python scripts/check_file_matrix.py --check` | ✅ |

### Wave 0 Gaps

None — 当前 repo 已具备足够的 focused tests 与 meta/script guard infrastructure。缺的不是测试框架，而是把 residual 删除、helper inward split 与 governance closeout 在同一 phase 一次对齐。

## Sources

### Primary (HIGH confidence)

- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/86-production-residual-eradication-and-boundary-re-tightening/86-CONTEXT.md`
- `.planning/phases/86-production-residual-eradication-and-boundary-re-tightening/86-DISCUSSION-LOG.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/V1_23_TERMINAL_AUDIT.md`
- `custom_components/lipro/core/anonymous_share/share_client.py`
- `custom_components/lipro/core/anonymous_share/share_client_flows.py`
- `custom_components/lipro/core/anonymous_share/share_client_support.py`
- `custom_components/lipro/core/anonymous_share/share_client_submit.py`
- `custom_components/lipro/core/anonymous_share/share_client_refresh.py`
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/runtime_infra.py`
- `custom_components/lipro/control/entry_lifecycle_support.py`
- `custom_components/lipro/control/entry_root_wiring.py`
- `tests/core/test_share_client_primitives.py`
- `tests/core/test_share_client_submit.py`
- `tests/core/test_runtime_infra.py`
- `tests/core/test_init_runtime_setup_entry.py`
- `tests/meta/test_phase61_formal_home_budget_guards.py`
- `tests/meta/test_phase69_support_budget_guards.py`
- `tests/meta/test_phase70_governance_hotspot_guards.py`
- `tests/meta/test_phase72_runtime_bootstrap_route_guards.py`
- `tests/meta/dependency_guards_service_runtime.py`

## Metadata

**Confidence breakdown:**
- `ShareWorkerClient` residual boundary: HIGH — 使用面已经缩到 single-test alias + mostly-test bool shim。
- `runtime_infra` split strategy: HIGH — outward surface、import locality 与 budget evidence 都很明确。
- closeout artifact set: HIGH — `Phase 85` 已把目标 ledger/review entries 精确路由到 `Phase 86`。

**Research date:** 2026-03-27  
**Valid until:** `Phase 86` 执行完成或 active route 切换前（以先到者为准）
