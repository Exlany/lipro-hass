# Phase 03 Research: Control Plane Convergence

**Updated:** 2026-03-12
**Research mode:** implementation / architecture baseline
**Decision stance:** 不受历史成本约束，以 Home Assistant 集成的终态 control-plane 设计为唯一判断标准

## Research Framing

Phase 3 不回答“现有 `__init__.py + services/wiring.py + diagnostics.py` 还能不能继续修补”，而回答：

- 什么样的 control plane 才算正式、统一、可长期维护？
- Home Assistant 强制存在的入口模块，如何与内部正式控制组件解耦？
- 控制面怎样访问 runtime 才不算 coordinator backdoor？
- 怎样在全仓审视的同时，避免把 Phase 3 膨胀成 Phase 4 / 5 / 6 / 7？

结论先行：

- **Control plane 必须拥有明确 internal home；HA 根模块只能做 adapter，不应继续承载真实编排。**
- **`EntryLifecycleController / ServiceRegistry / DiagnosticsSurface / SystemHealthSurface` 是正确的四个正式组件。**
- **控制面与 runtime 的交互必须经由 control-owned access contracts / read models，而不是直接读取 coordinator 内部字段。**
- **全仓 `378` 个 Python 文件的审视应该通过 governance matrix 落地，但本 phase 只执行 control-plane 范围内的改造。**

## Upstream Readiness

本 research 的仲裁前提是：**Phase 3 的设计方向可以先定义，但执行 readiness 不能跳过上游。**

当前最关键的 readiness 事实：
- `Phase 2.6` 的 execution outputs 与 closeout proof 已生成，并已成为 Phase 3 的正式上游输入
- `DiagnosticsSurface / SystemHealthSurface` 所依赖的 `support payload / share / firmware / external boundary` authority source 已由 `02.6` 正式沉淀，可直接被控制面消费
- 因此，本文件保留的是 pre-execution research；Phase 3 当前正式状态已由 `03-VALIDATION.md` 与 `03-01/02/03-SUMMARY.md` 定格为 Completed / validated

## Key Findings

### 1. HA 入口模块必须变薄，而不是继续当根

`__init__.py`、`diagnostics.py`、`system_health.py`、`config_flow.py` 是 Home Assistant 框架要求的入口模块，但它们不应该继续定义内部架构。

最佳模式应为：
- 根模块保留 HA 签名与最小路由职责
- 真实控制逻辑落到内部 `control/` package 或等价命名化组件
- 所有复杂生命周期与 support logic 在内部正式对象上完成，而不是在根模块堆叠 helper 调用

### 2. Lifecycle 应有唯一 owner

当前 setup / unload / reload / reauth / options / service sync 分散在多个模块间，导致“谁拥有 entry 生命周期”并不清晰。

正确终态应为：
- `EntryLifecycleController` 成为唯一 lifecycle owner
- `entry_auth.py`、`entry_options.py`、`runtime_infra.py`、`coordinator_entry.py`、`domain_data.py` 变成 controller collaborators
- `__init__.py` 只负责把 HA 调用转发给 controller

### 3. Service surface 必须声明式化 + 去热点化

`services/wiring.py` 之所以成为热点，不是因为 service 本身复杂，而是因为声明、注册、路由、debug gating、runtime lookup、日志包装都被塞进同一文件。

最佳设计应为：
- `ServiceRegistry` 作为唯一 service boundary owner
- `contracts.py + registrations.py + registry.py` 成为声明式真源
- `execution.py / device_lookup.py / errors.py` 承担命名化协作职责
- `wiring.py` 拆解为若干显式组件，最终不再作为正式根存在
- debug / developer service gating 只能有一处权威实现

### 4. Diagnostics / System Health 本质上是 Support Surface

`diagnostics.py` 与 `system_health.py` 不是 runtime 平面的一部分，也不应直接触碰 runtime internals；它们本质上是 control plane 的 support surface。

最佳设计应为：
- `DiagnosticsSurface` 负责 config-entry / device diagnostics、redaction、support payload 汇总
- `SystemHealthSurface` 负责聚合 entry 级健康探针、依赖状态、设备数量等高层信息
- 两者共享控制面自己的 runtime read models / adapters，而不是重复读取 `runtime_data`
- redaction policy 成为显式协作对象，而不是散落 helper 约定

