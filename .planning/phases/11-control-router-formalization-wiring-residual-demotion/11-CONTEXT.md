# Phase 11 Context

**Phase:** `11 Control Router Formalization & Wiring Residual Demotion`
**Milestone:** `v1.1 Protocol Fidelity & Operability`
**Date:** 2026-03-14
**Status:** Reopened for expanded planning
**Source:** Roadmap + Requirements + Phase 11 executed subset + full-repo re-audit + user directive

## User / Product Context

- 契约者要求把本轮全仓复审暴露的问题**全部纳入** `Phase 11` 规划，而不是散落成口头技术债。
- 契约者明确裁决：**不要为了照顾测试而继续让插件代码保留兼容冗余**；同理，也不要为了维持历史叙事而把治理/CI/文档冲突留到“以后再说”。
- 因此前述已完成的 `11-01 ~ 11-03` 只视作 `Phase 11` 的第一波落地；当前要把剩余 residual / surface / governance / open-source maturity gaps 正式编织进同一 phase 的 addendum plans。

## What Is Already Done

- `custom_components/lipro/control/service_router.py` 已成为真实 control-plane router implementation home。
- `custom_components/lipro/services/wiring.py` 已降为显式 compat re-export shell。
- 仓库 tests 已切到 `control.service_router` formal seam。
- control-plane 命名、baseline、residual、kill-gate 与 verification docs 已完成一轮同步。

## Accepted Audit Expansion Inputs

### A. Protocol / Runtime Surface Residuals

- `custom_components/lipro/core/api/client.py` 的 `LiproRestFacade` 仍通过 `_endpoint_exports` + `__getattr__` / `__dir__` 做隐式 surface 扩面，REST child façade 不能被静态枚举。
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` 仍在正式刷新链路中保留 `get_device_list()` compat fallback。
- `custom_components/lipro/core/coordinator/orchestrator.py` 仍探测 `self.client.status.query_device_status` 这种 ghost child surface，而不是只依赖 formal protocol contract。
- `custom_components/lipro/runtime_types.py` 仍以 concrete `Coordinator` alias 暴露 runtime typing，而不是窄 public protocol。

### B. Runtime / Control Hardening Gaps

- `runtime_data` 读取仍散落在 `control/` 与 `services/**`，没有真正统一到 `control/runtime_access.py`。
- debug-mode gating、coordinator→entry 反查逻辑仍存在多处重复实现。
- `control/diagnostics_surface.py` 对 malformed runtime / malformed share-manager 的鲁棒性弱于 `runtime_access` 路径。
- `core/coordinator/runtime/status/executor.py` 缺少单设备级错误隔离，一次 apply 失败可污染整批状态处理。

### C. Entity / Platform Modeling Gaps

- `custom_components/lipro/switch.py` 仍通过 `hasattr()` 等弱判定构造 supplemental switches，存在 plain light / panel entity 误暴露风险。
- supplemental entity 暴露规则分散在 `switch.py` / `sensor.py` / `select.py` / `update.py`，没有统一领域真源。
- `select.py` 仍有 sibling 同步直戳 `coordinator.async_update_listeners()` 的平台特例。
- 多处未知供应商枚举被静默回退为默认 UI 值，掩盖协议漂移。
- `entities/firmware_update.py` 仍承担 OTA 查询、共享缓存、manifest 仲裁、确认逻辑与错误观测等过多职责，是明确的大文件热点。

### D. Governance / Open-Source Maturity Gaps

- `docs/README.md` 与 `AGENTS.md` 对 `.planning/phases/**` 的 Git/证据身份仍存在冲突叙事。
- release workflow 未复用 CI / governance / version-sync 门禁，存在发版旁路。
- issue template 的 HA 版本下限、`CONTRIBUTING.md` / PR 模板 / CI 关于 benchmarks 的契约仍不一致。
- `tests/meta/test_governance_guards.py` 仍有大量文本级脆弱断言，需要继续降到结构级校验。
- 缺少 `SECURITY.md` / 私密漏洞披露入口；开源成熟度尚未闭环。

## Expanded Phase Goal

在已完成的 control-router formalization 基础上，把本轮全仓复审中仍未关闭的 residual/gov/open-source maturity gaps 正式纳入 `Phase 11`：

1. 收口 protocol/runtime 剩余隐式 surface 与 compat fallback；
2. 收口 control/runtime access、error isolation 与 diagnostics robustness；
3. 收口 entities/platform 的 supplemental rule truth、unknown-enum 策略与超载热点；
4. 收口 governance / release / contributor-facing truth 的冲突与脆弱性。

## Locked Decisions

### Surface and Contract Policy
- `LiproProtocolFacade` / formal child façades / runtime public surface 必须继续收敛到显式、可枚举、可守卫的 contract。
- 不允许继续保留 ghost child surface、dynamic export surface 或 runtime self-hosted compat fallback 作为“可接受长期状态”。

### Runtime Access Policy
- control plane 与服务面涉及 runtime locator 的读取必须收敛到 `control/runtime_access.py` 或其正式衍生 contract。
- diagnostics / system health / services 若需要额外 locator/helper，应优先沉到同一 formal home，而不是继续横向复制。

### Domain / Platform Policy
- supplemental entity 暴露规则必须有单一领域真源；平台文件只能消费规则，不再各自写第二套事实。
- 未知供应商枚举不应再静默坍缩为默认 UI 值；必须提供可观测、可诊断、可回归的策略。

### Governance Policy
- `.planning/*`、`docs/*`、`.github/*`、templates、CI/release/workflow 必须形成单一对外叙事，不允许“开发文档一套、CI 一套、发布一套”。
- 开源项目最低成熟度要求：版本支持口径一致、漏洞披露路径明确、发布复用验证门禁、治理 guards 尽量结构化。

## Planning Expectations

- 新增 plans 不应推翻已完成的 `11-01 ~ 11-03`；而应以 addendum wave 的方式继续展开。
- plans 应至少分成：
  1. protocol/runtime formal surface convergence
  2. runtime access + diagnostics + error isolation hardening
  3. entity/platform truth convergence
  4. firmware update hotspot slimming（若不并入上一项）
  5. governance / release / open-source coherence
- 每个 plan 必须列明：文件范围、要消灭的 residual、验证矩阵、与已完成 control-router 子成果的依赖关系。

## Deferred But Still Out of Scope

- 不在本 addendum 内引入全新技术栈或重型依赖。
- 不把 future host/shared-core 物理抽离提升为当前里程碑目标。
- 不做无边界的大规模 UI/feature 扩张。

---

*Phase: 11-control-router-formalization-wiring-residual-demotion*
*Context updated: 2026-03-14 after repo-wide audit expansion acceptance*
