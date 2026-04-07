# Phase 18 Context

**Phase:** `18 Host-Neutral Boundary Nucleus Extraction`
**Milestone:** `v1.2 Host-Neutral Core & Replay Completion` (draft)
**Date:** 2026-03-16
**Status:** Ready for planning
**Source:** roadmap draft + v1.2 milestone draft + Phase 10/17 follow-through review

## Why Phase 18 Exists

`Phase 10` 已把 host-neutral auth/result contracts 与 HA adapter decoupling 推到“边界已对、物理未完全收口”的状态；`Phase 17` 又完成了 residual spine、legacy transport naming 与 helper-level compat envelope 的 final closeout。当前真正剩下的，不再是旧壳清理，而是 **把已经成熟的 boundary/auth/device nucleus 从 HA adapter 语义里继续抽出来**，同时保持单一正式主链不分裂。

最近复查显示，仍有几类 shared-core debt 处在“语义已接近 host-neutral、但物理 home 仍夹带宿主叙事”的状态：

1. `custom_components/lipro/flow/login.py` 的 `LoginResult` 继续在 HA flow 层投影 formal auth session/login result；
2. `custom_components/lipro/config_flow.py` 与 `custom_components/lipro/entry_auth.py` 仍分别持有一部分可复用 auth/bootstrap 逻辑，adapter seam 还不够显式；
3. `custom_components/lipro/core/capability/registry.py`、`custom_components/lipro/core/capability/models.py`、`custom_components/lipro/core/device/device_views.py` 仍把 `DeviceCategory -> Home Assistant platform strings` 的映射保留在 core/device capability truth 中；
4. 当前 architecture guards 已能阻断 boundary locality / control bypass / MQTT transport backflow，但还没有专门的 host-neutral nucleus locality 守卫，无法阻止 `homeassistant` imports 或 HA-only platform projection 再回流到新 nucleus homes。

本 phase 的目标不是“创建第二个 shared SDK / CLI root”，而是把这些已成熟的 nucleus 物理归位、把 adapter seam 说清楚，并用守卫锁住，给 `Phase 19` 的 headless proof 准备稳定底座。

## Goal

1. 明确并提炼 boundary/auth/device 方向的 host-neutral contracts 与 adapter seams，使可复用 truth 不再依赖 `ConfigEntry`、`HomeAssistant`、`entry.runtime_data` 或 HA platform naming；
2. 把已成熟的 auth/device/shared helpers 收口到合适的 nucleus home，但不改变 `LiproProtocolFacade` / `Coordinator` 的正式根身份；
3. 增加 locality / dependency / regression guards，阻止 HA-specific imports、platform projections 或 adapter-only assumptions 回流到 nucleus；
4. 明确本 phase 与 `Phase 19/20/21/22` 的边界：本 phase 只抽 nucleus 与 adapter seam，不偷跑 headless root、剩余 replay family 完成或 broad-catch 全量 hardening。

## Decisions (Locked)

- **单一主链不变**：`LiproProtocolFacade` 仍是唯一正式 protocol root，`Coordinator` 仍是唯一正式 runtime orchestration root。
- **抽 helper / contract，不抽第二 root**：允许提炼 host-neutral helper、typed contract、projection seam、adapter bootstrap；不允许创建 parallel runtime story、parallel CLI root 或 framework-style shared core。
- **adapter-only 语义必须留在 adapter**：`ConfigEntry` / `HomeAssistant` / service registration / platform strings / entity exposure 仍属于 HA adapter 或 adapter projection layer，不再混入 host-neutral nucleus。
- **device 真源优先于平台投影**：device/capability nucleus 只能表达 device/domain truth；HA platform projection 必须被视为 host adapter concern，而不是 core capability truth 的一部分。
- **本 phase 不做 headless proof**：`CORE-02` 明确 defer 到 `Phase 19`；本 phase 只为它铺路，不实现 CLI/headless composition root。
- **文档与守卫同步**：context/research/plans、dependency/public-surface baseline、architecture policy、reviews 与 focused tests 必须同轮同步规划。

## Non-Negotiable Constraints

- 不得创建第二个 runtime root、第二套 protocol façade 或第二条合法 boot story；
- 不得让 `core/protocol`、`core/auth`、`core/device` 新增 `homeassistant` 依赖；
- 不得把 `DeviceCategory -> platform` 这类 HA-only projection 继续登记为 host-neutral truth；
- 不得把 `config_flow` / `entry_auth` / control adapters 重新写回 raw response dict / vendor envelope 依赖；
- 不得把 `Phase 20` 的 boundary-family formalization、`Phase 21` 的 exception hardening、`Phase 22` 的 full governance closeout 提前塞进本 phase。

## Specific Concerns To Address

- `flow/login.py` 的 `LoginResult`、`config_flow.py` 的 `_async_do_login()` / `_async_try_login()` 与 `entry_auth.py` 的 `build_entry_auth_context()` / token persistence 中，哪些部分应成为 host-neutral auth/bootstrap contract，哪些必须继续留在 HA adapter；
- `core/capability/models.py`、`core/capability/registry.py`、`core/device/device_views.py` 与 `const/categories.py` 之间，哪些 currently encode Home Assistant platform semantics，应如何拆成 device-kind truth vs host projection seam；
- `core/device` / `core/auth` / `core/protocol` 中哪些 homes 可以成为 nucleus，且不会让 future host 误以为这里已经是 second root；
- 需要新增哪些 architecture policy / dependency guard / focused regression tests，才能保证 host-neutral nucleus 不再回流 `homeassistant` imports、HA platform strings 与 adapter-only helpers；
- 哪些文档真源需要更新 wording，明确 “host-neutral nucleus” 是 formal helper/contract family，而不是新的 public root。

## Deferred Ideas

- 正式 CLI / headless consumer proof（留到 `Phase 19`）；
- remaining replay/boundary family completion（留到 `Phase 20`）；
- broad-catch / diagnostics failure classification 全量 hardening（留到 `Phase 21`）；
- v1.2 governance/release closeout（留到 `Phase 22`）；
- physical package split / cross-platform SDK release / monorepo shared library。
