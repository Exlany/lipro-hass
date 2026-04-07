# Phase 11 Research

## Research Question

在 `11-01 ~ 11-03` 已完成 control-router formalization 的基础上，如何把本轮全仓复审剩余问题继续纳入 `Phase 11`，形成一组可执行、可验证、可并行的 addendum plans，而不重新引入第二条主链？

## Already Resolved In Phase 11 Wave 1

- `custom_components/lipro/control/service_router.py` 已接管真实 HA service routing implementation。
- `custom_components/lipro/services/wiring.py` 已降为显式 compat re-export shell。
- tests 已切到 `control.service_router` formal seam。
- control-plane 命名、formal surface、baseline / residual / kill-gate / verification 已完成一轮回写。

## Remaining Accepted Problem Families

### 1. Protocol / Runtime Surface Residuals

- `custom_components/lipro/core/api/client.py` 的 REST child façade 仍通过 `_endpoint_exports` + `__getattr__` / `__dir__` 扩面。
- `custom_components/lipro/core/coordinator/runtime/device/snapshot.py` 仍保留 `get_device_list()` compat fallback。
- `custom_components/lipro/core/coordinator/orchestrator.py` 仍探测 `self.client.status.query_device_status` ghost child surface。
- `custom_components/lipro/runtime_types.py` 仍是 concrete alias，而不是窄 public protocol。

### 2. Runtime / Control Hardening Gaps

- `runtime_data` 读取仍散落在 `control/` 与 `services/**`，`runtime_access.py` 尚未真正成为唯一 locator home。
- debug-mode gating 与 coordinator→entry 反查逻辑存在重复。
- `control/diagnostics_surface.py` 对 malformed runtime / share-manager 的鲁棒性不一致。
- `core/coordinator/runtime/status/executor.py` 缺少单设备级错误隔离。

### 3. Entity / Platform Modeling Gaps

- `switch.py` 的 `hasattr()` 弱判定导致 supplemental switch 暴露存在误建模风险。
- supplemental entity rules 分散在多个平台文件，没有单一领域真源。
- `select.py` 仍存在 sibling 同步直戳 `coordinator.async_update_listeners()` 的平台特例。
- 未知枚举被静默回退默认值，掩盖协议漂移。
- `entities/firmware_update.py` 仍职责过载。

### 4. Governance / Open-Source Maturity Gaps

- `docs/README.md` 与 `AGENTS.md` 对 `.planning/phases/**` 的资产身份冲突。
- release workflow 未复用 CI / governance / version-sync。
- issue template 的 HA 版本、`CONTRIBUTING.md` / PR 模板 / CI benchmark 契约不一致。
- `tests/meta/test_governance_guards.py` 仍有较多文本脆弱断言。
- 缺少 `SECURITY.md` 与私密 disclosure 通道。

## Recommended Direction

### A. Keep Phase 11 as an addendum container, not a brand-new phase

推荐保留 `Phase 11` 编号与目录，不推翻已执行的 `11-01 ~ 11-03`，而是通过 `11-04+` addendum plans 继续扩展。

理由：
- 已执行子成果与其验证资产仍有效；
- 契约者要求“把这些问题全部完善进去”，而不是切去下一 phase；
- 追加 plans 比重写既有 phase 历史更可审计。

### B. Split remaining work into five buckets

#### 11-04 Protocol / Runtime Formal Surface Convergence
聚焦 dynamic REST child surface、ghost child surface、runtime compat fallback 与相关 tests/guards。

#### 11-05 Runtime Access / Diagnostics / Error Isolation Hardening
聚焦 `runtime_access` 单一 locator、debug-mode / entry lookup 去重、diagnostics robustness、status executor 单设备隔离、runtime public typing。

#### 11-06 Entity / Platform Truth Convergence
聚焦 supplemental entity rules 单一真源、`switch.py` 误暴露、unknown-enum 策略、平台特例写侧收口。

#### 11-07 Firmware Update Hotspot Slimming
聚焦 `entities/firmware_update.py` 的职责拆分，把 OTA candidate / cache / confirmation / arbitration 进一步外移到 formal helper cluster。

#### 11-08 Governance / Release / Open-Source Coherence
聚焦 phase-asset truth、release gate、issue template/version drift、benchmark contract、governance guard brittleness、`SECURITY.md`。

### C. Prefer explicit contracts over new wrappers

本轮不应再新增大而泛化的 adapter / facade；应优先：
- 删除 dynamic surface / compat fallback；
- 提升 formal contract / protocol / rule registry；
- 用 guard/tests 锁死新事实。

## Suggested Requirement Expansion

- `SURF-01`: protocol/runtime 剩余动态 surface、ghost surface 与 compat fallback 必须收口到显式 formal contract。
- `CTRL-04`: runtime locator、debug-mode gating、diagnostics robustness 必须收口到 control/runtime formal home。
- `RUN-01`: runtime public typing 必须窄化；status executor 必须隔离单设备失败。
- `ENT-01`: supplemental entity rules 必须收口到单一领域真源，并修复 `hasattr()`/unknown-enum 等误建模。
- `ENT-02`: firmware update 热点必须拆薄，实体只保留平台投影职责。
- `GOV-08`: governance / docs / release / template / security truth 必须一致，guards 尽量结构化。

## Dependency Order

1. `11-04` 先做 formal surface convergence，避免后续 runtime/entity/governance 基于错误 surface 继续加固。
2. `11-05` 在 formal surface 后收口 runtime locator / diagnostics / error isolation。
3. `11-06` 与 `11-07` 可并行：前者聚焦 platform rule truth，后者聚焦 firmware hotspot。
4. `11-08` 最后统一治理、CI、release、docs、security 与 meta guards。

## Verification Strategy

- `11-04`: `uv run pytest tests/core/api tests/core/coordinator/runtime/test_device_runtime.py tests/core/test_coordinator_integration.py tests/meta/test_public_surface_guards.py -q`
- `11-05`: `uv run pytest tests/core/coordinator/runtime/test_status_runtime.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/core/test_control_plane.py tests/meta/test_dependency_guards.py -q`
- `11-06`: `uv run pytest tests/platforms/test_switch.py tests/platforms/test_select.py tests/platforms/test_platform_entities_behavior.py tests/entities/test_descriptors.py -q`
- `11-07`: `uv run pytest tests/core/ota tests/update* tests/platforms/test_update.py -q`（按仓库实际文件调整）
- `11-08`: `uv run pytest tests/meta/test_governance_guards.py tests/meta/test_version_sync.py -q` + 相关 workflow/schema smoke
- Closeout: `uv run ruff check .` + `uv run mypy` + `uv run pytest tests -q`

## Decision

采用“**保留 Phase 11 编号与已完成子成果，追加 11-04 ~ 11-08 addendum plans**”方案。这最符合契约者要求，也最利于维持 planning truth 与 execution truth 的连续性。
