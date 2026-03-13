# Lipro 北极星架构执行计划（2026-03-12）

> **Status**: Historical snapshot / Archived execution context
> **Goal**: 记录 2026-03-12 当日的执行思路快照，不再作为当前 phase/status 真源。
> **Current authority**: `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` + `.planning/ROADMAP.md` + `.planning/REQUIREMENTS.md` + `.planning/STATE.md` + `.planning/reviews/FILE_MATRIX.md`

## 0. GSD 工作集

当前已初始化本地 `.planning/` 工作集（被 `.gitignore` 忽略，不进入仓库版本视图）：

- `.planning/PROJECT.md` — 项目北极星上下文
- `.planning/REQUIREMENTS.md` — 可追踪架构需求
- `.planning/ROADMAP.md` — GSD 路线图真源
- `.planning/STATE.md` — 会话延续与当前焦点
- `.planning/phases/01-protocol-contract-baseline/` — Phase 01 context + plans
- `.planning/phases/01.5-north-star-baseline-assets/` — Phase 01.5 full planning pack
- `.planning/phases/02-api-client-de-mixin/` — Phase 02 full planning pack
- `.planning/phases/02.5-protocol-root-unification/` — Phase 02.5 full planning pack
- `.planning/phases/02.6-external-boundary-convergence/` — Phase 02.6 full planning pack
- `.planning/phases/03-control-plane-convergence/` — Phase 03 drafted planning pack
- `.planning/codebase/` — brownfield codebase map（7 份）

## 1. 执行总原则

1. **目标态先行**：先定义终态，再设计迁移步骤
2. **全仓视角**：不是修几个热点文件，而是让全部 Python 文件都有最终去向
3. **主链优先**：先治理正式主链与跨层标准，再处理局部优化
4. **先消灭双标准**：凡是“某层例外”优先治理
5. **验证先行**：每个批次必须有明确验收命令与回归范围
6. **历史债不参与终态决策**：只影响排期，不影响正确性判断

## 2. 协作与分工模型

### 主代理（吾）

负责：
- 北极星终态裁决
- 文档 / ADR / 路线图收敛
- 任务拆分与依赖排序
- 子代理输出仲裁
- 关键代码改动的最终整合与验收

### 子代理 A：Runtime / Control Plane

负责：
- `Coordinator / Runtime / lifecycle / services / flow / diagnostics` 巡检或定点改造
- 输出运行面与控制面的一致性问题、修复建议与补丁候选

### 子代理 B：Protocol / Domain Surface

负责：
- `API client / MQTT / auth / command / capability / platform` 巡检或定点改造
- 输出协议边界、领域模型、兼容层清理建议与补丁候选

### 子代理 C：Assurance / Enforcement

负责：
- `contract tests / snapshot / architecture tests / observability / CI` 路径
- 输出验证矩阵、守卫测试、指标采集建议与补丁候选

## 3. 全仓治理轨（Cross-Cutting Tracks）

### Track X1 — 全量文件审视矩阵

目标：把全部 Python 文件纳入正式治理，而不是只盯热点模块。

