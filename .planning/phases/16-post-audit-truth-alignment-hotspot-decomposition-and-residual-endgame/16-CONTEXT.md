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
5. device/entity/OTA/test layering 与 contributor/open-source DX follow-through；
6. 用 second-pass repo audit 把 Phase 16 的完成态锁成“零 silent defer / 零无主高风险尾债”。

</domain>

<decisions>
## Implementation Decisions

### Governance Truth & Toolchain Alignment
- `AGENTS.md` 与 baseline/review truth 必须与代码一致，已关闭 seam 不得继续登记为 active residual。
- `.planning/codebase/*` 必须被裁决为正式协作资产或本地缓存视图，不再半悬空。
- Python / mypy / Ruff / pre-commit / devcontainer 版本口径统一；marker / benchmark / dev-audit / coverage gate 必须真实可解释。
- phase closeout 时不能只更新 phase 目录；active truth docs 与 review assets 必须同步收口。

### Hotspot Decomposition
- 第一优先级热点：`core/api/client.py`、`core/protocol/facade.py`、`core/coordinator/coordinator.py`。
- 第二优先级热点：`control/service_router.py`、`config_flow.py`、`entities/firmware_update.py`、`control/entry_lifecycle_controller.py`、`control/diagnostics_surface.py`、`control/telemetry_surface.py`、`core/coordinator/runtime/mqtt_runtime.py`、`core/api/request_policy.py`、`core/api/status_fallback.py`、`core/api/auth_service.py`、`core/api/mqtt_api_service.py`、`core/protocol/boundary/rest_decoder.py`、`core/utils/developer_report.py`、`core/command/dispatch.py`。
- 拆薄只能沿 formal boundary 做 extraction；不得为减行数引入第二 root 或 helper-root promotion。

### Type Contracts & Exception Semantics
- `Any` / `type: ignore` / 反射宽口继续收窄到 `Protocol`、typed alias、`TypedDict` 与更明确的 formal contract。
- 关键链路的 catch-all 异常必须收窄或 documented arbitration；不能保留“谁都接住但谁也说不清”的口袋异常。
- `cast` / `getattr` / `import_module` 只能作为过渡，不得继续充当长期 contract。
- second-pass metrics 中暴露出的 secondary hotspots，必须在对应 plan 中被显式列名，而不是只被总目标含混覆盖。

### Residual Endgame
- `_ClientBase` / `_Client*Mixin` / endpoint mixin exports / `LiproMqttClient` / `get_auth_data()` / power compat envelope 都在 endgame scope 内。
- 不做无 gate rename campaign；future rename 必须以后续解绑为前提。
- endpoint mixin exports 不能继续作为半公开 API 暴露。
- 任何 remaining residual 若保留，必须在 phase closeout 中证明它是局部、低风险、可删除而非再次合法化。

### Control / Service / Runtime Contracts
- `send_command` 必须并入统一 auth/error mainline。
- share / developer-report / maintenance / device-lookup / runtime-access / diagnostics / telemetry / entry-lifecycle response contract 继续收口；动态导入与反射式能力探测继续下降。
- `service_router.py` 保持 public handler home；私有 glue 继续下沉。
- `EntryLifecycleController`、`DiagnosticsSurface`、`TelemetrySurface` 不能继续作为“宽 Any 注入 + broad catch”灰区存在。

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
- secondary hotspots 是在单 plan 内消化，还是通过相邻 helper cluster 一并收口的具体拆法

</decisions>

<specifics>
## Specific Ideas

- 先做治理/toolchain truth alignment，再推进热点拆薄；避免用错误地图指导重构。
- 继续按 `3 waves / 6 plans` 推进，但每个 plan 要显式接住 second-pass 发现的漏网热点：
  1. `16-01`：governance truth + codebase map policy + active residual / authority ordering + closeout truth vocabulary。
  2. `16-02`：toolchain truth + dead marker removal + local DX contract + contributor-facing single-story cleanup。
  3. `16-03`：control/service/config-flow + entry lifecycle + diagnostics/telemetry surfaces + developer-report / maintenance / device-lookup contract unification。
  4. `16-04`：protocol/runtime hotspots + request-policy / status-fallback / auth-service / mqtt-runtime / rest-decoder typing & exception tightening。
  5. `16-05`：domain/entity/OTA rationalization + explicit domain truth + firmware update residual slim-down。
  6. `16-06`：platform/domain test-layer correction + DX/runbook docs + release/support truth + second-pass repo audit / zero-carry-forward closeout。
- 验证必须覆盖：`uv run ruff check .`、`uv run mypy`、focused suites、governance/meta guards、`scripts/check_architecture_policy.py --check`、`scripts/check_file_matrix.py --check`、必要时 full suite 与 snapshots。
- 除常规验证外，还要在波次末尾做 debt audit：复核 `Any`、`type: ignore`、`except Exception`、dead markers、dynamic entry points 与 hotspot inventory 是否还有未纳管对象。

</specifics>

<deferred>
## Deferred Ideas

- `LiproMqttClient` physical rename
- 与北极星无关的大规模换栈
- 新重型依赖或新 observability stack
- 为 residual 清理而重开第二条正式主链
- 没有 owner / delete gate / 风险说明的 silent defer

</deferred>

---

*Phase: 16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame*
*Context gathered: 2026-03-15 via PRD Express Path*