### 5. 测试要围绕 public surfaces，不围绕私有 helper

当测试直接 import `_async_handle_get_city` 或围绕内部结构 patch 时，说明正式公共边界不存在。

Phase 3 的正确测试策略应为：
- lifecycle tests 围绕 `async_setup_entry / async_unload_entry / async_reload_entry` 与 controller 协作
- flow tests 围绕 `config_flow.py` / `flow/**` 的用户语义与 reauth / options story
- services tests 围绕 `ServiceRegistry` 暴露的正式注册与调用面
- diagnostics / system health tests 围绕 `DiagnosticsSurface / SystemHealthSurface` 的 public outputs 与 redaction guarantees
- 尽量减少对私有 handler、内部 coordinator 字段、私有 wiring 细节的断言

### 6. Governance 必须与架构改造同轮推进

如果只改代码、不更新 `FILE_MATRIX / RESIDUAL_LEDGER / KILL_LIST / PUBLIC_SURFACES / DEPENDENCY_MATRIX / VERIFICATION_MATRIX`，就会出现“代码重构了，但全仓治理口径仍旧停在旧世界”的问题。

所以 Phase 3 必须把“全仓 control-plane lens 审视”落成治理资产，而不是口头承诺。

## Cross-Phase Arbitration

为避免 Phase 1 ~ 3 各自说一套话，Phase 3 必须接受以下仲裁：

- **Phase 1** 只负责冻结最小高价值协议契约，不负责 control plane 设计；Phase 3 不得回头改写 protocol truth。
- **Phase 2 / 2.5** 负责建立 `LiproRestFacade -> LiproProtocolFacade` 的协议正式根；Phase 3 不得把 control plane 变成协议根的直接消费者。
- **Phase 2.6** 负责 formalize `support payload / share / firmware / external boundary`；Phase 3 的 `DiagnosticsSurface` 只能消费已 formalized 的边界，不得重新拍板 authority source。
- **Phase 4** 负责 capability truth；Phase 3 的 support read models 只能是 control-oriented projection，不能变成新的领域规则系统。
- **Phase 5** 负责 runtime public surface 最终统一；Phase 3 的 runtime access contracts 只能是控制面消费者边界，不得升级成第二个 runtime root。

## Recommended Target Component Map

### Mandatory Deliverables
- `EntryLifecycleController`
- `ServiceRegistry`
- `DiagnosticsSurface`
- `SystemHealthSurface`

### Recommended Supporting Collaborators
- `control/runtime_access.py` 或等价模块：提供 control → runtime 的稳定访问契约
- `control/service_router.py` 或等价模块：承接 service 声明到 handler 绑定
- `control/redaction.py` 或等价模块：集中 support surface 的脱敏规则
- `control/models.py` 或等价模块：承载 diagnostics / system health read models

上述 supporting collaborators 的命名可调整，但“四个正式组件 + 一组稳定 runtime access / support read model 协作者”的组合是锁定方向。

## What Not To Do

1. **不要让 `wiring.py` 只是“稍微整理一下继续留着”**
   - 这会让热点文件继续充当事实根，违背 Phase 3 目标。

2. **不要把 runtime public surface 的最终统一化提前塞进本阶段**
   - Phase 3 需要稳定接缝，但 runtime plane 的正式最终化属于 Phase 5。

3. **不要用更多 helper / utils 再包一层，继续维持散点协作**
   - 需要的是命名化组件与 ownership，而不是新的松散函数堆。

4. **不要让 tests 继续绑定私有 `_async_handle_*` 与内部字段名**
   - 这样会把旧结构变成“被测试强行冻结”的残留。

5. **不要只看控制面文件，不更新全仓治理矩阵**
   - 用户要求是全仓审视；Phase 3 必须在治理台账上体现这一点。

## Common Pitfalls

- 在 `__init__.py` 中继续混合 setup / unload / service sync / runtime cleanup 细节
- 在 `diagnostics.py` 与 `system_health.py` 分别复制相似的 runtime 读取逻辑
- 在 `registrations.py` 与 `wiring.py` 同时定义 debug gating，造成双权威
- 把 service handlers 当成正式 public surface，而不是 `ServiceRegistry`
- 把“全仓审视”误解成“全仓一次性重构”，导致 Phase 3 失控