交付物：
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`

要求：
- 每个 `*.py` 文件都有 `保留 / 重构 / 迁移适配 / 删除` 归类
- 每个 phase 都要更新本轮触达文件簇与残留清单
- 不允许“暂时保留但无人负责”的灰色模块长期存在

### Track X2 — 架构一致性护栏

目标：把北极星原则变成日常守卫。

要求：
- contract tests 锁协议边界
- architecture tests 锁依赖方向与双主链回归
- lifecycle / flow / diagnostics tests 锁控制面
- invariants tests 锁 runtime plane

### Track X3 — 残留清零机制

目标：历史兼容层只能短期存在，且必须有失效时间点。

要求：
- 每个 compat adapter 必须有 owning phase
- 每个 compat adapter 必须有下游消费者清单
- 每个 compat adapter 必须有删除触发条件

## 4. 工作流拆分

### Phase 1 — 协议契约基线

**目标**：先冻结高漂移协议边界，避免后续 API façade 与 capability 重构把协议漂移误判为架构回归。

- 建立 protocol contract matrix
- 固化 golden fixtures
- 将首批 contract baseline 纳入 targeted tests 与 snapshot 视角

**当前状态**：`In Progress`

### Phase 1.5 — 北极星基准资产化

**目标**：在大规模重构前，把 target topology、dependency matrix、public surfaces、verification matrix 与 authority matrix 正式资产化，并落下最小 seed guards。

- 固化 baseline asset pack 的 formal status 与同步方向
- 建立 dependency/public-surface 最小 guard seeds
- 为 Phase 2+ 提供统一 baseline handoff

**当前状态**：`Drafted / Blocked by unfinished Phase 01 closeout outputs`

### Phase 2 — API Client 去 Mixin 化

**目标**：先把 REST / IoT 协议主链从历史 mixin 聚合收敛到显式 facade + collaborators，并把 `core/api/**/*.py` 全量纳入正式治理。

- 盘点 `core/api/**/*.py` 与相关 tests 的 keep / refactor / adapter / delete 去向
- 设计 `LiproRestFacade + collaborators + normalizers + compat adapters` 目标结构
- 用组合式对象替代 `_Client*Mixin` 多重继承
- 在 Phase 1 contract baseline 保护下迁移公开 REST API surface
- 保证结构可无缝演进到统一协议根 `LiproProtocolFacade`

**当前状态**：`Drafted / Waiting for upstream baseline closeout and execution outputs`

### Phase 2.5 — Protocol Root Unification

**目标**：把 REST / MQTT 一起统一到单一 protocol-plane root `LiproProtocolFacade`，让协议平面成为真正完整的一等平面。

- 建立 `LiproProtocolFacade` 作为唯一正式协议入口
- 让 `LiproRestFacade` 与 `LiproMqttFacade` 成为子门面，而不是两个独立根
- 对齐 auth / telemetry / diagnostics / protocol contracts 的共享边界
- 明确 canonical normalization 由 protocol plane 边界正式拥有
- 清退 split-root public surface 与 `LiproClient` compat semantics

**当前状态**：`Drafted / Blocked by unfinished Phase 02 execution outputs`

### Phase 2.6 — External Boundary Convergence

**目标**：把 `share / firmware advisory / support payload / diagnostics capability` 收敛为 formal owner、authority、fixture、generated artifact 与 drift-detection 体系。

- external-boundary inventory 必须以 unified protocol root 为前提
- `firmware_support_manifest.json` 是 local trust root；remote firmware-support 只能 advisory-only
- `generated` 不能继续藏在实现文件里暗中定义真相
- 为 Phase 3 提供 support surface / diagnostics / system health 可直接引用的外部边界输出

**当前状态**：`Drafted / Blocked by unfinished Phase 2.5 execution outputs`

### Phase 3 — Control Plane 收敛

**目标**：让 `config entry / options / diagnostics / system health / service wiring` 成为清晰、可验证的控制面。

### Phase 4 — Capability Model 统一

**目标**：统一 capability source-of-truth，减少 entity / platform / domain 三方重复表达。

### Phase 5 — Runtime 主链加固

**目标**：让 runtime plane 在实现上完全符合单一正式主链与显式 public surface 原则。

### Phase 6 — Assurance Plane 正式化

**目标**：把 contract、observability、architecture enforcement、CI gates 变成正式保障面。

## 5. 原子提交序列建议

1. `docs: strengthen north-star target architecture and execution tracks`
2. `test(api): add protocol contract matrix and golden fixtures`
3. `docs(planning): define phase-2 demixin research and execution plans`
4. `refactor(api): replace client mixin inheritance with explicit rest facade`
5. `refactor(protocol): unify rest and mqtt under protocol root`
6. `refactor(control-plane): consolidate config entry and support surfaces`
7. `refactor(domain): unify capability and platform rules`
8. `test(runtime): enforce north-star runtime invariants`
9. `feat(observability): add north-star telemetry hooks`
10. `test(architecture): enforce dependency and boundary rules`

## 6. 本轮焦点

### 已完成

- 北极星目标文档、开发者架构文档、ADR、审计活跃文档已建立回链
- `.planning/` 工作集已初始化
- Phase 1 已建立首批 protocol contract baseline

### 正在推进

- 完成 Phase 1 收尾（snapshot / summary / handoff）
- 生成 Phase 2 的 context / research / detailed plans
- 把“全量文件审视矩阵”纳入后续 phase 的刚性要求

## 7. 本轮之后的直接下一步

1. 完成 `.planning/phases/01-protocol-contract-baseline/01-02-PLAN.md`
2. 执行 `.planning/phases/01.5-north-star-baseline-assets/*-PLAN.md`
3. 完成 `Phase 02` execution closeout，生成 REST façade / demixin 的真实 summaries
4. 执行 `.planning/phases/02.5-protocol-root-unification/*-PLAN.md`
5. 在 unified protocol root 落地后执行 `.planning/phases/02.6-external-boundary-convergence/*-PLAN.md`
6. 基于 `02.5 + 02.6` 真实输出回到 `Phase 03` 做 unblock 复核
