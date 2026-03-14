# lipro-hass AGENTS.md

本文件是 `lipro-hass` 仓库的项目级执行契约，作用域覆盖整个仓库。
未来任何代理/贡献者进入本仓库，默认先遵守本文件，再结合更深层目录中的局部约束执行。

## 1. 项目定位

`lipro-hass` 是 Home Assistant 的 `Lipro` 集成。
本仓库已经采用“北极星终态架构”作为唯一正式裁决基准：

- **先定义正确终态，再安排迁移路径**
- **历史兼容成本不构成架构正确性的理由**
- **compat / residual 可以存在，但只能是显式、可计数、可删除的过渡层**

必读基线文档：

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/PROJECT.md`
3. `.planning/STATE.md`
4. `.planning/ROADMAP.md`
5. `.planning/REQUIREMENTS.md`
6. `.planning/baseline/PUBLIC_SURFACES.md`
7. `.planning/baseline/DEPENDENCY_MATRIX.md`
8. `.planning/baseline/VERIFICATION_MATRIX.md`
9. `.planning/baseline/AUTHORITY_MATRIX.md`
10. `.planning/reviews/FILE_MATRIX.md`
11. `.planning/reviews/RESIDUAL_LEDGER.md`
12. `.planning/reviews/KILL_LIST.md`


## 1.1 当前权威顺序

若文档之间出现冲突，按以下顺序仲裁：

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/ROADMAP.md`
3. `.planning/REQUIREMENTS.md`
4. `.planning/STATE.md`
5. `.planning/baseline/*.md`
6. `.planning/reviews/*.md`
7. `docs/developer_architecture.md`
8. `AGENTS.md`
9. `CLAUDE.md`（若存在，仅作 Claude Code 兼容入口，不另立规则）
10. 历史执行/审计/归档文档

## 2. 北极星硬约束

### 2.1 架构法则

全仓默认遵守以下法则：

1. **显式组合优于继承聚合**
2. **单一正式主链优于多入口并存**
3. **边界归一化优于上层兼容供应商原始形态**
4. **领域真源优于平台/实体重复表达**
5. **控制面 / 运行面 / 协议面 / 领域面 / 保障面分离**
6. **可验证、可观测、可仲裁优于“看起来能跑”**
7. **迁移残留必须持续收口，不得长期合法化**

### 2.2 明确禁止

以下模式不属于正式架构：

- `mixin` 作为正式设计模式
- 两条正式主链并存
- 兼容层反向定义 public surface
- 原始 vendor payload 穿透 protocol boundary 进入 runtime / domain / entity
- control plane、entity、platform 直连 `core.api` / `core.mqtt` / `core.coordinator` internals

## 3. 正式组件归属

### 3.1 Protocol Plane

正式协议根：

- `custom_components/lipro/core/protocol/facade.py` → `LiproProtocolFacade`
- `custom_components/lipro/core/api/client.py` → `LiproRestFacade`（Phase 2 正式 REST 子门面）
- `custom_components/lipro/core/mqtt/*` → MQTT transport / child-facade collaborators

裁决：

- `LiproProtocolFacade` 是**唯一正式 protocol-plane root**
- `LiproRestFacade` / `LiproMqttFacade` 是 child façade
- `LiproMqttClient` 仍是 direct transport class；`LiproClient` 已移除，不得以 compat shell 形式回流
- payload normalization 必须在 protocol plane 或已登记的 external-boundary family 内完成

### 3.2 Runtime Plane

正式运行根：

- `Coordinator` 是唯一正式 runtime orchestration root
- runtime public surface 只能通过正式 wiring / service surface 暴露

不要：

- 旁路刷新
- 旁路写状态
- 新增 coordinator internals backdoor
- 让 control / platform / entity 直接摸 runtime internals

### 3.3 Control Plane

正式控制面 home：

- `custom_components/lipro/control/`

正式组件：

- `EntryLifecycleController`
- `ServiceRegistry`
- `ServiceRouter`
- `DiagnosticsSurface`
- `SystemHealthSurface`
- `RuntimeAccess`
- `Redaction`

裁决：

- `custom_components/lipro/__init__.py`
- `custom_components/lipro/diagnostics.py`
- `custom_components/lipro/system_health.py`
- `custom_components/lipro/config_flow.py`

这些 HA 根模块只允许做 **thin adapter**，不得重新长回正式业务根。

### 3.4 External Boundary Truth

外部边界的正式真源由以下几层共同仲裁：

- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/phases/02.6-external-boundary-convergence/02.6-BOUNDARY-INVENTORY.md`
- `tests/fixtures/external_boundaries/**`
- `tests/meta/test_external_boundary_authority.py`
- `tests/meta/test_external_boundary_fixtures.py`
- `tests/meta/test_firmware_support_manifest_repo_asset.py`

特殊规则：

- `custom_components/lipro/firmware_support_manifest.json` 是 **local trust root**
- 远端 firmware support 仅是 **remote advisory source**
- 远端 advisory **不能单独决定 certified**
- `get_city / query_user_cloud` 继续复用 `tests/fixtures/api_contracts/**`，不要复制第二套真源

## 4. 当前已知残留与禁止误清理项

以下残留已登记，但**现在不要误删**：

1. `custom_components/lipro/services/execution.py`
   - 现状：仍有 coordinator 私有 auth seam
   - 处理原则：后续必须用正式 runtime/auth contract 替代，不要再扩散新的私有 hook

2. `LiproMqttClient`
   - 现状：direct transport class（非 protocol root）
   - 处理原则：不得新增新的生产路径直连 concrete transport，也不得恢复 `LiproClient` legacy constructor name

## 5. 关键实现陷阱

### 5.1 `__init__.py` 工厂模式不能回退

`custom_components/lipro/__init__.py` 必须保留“按调用时现取依赖”的工厂型装配。

不要做：

- 把 controller 变回模块级单例
- 提前绑定 `Coordinator` / `LiproProtocolFacade` / `LiproAuthManager`

原因：测试会 patch 这些依赖；若改回 eager binding，会破坏 `tests/core/test_init.py` 一类回归。

### 5.2 `system_health.py` 注册函数身份不能漂移

`custom_components/lipro/system_health.py` 中的 `async_register()` 必须注册根模块自己的 `system_health_info`。

不要直接把 control surface 的函数对象原样塞进注册流程，否则会破坏函数身份一致性相关测试。

### 5.3 control plane 不得绕开 `RuntimeAccess`

控制面读取 runtime 状态时：

- 必须优先走 `custom_components/lipro/control/runtime_access.py`
- 不要在 `diagnostics.py`、`system_health.py`、`services/**`、`flow/**` 重新散落读取 `entry.runtime_data` 或 coordinator 内部字段

## 6. 修改时必须同步的文档

出现以下情况时，必须同步文档：

### 6.1 改 public surface / dependency / authority

必须回写：

- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`（如果 external boundary truth 变化）

### 6.2 改文件归属 / residual / delete gate

必须回写：

- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

### 6.3 phase 完成态变化

必须回写：

- `.planning/STATE.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- 如需长期保留阶段结论，回写 `.planning/milestones/*.md` 或相应 governance docs；`phase` 目录下的 `*-SUMMARY.md` / `*-VALIDATION.md` 默认视为本地执行痕迹，不要求纳入 Git

### 6.4 Phase 资产身份与开源治理

- **默认身份**：`.planning/phases/**` 默认是执行工作区；`*-PLAN.md`、`*-CONTEXT.md`、`*-RESEARCH.md` 与临时过程文件按执行痕迹处理，不自动成为长期治理真源。
- **提升条件**：只有被 `.planning/ROADMAP.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/milestones/*.md` 或 `.planning/reviews/*.md` 显式引用的 phase 资产，才算长期治理/CI 证据。
- **发布门禁**：`.github/workflows/release.yml` 必须复用 `.github/workflows/ci.yml` 的版本/治理守卫，不得建立旁路发版故事线。
- **对外入口**：贡献者契约以 `CONTRIBUTING.md`、`.github/pull_request_template.md`、`.github/ISSUE_TEMPLATE/*.yml` 与 `SECURITY.md` 为准。

## 7. 测试与检查命令

### 7.1 基本规则

- 所有 Python 命令统一使用 `uv run ...`
- 不要裸跑 `python` / `pytest` / `ruff`

### 7.2 通用检查

- `uv run ruff check .`
- `uv run pytest -q`

### 7.3 按架构切片的推荐回归

**Protocol / API 改动**
- `uv run pytest tests/core/api tests/snapshots/test_api_snapshots.py -q`

**Unified protocol root / MQTT 改动**
- `uv run pytest tests/core/api tests/core/mqtt tests/integration/test_mqtt_coordinator_integration.py -q`

**External-boundary 改动**
- `uv run pytest tests/meta/test_external_boundary_authority.py tests/meta/test_external_boundary_fixtures.py tests/meta/test_firmware_support_manifest_repo_asset.py -q`
- `uv run pytest tests/core/test_report_builder.py tests/services/test_services_share.py tests/services/test_services_diagnostics.py tests/core/ota/test_firmware_manifest.py -q`

**Control-plane 改动**
- `uv run pytest tests/core/test_control_plane.py tests/core/test_init.py tests/core/test_diagnostics.py tests/core/test_system_health.py tests/services/test_services_registry.py tests/services/test_service_resilience.py tests/flows/test_config_flow.py -q`

**架构守卫**
- `uv run pytest tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py -q`

## 8. 代码修改偏好

- 优先小范围、明确边界、可验证的修改
- 优先修根因，不做表面缝补
- 优先复用已有正式组件，不新增“第三条故事线”
- 没有成为正式边界之前，不要创造新 adapter / helper / wrapper
- 对 compat 的任何新增都必须同时写明 delete gate

## 9. 提交前自检清单

提交前至少确认：

- [ ] 没有把 compat shell 重新提升为正式 root
- [ ] 没有新增 control / entity / platform 直连 internals
- [ ] 没有让 raw vendor payload 穿透正式边界
- [ ] 相关 baseline / governance / phase docs 已同步
- [ ] 跑过与本次改动匹配的最小充分测试集

## 10. 一句话裁决标准

如果你不确定某个改动是否正确，就问自己：

> **它是在把仓库继续收敛到单一北极星主链，还是在偷偷恢复第二套合法架构？**

若答案是后者，就不要那样改。
