# Dependency Matrix

**Purpose:** 定义允许/禁止的跨平面依赖方向，并作为 architecture guards 的语义真源。
**Status:** Baseline reference
**Updated:** 2026-03-14

## Formal Role

- 本文件定义 allowed / forbidden dependency direction 的 baseline truth。
- `.planning/baseline/ARCHITECTURE_POLICY.md` 把这些语义规则翻译成可执行的 rule ids 与 enforcement chain；两者必须同步演进，不能各写各的 seed 文案。

## Allowed Dependencies

| From | May Depend On | Why |
|------|----------------|-----|
| Entity / Platform | Domain, Runtime public surface, Control contracts | 实体与平台只消费稳定投影与服务面 |
| Services / Control surfaces | Runtime public surface, Domain, Assurance hooks | 控制面与服务面要经正式公开边界协作 |
| Runtime | Domain, Protocol canonical public surface (`LiproProtocolFacade` + canonical contracts), Assurance hooks | 运行面编排只消费统一协议根与归一化 contracts；不得直接依赖 `core/protocol/boundary/*` decoder internals |
| Protocol | protocol-local collaborators, transport, auth, codecs | 协议边界内部闭环恢复与归一化 |
| Assurance | All planes (read/observe only) | 用于测试、审计、CI 守卫 |

## Forbidden Dependencies

| From | Must Not Depend On | Why |
|------|--------------------|-----|
| Entity / Platform | raw protocol internals, `core/protocol/boundary/*`, MQTT client, REST transport | 破坏边界与测试隔离 |
| Control plane | protocol internals, `core/protocol/boundary/*`, runtime internals bypassing public surface | 容易形成 backdoor 与 split-root 回流；`control/` 只能通过正式 runtime/public surfaces 协作，且不得依赖 child façade roots |
| Domain | HA lifecycle, auth/retry/network recovery | 会污染领域真源 |
| Protocol | coordinator, entity, platform, diagnostics UI semantics | 协议层不应感知宿主上层语义 |
| Compat shell | 反向定义正式 public surface | compat 只能跟随，不可主导 |

## Architecture Policy Mapping

| Rule ID | Enforces | Notes |
|--------|----------|-------|
| `ENF-IMP-ENTITY-PROTOCOL-INTERNALS` | Entity / Platform 不直连 `core.api`、`core.mqtt`、`core.protocol.boundary` internals | 结构性 import 规则 |
| `ENF-IMP-CONTROL-NO-BYPASS` | Control surface 不直连 protocol internals 或 runtime internals bypass | 阻断 backdoor / split-root 回流 |
| `ENF-IMP-BOUNDARY-LOCALITY` | `core/protocol/boundary/*` 仅限 protocol-plane internal collaborators 合法消费 | future assurance-only 例外必须先登记 |

## Guard Chain

| Rule | Initial Enforcement | Full Enforcement Target |
|------|---------------------|--------------------------|
| Entity 不直连 protocol internals / boundary decoders | `scripts/check_architecture_policy.py` + `tests/meta/test_dependency_guards.py` | local-fast + CI fail-fast |
| Control 只走 runtime public surface | `scripts/check_architecture_policy.py` + `tests/meta/test_dependency_guards.py` | local-fast + CI fail-fast |
| Protocol 不依赖 coordinator/entity | import scan + reviewer checklist | future protocol/root checks |
| Compat 不成为 public truth | `ARCHITECTURE_POLICY.md` + public-surface guards | residual kill gate |
| Runtime/control 不直连 child façade roots | protocol/root contract tests + integration proof | stronger dependency guards |

## Phase 07.3 Observer-Only Telemetry Surface

- `custom_components/lipro/core/telemetry/*` 只允许 pull `ProtocolTelemetrySource` / `RuntimeTelemetrySource` ports、pure models 与 sink projections；不得反向依赖 `control/*`、`Coordinator` internals 或 child façade internals。
- `custom_components/lipro/control/telemetry_surface.py` 是 control-plane 唯一 bridge：可以装配 `RuntimeTelemetryExporter`，但 diagnostics / system-health consumers 不得绕过它回退到 runtime private fields。
- exporter family 属于 `observer-only surface`：允许读取正式 runtime / protocol telemetry truth，不得获得编排权、服务注册权或第二套事件总线语义。

## Phase 10 Control / Core Boundary Clarifications

- `custom_components/lipro/control/runtime_access.py` 是 control plane 读取 runtime-home `Coordinator` 的唯一 helper；`entry.runtime_data.coordinator` 不得在 adapter / control surface 中散落读取。
- `custom_components/lipro/control/telemetry_surface.py` 必须通过 `runtime_access.get_entry_runtime_coordinator()` 定位 runtime root；telemetry bridge 不能重新承担 runtime-home 叙事。
- `custom_components/lipro/config_flow.py`、`custom_components/lipro/entry_auth.py` 允许依赖 `LiproAuthManager` / `AuthSessionSnapshot` 这类 host-neutral contract；不允许依赖 raw login/result payload 或 boundary decoder internals。

## Review Checklist

- [ ] 新增依赖是否符合 allowed matrix
- [ ] 是否引入了新的跨平面 shortcut
- [ ] 是否把 compat 层误提升为正式 public surface
- [ ] 是否需要同步更新 `PUBLIC_SURFACES.md`、`ARCHITECTURE_POLICY.md` 与 `VERIFICATION_MATRIX.md`

---
*Used by: Phase 1.5 seed guards, Phase 7.2 architecture policy, and CI-level dependency enforcement*