## Recommended Verification Matrix

### Minimum execution proof

```bash
uv run pytest tests/core/test_init.py tests/core/test_entry_update_listener.py tests/core/test_token_persistence.py tests/flows/test_config_flow.py tests/services/test_services_registry.py tests/core/test_diagnostics.py tests/core/test_system_health.py -q
```

### Stronger closeout proof

```bash
uv run pytest tests/flows tests/services tests/core/test_init.py tests/core/test_entry_update_listener.py tests/core/test_token_persistence.py tests/core/test_diagnostics.py tests/core/test_system_health.py -q
```

### Manual review proof

- `FILE_MATRIX.md` 已登记 control-plane lens 下的全仓分类与本 phase 归属
- `RESIDUAL_LEDGER.md` 已记录 `wiring.py`、private handler imports、runtime backdoor 等残留
- `KILL_LIST.md` 已列出本 phase 可删与 Phase 7 再删对象
- `PUBLIC_SURFACES.md` 与 `DEPENDENCY_MATRIX.md` 已写明 control plane 的正式边界与 allowed edges
- `VERIFICATION_MATRIX.md` 已记录 CTRL-01 ~ CTRL-04 的 exit contract

## Recommendation

### Locked Recommendation

**Phase 3 的最优实施路线应为：**

1. 先用全仓 control-plane lens 完成治理与公共边界冻结
2. 再提炼 `EntryLifecycleController` 与 control → runtime access contracts
3. 然后拆掉 `services/wiring.py` 的 mega-root 角色，收口 `ServiceRegistry`
4. 再统一 `DiagnosticsSurface / SystemHealthSurface` 与 redaction / read models
5. 最后把 flow / lifecycle / diagnostics / services tests 全部对齐到正式 public surfaces，并更新治理 handoff

### What Makes This “Advanced”

不是“多引几个框架”，而是：
- HA 入口与内部正式组件彻底分离
- 单一 owner、单一 public surface、单一 service registration story
- runtime 访问通过稳定 contract，而不是字段 folklore
- support surface 的 redaction、health、diagnostics 拥有显式模型与测试契约
- 全仓治理矩阵与代码重构同步演进，不再口径分裂

## Confidence

- **High**: `EntryLifecycleController / ServiceRegistry / DiagnosticsSurface / SystemHealthSurface` 作为 Phase 3 正式交付物，与 requirements / roadmap / codebase concerns 完全一致。
- **High**: `services/wiring.py` 不应继续作为终态根，这一点有代码热点与测试耦合双重证据支撑。
- **High**: diagnostics / system health 应通过 stable runtime access contracts，而不是继续直接读 coordinator 内脏。
- **Medium**: control-plane 内部 `control/` 子包的具体文件命名可在执行期微调。
- **Medium**: 某些 service handlers 是否完全迁移路径，需结合 direct consumers 与 Phase 7 compat 清理节奏裁定。

## Sources

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/CONCERNS.md`
- `.planning/codebase/STRUCTURE.md`
- `.planning/phases/02-api-client-de-mixin/02-CONTEXT.md`
- `.planning/phases/01-protocol-contract-baseline/01-RESEARCH.md`
- `.planning/phases/02-api-client-de-mixin/02-ARCHITECTURE.md`
- `.planning/phases/02.6-external-boundary-convergence/02.6-CONTEXT.md`
- `.planning/phases/02.6-external-boundary-convergence/02.6-ARCHITECTURE.md`
- `custom_components/lipro/__init__.py`
- `custom_components/lipro/config_flow.py`
- `custom_components/lipro/diagnostics.py`
- `custom_components/lipro/system_health.py`
- `custom_components/lipro/services/wiring.py`
- `custom_components/lipro/services/registrations.py`
- `custom_components/lipro/services/registry.py`
- `tests/flows/test_config_flow.py`
- `tests/services/test_services_registry.py`
- `tests/services/test_service_resilience.py`
- `tests/core/test_diagnostics.py`
- `tests/core/test_system_health.py`
