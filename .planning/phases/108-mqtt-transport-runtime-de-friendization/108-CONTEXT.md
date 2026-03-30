# Phase 108: MQTT transport-runtime de-friendization - Context

**Gathered:** 2026-03-30
**Status:** Executed / governance projected
**Source:** `v1.30` active route continuation from `.planning/MILESTONE-CONTEXT.md` + `108-RESEARCH.md`

<domain>
## Phase Boundary

本 phase 只处理 `core/mqtt` 的 transport/runtime 边界收口：

- 把 `custom_components/lipro/core/mqtt/transport_runtime.py` 从 whole-owner friend-style reach-through 改成显式 owner/state contract。
- 保持 `MqttTransport` 为唯一 concrete transport root，不新增 second root、package export 或 public backdoor。
- 通过 focused MQTT regressions 冻结 transport-facing message/connect entrypoint patchability 与 collaborator replacement visibility。
- 把 `Phase 108 complete` 投射回 planning/baseline/review/docs truth、focused guards 与 GSD fast-path。

不在本 phase 重开 anonymous-share manager 或 runtime snapshot surgery；这些 scope 已显式路由到 `Phase 109 -> 110`。
</domain>

<decisions>
## Locked Decisions

- `MqttTransport` 继续保持 localized concrete transport 身份；runtime helper 只允许 inward split，不能升级为新 root。
- `MqttTransportRuntime` 只能消费显式 `owner/state` contract 与 transport-facing entrypoint provider，不再直接摸一整个 transport owner 的私有字段。
- `connection_manager.py`、`subscription_manager.py` 与 `message_processor.py` 继续保持 focused collaborator 身份，不把 runtime state 倒灌回它们。
- `Phase 108` 完成后，current route 必须前推到 `v1.30 active route / Phase 108 complete / latest archived baseline = v1.29`，默认下一步是 `$gsd-discuss-phase 109`。
</decisions>

<canonical_refs>
## Canonical References

- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `custom_components/lipro/core/mqtt/transport.py`
- `custom_components/lipro/core/mqtt/transport_runtime.py`
- `custom_components/lipro/core/mqtt/connection_manager.py`
- `custom_components/lipro/core/mqtt/subscription_manager.py`
- `tests/core/mqtt/test_transport_refactored.py`
- `tests/core/mqtt/test_transport_runtime_connection_loop.py`
- `tests/core/mqtt/test_transport_runtime_lifecycle.py`
- `tests/core/mqtt/test_transport_runtime_ingress.py`
- `tests/core/mqtt/test_transport_runtime_subscriptions.py`
- `tests/core/mqtt/test_connection_manager.py`
</canonical_refs>
