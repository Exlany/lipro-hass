# Phase 73 Context

## Phase

- **Number:** `73`
- **Title:** `Service-family deduplication, diagnostics/helper convergence, and runtime-surface formalization`
- **Milestone:** `v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement`
- **Starting baseline:** `v1.20 active / Phase 72 complete`
- **Archived reference:** `v1.19 archived / evidence-ready`

## Why This Phase Exists

`Phase 72` 已把 runtime bootstrap、entry lifecycle、runtime-access probe retirement 与 current-route truth 收口到当前正式主链，但 active route 仍保留几类更贴近 control/runtime formalization 的热点：

- `service_router` / `services/*` forwarding family 仍有重复转发与旁路协议调用
- diagnostics / telemetry / helper 家族仍存在 helper/support duplication 与认知噪音
- `LiproEntity` / platform helper 仍直接依赖 live runtime 结构，缺少更诚实的 runtime read surface
- `schedule.py` 已切到 `coordinator.schedule_service` 正式链路，但 guard / 命名 / focused evidence 仍需同步冻结

## Additional Audit Drivers

本轮全仓审视补充了以下高优先级输入，Phase 73 规划必须显式吸收：

- `custom_components/lipro/services/schedule.py` 已建立正式 runtime schedule 链路；本 phase 要冻结既有 `schedule_service` truth，而不是重造新 facade。
- `custom_components/lipro/helpers/platform.py` 与 entity runtime strategy 需要收口到 runtime-owned typed contract，并禁止回流到 raw `.devices` / `control/runtime_access.py`。
- `custom_components/lipro/control/runtime_access*` outward home 已成立，但 view/facts/support 结构仍偏绕，需要进一步降低 surface 认知成本。
- diagnostics / telemetry / helper family 要维持单一 outward home，避免 support/helper 语义继续散落。

## In Scope

- `custom_components/lipro/control/service_router.py`
- `custom_components/lipro/control/service_router_handlers.py`
- `custom_components/lipro/control/service_router_support.py`
- `custom_components/lipro/services/schedule.py`
- `custom_components/lipro/diagnostics.py`
- `custom_components/lipro/system_health.py`
- `custom_components/lipro/control/diagnostics_surface.py`
- `custom_components/lipro/control/telemetry_surface.py`
- `custom_components/lipro/control/runtime_access.py`
- `custom_components/lipro/control/runtime_access_support_*`
- `custom_components/lipro/helpers/platform.py`
- `custom_components/lipro/entities/base.py`
- touched `tests/core/**`, `tests/services/**`, `tests/platforms/**`, `tests/meta/**`
- current mutable governance docs only when topology / truth changes

## Constraints

- 不新增第二条正式主链；所有收敛必须回到既有 formal homes
- root HA adapters 继续保持 thin adapter，不把正式 ownership 长回根层
- compat / helper residual 若暂存，必须局部、可计数、可删除，不得伪装成长期架构
- 所有 Python / test / script 命令统一 `uv run ...`
- 方案应优先“彻底回收热点”而不是临时缝补；若无法同轮完成，必须给出明确 delete gate 与后续 owner
