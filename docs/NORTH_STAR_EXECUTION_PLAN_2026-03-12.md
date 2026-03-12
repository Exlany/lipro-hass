# Lipro 北极星架构执行计划（2026-03-12）

> **Status**: Active / In Progress
> **Goal**: 把“北极星目标架构”从文档标准推进为实际代码结构。
> **Strategy**: 原子提交、分平面推进、主代理仲裁、子代理并行巡检与落地。

## 1. 执行总原则

1. **目标态先行**：先定义终态，再设计迁移步骤
2. **一批只做一件事**：每次提交只完成一个清晰边界内的收敛动作
3. **主链优先**：先处理主链与跨层标准，再处理局部优化
4. **先消灭双标准**：凡是“某层例外”优先治理
5. **验证先行**：每个批次都必须有明确的验收命令与回归范围

## 2. 协作与分工模型

### 主代理（吾）

负责：
- 北极星终态裁决
- 文档/ADR 收敛
- 任务拆分与依赖排序
- 子代理输出仲裁
- 关键代码改动的最终整合与验收

### 子代理 A：Runtime / Control Plane

负责：
- Coordinator / Runtime / lifecycle / services / flow / diagnostics 只读巡检或定点改造
- 输出运行面与控制面的一致性问题、修复建议与补丁候选

### 子代理 B：Protocol / Domain Surface

负责：
- API client / MQTT / auth / command / platform capability 只读巡检或定点改造
- 输出协议边界与领域模型收敛建议、补丁候选

### 子代理 C：Assurance / Enforcement

负责：
- contract tests / snapshot / architecture tests / observability / CI 路径
- 输出验证矩阵、守卫测试、指标采集建议与补丁候选

## 3. 工作流拆分

### Phase A — 目标态对齐（已启动）

**目标**：统一文档、ADR、任务板与命名，明确北极星目标架构。

- A1. 建立北极星目标文档
- A2. 建立执行计划与分工文档
- A3. 回链 `developer_architecture.md` / ADR / audit active docs

**验收**：
- 文档口径无双标准
- 所有活跃文档能回答“终态是什么、当前偏差是什么、下一步做什么”

**状态**：`In Progress`

### Phase B — Protocol Contract Baseline

**目标**：先冻结高漂移协议边界，避免后续 API façade 与 capability 重构把协议漂移误判为架构回归。

#### B1. Protocol Contract Matrix
- 写 scope：`tests/fixtures/api_contracts/README.md`、相关 docs
- 结果：明确首批高风险入口、canonical payload、验收命令与 owning tests
- 验收：契约矩阵与首批测试文件一一对应

#### B2. Golden Fixtures（启动包）
- 写 scope：`tests/fixtures/api_contracts/`
- 结果：至少固化 `get_mqtt_config`、`get_city`、`query_user_cloud` 三个高风险入口
- 验收：fixture + targeted tests 通过

#### B3. Contract Tests / Snapshot Extension
- 写 scope：`tests/core/api/`、`tests/snapshots/`
- 结果：协议 helper/service 对 fixture 的 canonical 行为被锁定
- 验收：`uv run pytest tests/core/api tests/snapshots/test_api_snapshots.py -q`

### Phase C — Protocol Plane 重建

**目标**：把 `API Client` 从历史 mixin 聚合收敛到显式 facade + collaborators。

#### C1. API Client 目标态建模
- 写 scope：`custom_components/lipro/core/api/client.py` 及相关新 facade/collaborators
- 结果：`LiproClient` 不再通过多重继承聚合 transport/endpoints
- 验收：`uv run pytest tests/core/api -q`

#### C2. Endpoint collaborator 拆分
- 写 scope：`custom_components/lipro/core/api/endpoints/`、必要的 facade 层
- 结果：按域协作者显式注入，不再通过 `_Client*Mixin` 叠加行为
- 验收：`uv run pytest tests/core/api tests/snapshots/test_api_snapshots.py -q`

### Phase D — Control Plane 收敛

**目标**：让 config entry / options / diagnostics / system health / service wiring 成为清晰的控制面。

#### C1. Config Entry lifecycle 文档化并对齐实现
- 写 scope：`custom_components/lipro/__init__.py`、`config_flow.py`、`entry_options.py`、文档
- 结果：setup/unload/reload/reauth/option 边界统一

