# Phase 16: Post-audit truth alignment, hotspot decomposition, and residual endgame - Context

**Gathered:** 2026-03-15
**Status:** Ready for planning
**Source:** PRD Express Path (`.planning/phases/16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame/16-PRD.md`)

<domain>
## Phase Boundary

本 phase 聚焦终极审阅后仍然成立的“高标准收尾期”问题：
1. 治理真源 / toolchain / codebase map policy 真相校准；
2. core/runtime/protocol/control/domain/OTA 热点继续拆薄；
3. 类型契约、异常语义与 control/runtime/service formal contracts 收紧；
4. residual/compat 认知债与 helper-level envelope 继续本地化、减语义；
5. device/entity/OTA/test layering 与 contributor/open-source DX follow-through。

</domain>

<decisions>
## Implementation Decisions

### Governance Truth & Toolchain Alignment
- `AGENTS.md` 与 baseline/review truth 必须与代码一致，已关闭 seam 不得继续登记为 active residual。
- `.planning/codebase/*` 必须被裁决为正式协作资产或本地缓存视图，不再半悬空。
- Python / mypy / Ruff / pre-commit / devcontainer 版本口径统一；marker / benchmark / dev-audit / coverage gate 必须真实可解释。

### Hotspot Decomposition
- 第一优先级热点：`core/api/client.py`、`core/protocol/facade.py`、`core/coordinator/coordinator.py`。
- 第二优先级热点：`control/service_router.py`、`config_flow.py`、`entities/firmware_update.py`。
- 拆薄只能沿 formal boundary 做 extraction；不得为减行数引入第二 root 或 helper-root promotion。

### Type Contracts & Exception Semantics
- `Any` / 反射宽口继续收窄到 `Protocol`、typed alias、`TypedDict` 与更明确的 formal contract。
- 关键链路的 catch-all 异常必须收窄或 documented arbitration。
- `cast` / `getattr` / `callable` 只能作为过渡，不得继续充当长期 contract。

### Residual Endgame
- `_ClientBase` / `_Client*Mixin` / endpoint mixin exports / `LiproMqttClient` / `get_auth_data()` / power compat envelope 都在 endgame scope 内。
- 不做无 gate rename campaign；future rename 必须以后续解绑为前提。
- endpoint mixin exports 不能继续作为半公开 API 暴露。

### Control / Service / Runtime Contracts
- `send_command` 必须并入统一 auth/error mainline。
- share / developer-report / runtime-access response contract 继续收口；动态导入与反射式能力探测继续下降。
- `service_router.py` 保持 public handler home；私有 glue 继续下沉。

### Domain / Entity / OTA / Tests
- `LiproDevice` 收窄到单一领域真源投影，不再继续膨胀。
- capability 消费协议收敛，减少 `supports_platform()` / `is_xxx` 双轨语义。
- OTA entity 回到 projection + action bridge，manifest load / row arbitration / cache hot path 继续下沉。
- platform tests 优先测真实 entity adapter；domain / OTA 策略测试回归正确 home。

### Claude's Discretion
- 具体 extraction 的模块切分粒度
- `TypedDict` vs `Protocol` vs richer value object 的选型
- validation map 中 quick/full suite 的组合与 sampling cadence
- `.planning/codebase/*` 最终采用“删除/纳管/保留但显式标注”的哪一种策略

</decisions>

<specifics>
## Specific Ideas

- 先做治理/toolchain truth alignment，再推进热点拆薄；避免用错误地图指导重构。
- 可按 3 waves / 6 plans 规划：
  1. governance truth + toolchain truth + codebase map policy
  2. control/service contract unification + response schema stabilization
  3. protocol/api residual spine + typing + compat envelope narrowing
  4. runtime/protocol/control hotspot decomposition + exception semantics tightening
  5. domain/entity/OTA rationalization + platform test layering correction
  6. troubleshooting / runbook / contributor navigation / local develop DX follow-through
- 验证必须覆盖：`uv run ruff check .`、`uv run mypy`、focused suites、governance/meta guards、`scripts/check_architecture_policy.py --check`、`scripts/check_file_matrix.py --check`、必要时 full suite。

</specifics>

<deferred>
## Deferred Ideas

- `LiproMqttClient` physical rename
- 与北极星无关的大规模换栈
- 新重型依赖或新 observability stack
- 为 residual 清理而重开第二条正式主链

</deferred>

---

*Phase: 16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame*
*Context gathered: 2026-03-15 via PRD Express Path*
