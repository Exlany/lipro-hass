# Phase 43: Control-services boundary decoupling and typed runtime access - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning
**Source:** `v1.6` roadmap after `Phase 42 complete`

<domain>
## Phase Boundary

本 phase 只处理三类 `v1.6` 的 control/runtime 边界尾债：

1. `control/` 与 `services/` 仍存在 helper 反向渗透、formal ownership 不够薄、调用方向不够稳定的问题；
2. `RuntimeAccess` 仍承担过多反射式/宽类型读模型职责，消费者仍可能依赖私有字段形状或测试 patch 约定；
3. `services/maintenance.py` 仍承载 entry reload / listener / coordinator traversal 等 runtime infra，formal home 尚未收拢。

本 phase 不处理 `.planning/phases/**` 降噪与术语清理，也不拆 `rest_decoder_support.py` / `diagnostics_api_service.py` / `share_client.py` / `message_processor.py` 等热点；这些分别留给 `Phase 44` 与 `Phase 45`。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `custom_components/lipro/control/` 继续是 formal control-plane home；`services/` 只能保留 service declarations / adapter helpers 身份，不得重新长成第二 control root。
- `RuntimeAccess` 必须继续是 control → runtime 的唯一正式读模型入口，但要收窄成 typed public contract，避免反射、`MagicMock` 形状或私有字段依赖继续合法化。
- runtime infra 必须各回 formal home；`services/maintenance.py` 不得继续承担 entry reload、listener wiring、coordinator traversal 或 runtime lifecycle ownership。
- 任何解耦必须沿现有正式 seams 收口，不得新增 root / bus / DI 故事线，也不得扩张 public surface。
- phase 交付必须同步治理与测试真相：architecture docs、review ledgers、meta guards 与 focused service/runtime tests 要讲同一条边界故事。

### Claude's Discretion
- typed runtime read-model 使用 dataclass / Protocol / typed mapping 的具体形状；
- runtime infra 最终落在 `control/entry_lifecycle_controller.py`、`control/runtime_access.py`、`custom_components/lipro/runtime_infra.py` 或其他现有正式 home 的具体切分；
- 计划拆分是按 boundary inventory、typed runtime access、maintenance relocation 三块，还是补一块 docs/guards hardening。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / active truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 北极星终态与禁止项
- `docs/developer_architecture.md` — control/services/runtime 当前正式拓扑与边界说明
- `AGENTS.md` — authority 顺序、formal home、phase trace/promote contract
- `.planning/PROJECT.md` — 当前 `v1.6` milestone truth
- `.planning/ROADMAP.md` — `Phase 43` 正式路线与 success criteria
- `.planning/REQUIREMENTS.md` — `ARC-04 / CTRL-10 / RUN-07` 真源
- `.planning/STATE.md` — 当前 execution status / next-command truth
- `.planning/phases/42-delivery-trust-gates-and-validation-hardening/42-SUMMARY.md` — 上一 phase 已完成治理/交付门禁的落地状态
- `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-SUMMARY.md` — `RuntimeAccess` / shared execution 近期收口结果
- `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-VERIFICATION.md` — 当前 runtime-access / execution 正式合同证据

### Control / runtime files
- `custom_components/lipro/control/runtime_access.py` — 当前 runtime read-model home
- `custom_components/lipro/control/service_router.py` — public callback home
- `custom_components/lipro/control/service_router_handlers.py` — service handler wiring 与 request shaping 聚合点
- `custom_components/lipro/control/service_router_support.py` — support helpers / service router side support
- `custom_components/lipro/control/entry_lifecycle_controller.py` — entry lifecycle / reload / listener orchestration 正式 home
- `custom_components/lipro/control/diagnostics_surface.py` — diagnostics surface 与 runtime access 当前消费形态
- `custom_components/lipro/control/system_health_surface.py` — system health surface 与 runtime access 当前消费形态
- `custom_components/lipro/services/maintenance.py` — 当前 runtime infra / maintenance 交叉点
- `custom_components/lipro/services/device_lookup.py` — runtime lookup helper 现状
- `custom_components/lipro/runtime_infra.py` — runtime infra 现有薄层
- `custom_components/lipro/diagnostics.py` — HA diagnostics root adapter
- `custom_components/lipro/system_health.py` — HA system health root adapter

### Tests / guards
- `tests/core/test_control_plane.py` — control-plane 行为与 wiring 回归
- `tests/services/test_maintenance.py` — maintenance helper / runtime infra 回归
- `tests/services/test_device_lookup.py` — runtime lookup 回归
- `tests/services/test_services_registry.py` — service registry / router wiring 回归
- `tests/core/test_diagnostics.py` — diagnostics surface 回归
- `tests/core/test_system_health.py` — system health surface 回归
- `tests/meta/test_governance*.py` — governance / current truth / phase history 守卫

</canonical_refs>

<specifics>
## Specific Ideas

- 先做 control/services boundary inventory，明确哪些 import / helper / traversal 仍跨界回流；
- `RuntimeAccess` 应优先对 diagnostics / system health / maintenance / device lookup 暴露稳定 typed read-model，而不是把 coordinator internals 暗渡给 helper；
- `maintenance.py` 的 reload/listener/runtime traversal 很可能要并回 `entry_lifecycle_controller.py`、`runtime_infra.py` 或其他已有正式 home，而不是新建 carrier；
- 若边界解耦会改变 docs/guards 话术，需同步 `docs/developer_architecture.md`、review ledgers 与 meta guards。

</specifics>

<deferred>
## Deferred Ideas

- 不在本 phase 里裁剪 `.planning/phases/**` 或 contributor docs 噪音；
- 不在本 phase 里做 façade-era terminology convergence；
- 不在本 phase 里拆 protocol/share/mqtt 热点文件；
- 不把 benchmark 从 advisory posture 升级为新故事线。

</deferred>

---

*Phase: 43-control-services-boundary-decoupling-and-typed-runtime-access*
*Context gathered: 2026-03-20 after Phase 42 completion*
