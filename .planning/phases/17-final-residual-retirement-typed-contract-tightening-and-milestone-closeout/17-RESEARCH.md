# Phase 17 Research

## Inputs

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/ARCHITECTURE_POLICY.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/v1.1-MILESTONE-AUDIT.md`
- focused repo scans + parallel read-only subagent audits

## Key Findings

### 1. `_ClientTransportMixin` is effectively dead residual

- `custom_components/lipro/core/api/client_transport.py` 中的 `_ClientTransportMixin` 仍然存在，但仓内已无生产或测试消费者。
- `LiproRestFacade` 早已直接装配 `TransportExecutor`，并自行暴露所需 transport-facing methods。
- 这类仅剩“定义 + 导出”的 compat shell 会制造旧 transport mixin 仍然有效的认知债。

**Implication:** 可低风险物理删除，并同步 residual / kill / public-surface wording。

### 2. `_ClientBase` and endpoint mixin family still carry legacy inheritance semantics

- `_ClientBase` 现在主要承担 endpoint collaborators 的 typing anchor，而 `LiproRestFacade` 本身已经是 explicit collaborator composition。
- `_EndpointAdapter` 已经能通过 facade public methods 工作，说明 `_ClientBase` 更适合被 protocol port 替代，而不是继续保留为 pseudo-base-class。
- `AuthEndpoints` / `DeviceEndpoints` / `CommandEndpoints` / `StatusEndpoints` / `MiscEndpoints` / `ScheduleEndpoints` 仍沿用 `_Client*Mixin` family，残留了 Phase 2 的 demixin 叙事。

**Implication:** 可在 `core/api/endpoints/*` 引入本地 `Protocol` port，收敛掉 `_ClientBase` 继承脊柱与 `_ClientEndpointPayloadsMixin` 叙事。

### 3. `entry_auth` fallback is now a narrow compatibility seam

- `persist_entry_tokens_if_changed()` 已优先读取 `auth_manager.get_auth_session()`；`get_auth_data()` 只在 session tokens 不可用时兜底。
- 仓内生产调用只剩这一处显式 fallback；保留它的主要原因是旧测试 doubles / mocks。

**Implication:** 若同步更新 tests/mocks 到 `AuthSessionSnapshot` 正式契约，可删除 fallback 分支并进一步 demote `get_auth_data()` 语义。

### 4. `power_service.py` still returns compatibility-shaped polymorphic payloads

- 当前 helper 会返回 `{}`、单个 mapping、或 `{"data": rows}`，这让 runtime 上游仍要理解 helper-level compatibility envelope。
- outlet-power runtime 已有归一化逻辑，说明 boundary 更适合输出显式 typed result，而不是再合成 magic wrapper。

**Implication:** 应把 outlet-power helper 契约改成显式 typed union / canonical result，去掉 `{"data": rows}` synthetic envelope，并同步 runtime/tests。

### 5. `LiproMqttClient` legacy name remains visible in production/test seams

- 生产代码里，`LiproMqttFacade` 仍直接 import / annotate / instantiate `LiproMqttClient`。
- 测试中还有大量 direct usage；其中 `tests/core/coordinator/runtime/test_mqtt_runtime.py` 与 `tests/integration/test_mqtt_coordinator_integration.py` 属于非 transport-focused tests，更适合改到 protocol contract / fake transport。
- `ENF-IMP-MQTT-TRANSPORT-LOCALITY` 已存在于治理基线，但 pytest 层缺少 focused explicit guard。

**Implication:** Phase 17 最小步宜采用“canonical transport name + legacy alias”策略，先把生产与非 transport 测试迁到 canonical naming / contract，再补 focused guard，不强行做高风险彻底删除。

## Recommended Phase 17 Scope

### Plan 17-01
- 删除 `_ClientTransportMixin`
- 以 local `Protocol` 替代 `_ClientBase` / `_ClientEndpointPayloadsMixin`
- 让 endpoint collaborators 仅保留 explicit composition story

### Plan 17-02
- 删除 `entry_auth` 中的 `get_auth_data()` fallback
- 统一 tests/mocks 到 `AuthSessionSnapshot`
- 显式化 outlet-power helper 返回契约，去掉 `{"data": rows}` compat envelope

### Plan 17-03
- 引入 canonical MQTT transport naming（保留 legacy alias 仅作 local compatibility）
- 让 production code / non-transport tests 优先依赖 protocol contract / canonical name
- 增加 focused meta guard 锁定 locality

### Plan 17-04
- 回写 `ROADMAP` / `REQUIREMENTS` / `STATE` / baseline / reviews / docs
- 生成 `VERIFICATION` / `VALIDATION`
- 做 final repo audit：`ruff` / `mypy` / `pytest -q` + residual pattern recount

## Risks

- `_ClientBase` → protocol port 的改写会影响 endpoint helper tests，需要以 focused API regression 保护。
- outlet-power helper 契约收口需要与 runtime 归一化协同修改，否则可能破坏 multi-row / invalid-shape 边界测试。
- MQTT naming 不适合在本 phase 做无 alias 的彻底删除，否则会引入大量低价值 churn。

## Validation Matrix

- API spine cleanup: `uv run pytest tests/core/api/test_api.py tests/core/api/test_helper_modules.py -q`
- auth + init contract: `uv run pytest tests/core/test_init.py tests/core/test_auth.py -q`
- MQTT locality: `uv run pytest tests/core/mqtt tests/core/coordinator/runtime/test_mqtt_runtime.py tests/integration/test_mqtt_coordinator_integration.py tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py -q`
- full closeout: `uv run ruff check . && uv run mypy && uv run pytest -q`
