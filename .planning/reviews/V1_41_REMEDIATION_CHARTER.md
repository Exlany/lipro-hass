# V1.41 Remediation Charter

**Purpose:** `把 terminal audit 识别出的残留问题按 severity / priority / formal home / acceptance / delete gate / verification 分流为后续可执行 workstreams。`

## Workstreams

### WS-01 Mega-Facade Slimming
- **Severity:** `High`
- **Priority:** `P1`
- **Formal home:** `custom_components/lipro/core/api/rest_facade.py`, `custom_components/lipro/core/protocol/facade.py`
- **Targets:** `rest_facade` manual delegation wall、protocol child-facade rebinding seams
- **Goal:** 降低 manual rebinding wall，提升 discoverability 与 ownership clarity。
- **Acceptance:** outward import home 不变；delegation count 降低；runtime/protocol focused tests 不退化。
- **Delete gate:** 旧 delegation shell 不再承担新的业务入口；不得引入第二条 public import chain。
- **Verification:** `uv run pytest -q tests/core/api/test_protocol_contract_facade_runtime.py tests/core/protocol/test_facade.py tests/meta/test_public_surface_guards.py`

### WS-02 Auth Hotspot Decomposition
- **Severity:** `High`
- **Priority:** `P1`
- **Formal home:** `custom_components/lipro/core/auth/manager.py` 与相关 auth/runtime collaborators
- **Targets:** credential seed、token lifecycle、adaptive expiry、refresh coordination、re-login fallback
- **Goal:** 把 auth manager 从过厚单类拆回更清晰的职责簇。
- **Acceptance:** refresh/login/relogin/ensure-valid contract 不变；并发 dedupe 继续稳定。
- **Delete gate:** manager 不再继续吸纳新的 unrelated auth policy；新增行为必须挂到显式 collaborator。
- **Verification:** `uv run pytest -q tests/core/test_auth.py tests/core/coordinator/test_update_flow.py tests/core/test_coordinator_integration.py`

### WS-03 Device Facade Surface Rationalization
- **Severity:** `Medium`
- **Priority:** `P2`
- **Formal home:** `custom_components/lipro/core/device/device.py`, `device_views.py`, `state.py`, `extras.py`
- **Targets:** relay-wall 规模、view/port 切分、outward property taxonomy
- **Goal:** 明确哪些 outward properties 必须保留，哪些应下沉到 focused views/ports。
- **Acceptance:** entity/platform outward contract 不破；IDE/type discoverability 提升；新增 relay 禁止继续无节制膨胀。
- **Delete gate:** 旧 relay 仅在 formal migration 完成后才可移除，不允许破坏 outward compatibility。
- **Verification:** `uv run pytest -q tests/core/device/test_device.py tests/meta/test_public_surface_guards.py`

### WS-04 Typed Command Grammar
- **Severity:** `Medium`
- **Priority:** `P2`
- **Formal home:** `custom_components/lipro/core/command/dispatch.py` 与 runtime command collaborators
- **Targets:** stringly route grammar、command normalization、panel/group fallback semantics
- **Goal:** 从 stringly route / prefix 规则继续推进到 typed command intent grammar。
- **Acceptance:** group fallback / panel routing / post-refresh contract 继续稳定；focused command/runtime tests 通过。
- **Delete gate:** 旧 string parsing 只能作为 migration shim，不能继续扩写新命令族。
- **Verification:** `uv run pytest -q tests/core/test_command_result.py tests/core/test_share_client_submit.py tests/core/test_coordinator_integration.py`

### WS-05 Governance Derivation Cost Reduction
- **Severity:** `Medium`
- **Priority:** `P2`
- **Formal home:** `.planning/baseline/*`, `.planning/reviews/*`, `tests/meta/*`
- **Targets:** current-route docs、promoted-phase assets、verification baseline、archive history / current-truth helpers
- **Goal:** 降低 current-route / promoted-phase / file-matrix 手工同步成本。
- **Acceptance:** current selector family 与 tests/meta 继续 machine-readable；不得引入第二 authority chain。
- **Delete gate:** 任何自动化都不能削弱 baseline docs 的 formal authority，也不能把派生文件升格为新真源。
- **Verification:** `uv run pytest -q tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_governance_release_contract.py tests/meta/test_phase140_governance_source_freshness_guards.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/toolchain_truth_testing_governance.py`

### WS-06 Observability & Log-Safety Follow-Up
- **Severity:** `Medium`
- **Priority:** `P2`
- **Formal home:** `custom_components/lipro/core/api/status_service.py`, selected runtime/service logging call sites
- **Targets:** API-failure semantics、empty-map ambiguity、log-safety consistency、service/runtime error observability
- **Goal:** 明确区分“真实离线”与“查询失败”，并继续收敛剩余日志策略漂移。
- **Acceptance:** outward service/runtime contract 清晰；日志不泄露敏感信息；调用侧可区分 failure vs empty-state。
- **Delete gate:** 不允许再新增 raw vendor error 直接穿透到 user-facing semantics。
- **Verification:** `uv run pytest -q tests/core/api/test_api_status_service_fallback.py tests/core/test_log_safety.py tests/meta/test_dependency_guards.py`

## Explicit Non-Goals For Phase 136

- 不宣称“一次执行后永久无残留”。
- 不把已归档 `v1.40` 重新改写成 active story。
- 不在没有 focused proof 的情况下大面积重写 runtime/protocol 主链。
- 不为了降低治理维护成本而削弱 baseline / registry / meta-guard 的 formal authority。