#### C2. Support surface 归面
- 写 scope：`diagnostics.py`、`system_health.py`、`services/diagnostics/`
- 结果：diagnostics / support / health 不再作为散落辅件存在

#### C3. Service registry boundary 审计
- 写 scope：`services/registry.py`、`services/registrations.py`
- 结果：服务注册只暴露稳定控制面接口

### Phase E — Domain Plane 统一

**目标**：统一 capability source-of-truth，减少 entity/platform/domain 三方重复表达。

#### E1. Capability model 盘点与统一入口
- 写 scope：`core/device/`、`entities/descriptors.py`、`entities/commands.py`、`helpers/platform.py`
- 结果：能力、属性、命令、平台规则共用同一套领域表达

#### E2. Platform rule normalization
- 写 scope：`fan.py`、`sensor.py`、`switch.py` 等平台文件
- 结果：平台差异通过声明式 rule/config 表达，而不是散落 if/else

### Phase F — Runtime Plane 强化

**目标**：让 runtime plane 在实现上完全符合北极星标准。

#### F1. Runtime public surface 收紧
- 写 scope：`core/coordinator/**`
- 结果：只有正式 public primitives 对外暴露

#### F2. 主链 invariant tests
- 写 scope：`tests/core/coordinator/**`
- 结果：命令、刷新、状态写入、MQTT lifecycle 的 invariants 有测试守护

### Phase G — Assurance Plane 建设

**目标**：把“先进”落到 contract tests、observability、architecture enforcement。

#### G1. Contract tests
- 写 scope：`tests/snapshots/`、`tests/core/api/`、`tests/core/mqtt/`

#### G2. Observability metrics
- 写 scope：`custom_components/lipro/core/api/observability.py` 及 runtime metrics hooks

#### G3. Architecture enforcement
- 写 scope：`tests/` 新增 architecture/dependency tests
- 结果：自动阻止跨层违规依赖与双主链回归

## 4. 原子提交序列建议

1. `docs: define north-star target architecture and execution plan`
2. `test(api): add protocol contract matrix and golden fixtures`
3. `refactor(api): replace client mixin inheritance with explicit facade`
4. `refactor(control-plane): consolidate config entry and support surfaces`
5. `refactor(domain): unify capability and platform rules`
6. `test(runtime): enforce north-star runtime invariants`
7. `feat(observability): add north-star runtime metrics`
8. `test(architecture): enforce dependency and boundary rules`

## 5. 启动批次（本轮开始）

### Batch 1 — 文档与任务板对齐

- [x] 建立北极星目标架构文档
- [x] 建立执行计划与协作模型
- [ ] 在现有架构文档中回链北极星文档
- [ ] 将活跃文档口径更新到 audit 文档

### Batch 2 — Protocol Contract Matrix + Golden Fixture（已启动）

- [x] 仲裁三路子代理建议并确定“契约先于重构”
- [ ] 建立 `tests/fixtures/api_contracts/README.md` 契约矩阵
- [ ] 固化 `get_mqtt_config` / `get_city` / `query_user_cloud` 三个 fixture
- [ ] 新增 targeted contract tests 并跑通

### Batch 3 — API Client 去 mixin 化设计与落地准备

- [ ] 盘点 `_ClientTransportMixin` / `_ClientAuthRecoveryMixin` / `_ClientPacingMixin` / `endpoints/*`
- [ ] 设计显式 facade + collaborator 目标模块图
- [ ] 确定首批重构写入范围与测试矩阵
- [ ] 开始第一批代码重构

## 6. 本轮分工（已发起）

- 子代理 A：runtime / control-plane 终态与相位拆分
- 子代理 B：API client / protocol boundary / capability 终态与相位拆分
- 子代理 C：contract tests / observability / architecture enforcement 终态与相位拆分
- 主代理：合并三路建议，更新活跃文档与执行计划，并推进 Batch 2 / Batch 3

## 7. 本轮之后的直接下一步

**直接进入 Batch 2 / Batch 3**：

1. 先完成协议契约矩阵与 3 个高价值 golden fixtures
2. 再基于被锁定的边界推进 `API Client` 去 mixin 化设计
3. 最后开启第一批代码改造与 targeted tests
