# Project: Lipro-HASS North Star Evolution v1.1

**Status:** Active — `Phase 16` 已规划完成，execution pending
**Goal:** 把 `protocol truth`、`architecture policy`、`runtime telemetry export`、`replay evidence`、`ai-debug evidence pack`、`residual surface closure`、`api drift isolation / core-boundary prep`、`control router / runtime-access / OTA / governance coherence`、`type contract alignment / residual cleanup / contributor governance hygiene`、`explicit domain surface / governance guard hardening / hotspot boundary decomposition`、`legacy stack final closure / API spine demolition / governance truth consolidation`、`support feedback contract hardening / governance truth repair / maintainability follow-through` 与 `post-audit truth alignment / hotspot decomposition / residual endgame` 十三条演进线统一纳入北极星主链，进入“可保真、可观测、可仲裁、可回放、可给 AI 调试/分析、可持续收尾”的下一里程碑。

## Why This Milestone Exists

`v1.0` 已完成北极星主链重建，但还缺少几类“高杠杆正式能力”：

- protocol boundary schema / decoder family，让外部输入在边界被统一规范化
- architecture enforcement，把北极星裁决从文档提升为可自动阻断的规则链
- runtime telemetry exporter，把当前 snapshot/diagnostics 进化为正式导出面
- protocol replay / simulator harness，把逆向协议证据沉淀为可重复回放的 assurance asset
- AI debug evidence pack：把 telemetry/replay/边界库存统一导出为“可给 AI 分析”的脱敏证据包

这些能力不是孤立功能，而是为了让仓库进入下一阶段：

- **协议变更可被回放与比对**
- **结构回退可被规则自动拦截**
- **运行信号能被正式导出，而不是散落在 diagnostics 里**
- **AI 可分析优先**：telemetry/export/replay/evidence 的产物必须机器友好（结构化、稳定 schema、可版本化、带时间戳、带事件序列），同时严格脱敏。

## What Changes In v1.1

### 1. Boundary Truth 更严格

- protocol boundary family 成为 decode authority 的正式归属
- REST / MQTT 进入 runtime 前，必须先落 canonical contract
- schema / decoder / authority / fixture / drift detection 形成统一链路

### 2. Architecture Policy 更可执行

- 北极星约束不再只存在于文档里
- plane / root / public surface / authority / residual 规则可由 CI 与 meta tests 执行
- 双主链、compat 回流、跨层直连与 raw payload leakage 被更早阻断

### 3. Telemetry / Replay / Evidence 形成 assurance 主链

- telemetry exporter 收口 runtime/protocol 的正式运维信号
- replay harness 用正式 public path 回放协议样本
- evidence pack 从正式真源 pull 结构化证据给 AI 调试与分析

### 4. Residual Surface 更收敛

- protocol formal public surface 已显式化；child-defined contract 与 compat export 不再反向定义正式主链
- runtime 对设备集合的正式访问已收口为只读 view / formal primitive
- outlet power 已进入正式 primitive；remaining compat seam 只能作为显式 residual 存在

### 5. API Drift Isolation / Core Boundary Prep 已完成

- `rest.device-list` / `rest.device-status` / `rest.mesh-group-status` 已在 protocol boundary 输出 canonical contract
- `AuthSessionSnapshot` 已成为 host-neutral auth/session truth；`config_flow` / `entry_auth` 不再依赖 raw login dict
- `core/__init__.py` 已不再导出 `Coordinator`；HA runtime home 继续固定在 `custom_components/lipro/coordinator_entry.py`

### 6. Phase 11 Control / Runtime / OTA / Governance 收口已完成

- `control/service_router.py` 已成为 formal control-plane service callback home，`services/wiring.py` compat shell 已删除
- runtime-access / diagnostics / status isolation 已统一到 `control/runtime_access.py` 与 formal runtime contract
- supplemental entity truth、firmware update projection 与 OTA helper cluster 已收敛为单一正式故事线
- release / CI / issue / PR / security disclosure / phase assets 已形成一致的开源治理口径

### 7. Phase 12 Type / Residual / Governance 收口已完成

- `uv run mypy` 已恢复全绿，typed runtime / REST / diagnostics 合同重新与 concrete 实现对齐
- `core.api.LiproClient`、`LiproProtocolFacade.get_device_list`、`LiproMqttFacade.raw_client` 与 `DeviceCapabilities` 已从生产 public surface 清退，不再为测试保留插件 compat 入口
- `core/api/client.py` 与 device snapshot 主链继续沿 formal boundary 收薄，未引入任何第二 orchestration story
- contributor-facing docs / config / CI / community governance 已同步到当前仓库真相，shellcheck 已纳入 lint 门禁

### 8. Phase 13 显式领域表面 / 治理守卫 / 热点边界收口已完成

- `core/device/device.py`、`state.py` 与相关测试已移除动态 `__getattr__`，设备域正式表面变成显式 property / method 集合
- `core/coordinator/orchestrator.py`、`core/api/status_service.py` 与 `core/coordinator/mqtt_lifecycle.py` 已进一步拆成更小 helper，runtime 内部协议协作者术语继续向 `protocol` 收口
- README / README_zh / CONTRIBUTING / SUPPORT / CODEOWNERS / quality-scale / devcontainer 已被 meta guards 结构化校验，治理入口不再只靠文案约定

### 9. Phase 14 旧 API Spine 终局收口与治理真源归一已完成

- `core/coordinator/coordinator.py` 已把 protocol-facing runtime ops 统一收口到 `CoordinatorProtocolService`，`Coordinator.client` 不再构成合法内部术语。
- `ScheduleApiService` 与 schedule passthrough 已退出正式主链；schedule truth 固定为 `ScheduleEndpoints` + focused helpers。
- `core/api/status_fallback.py` 与 `control/developer_router_support.py` 已承接 fallback/glue 内核；`status_service.py` 与 `service_router.py` 仅保留 public orchestration / handler 身份。
- `PUBLIC_SURFACES`、`ARCHITECTURE_POLICY`、`VERIFICATION_MATRIX`、`FILE_MATRIX`、`RESIDUAL_LEDGER`、`KILL_LIST` 与 Phase 14 closeout 资产已同步到当前仓库真相。

### 10. Phase 15 支持反馈契约 / 治理真源修补 / 可维护性跟进已完成

- developer feedback upload contract 与 local debug view 已正式分家：上传保留 `iotName` 等供应商判型标识，但匿名化 `deviceName` / `name` / `roomName` / `productName` / `keyName` / IR 资产展示名等用户自定义标签。
- `PROJECT / ROADMAP / STATE / Phase 15 assets`、README / SUPPORT / SECURITY / bug template 与 source-path guards 已讲同一条完成态故事线，不再容忍死链、版本漂移或 phase-status drift。
- support hotspot typing narrowing、tooling/security arbitration 与 residual locality governance 已完成收口；`service_router.py` 仍保持 public handler home，未重开第二条正式主链。

### 11. Phase 16 后审计收口线已规划

- `Phase 16` 已按 `3 waves / 6 plans` 落盘，目标是把终极审阅仍然成立的问题收束为一条不偏离北极星主链的收尾执行线。
- **Wave 1**：先校准 governance truth、codebase-map policy、toolchain truth 与 local DX contract，消除 Phase 15 完成态与 post-audit 规划态之间的叙事漂移。
- **Wave 2**：聚焦 control/service/config-flow 与 protocol/runtime hotspots，继续拆薄 `service_router.py`、`config_flow.py`、`client.py`、`facade.py`、`coordinator.py`，同步收紧类型与异常语义。
- **Wave 3**：收口 device/capability/entity/OTA 边界、平台测试分层、troubleshooting / release runbook / contributor navigation 等开源维护路径。
- `Phase 16` 明确禁止：重开第二条正式主链、无 gate rename campaign、与北极星无关的大规模换栈、把 residual cleanup 包装成物理重命名工程。

## Architectural Stance

本 milestone 继续遵守 `v1.0` 的北极星哲学，并对“先进性”做出更克制、但更正确的裁决：

### 1. 不为“先进”引入错误复杂度

明确不把以下内容作为默认正确答案：
- 全局 DI 容器
- 全局事件总线
- 重型 observability stack（Prometheus / OpenTelemetry）
- 全域 schema 框架替换

### 2. 先进性来自“更强正式边界”而非“更多基础设施”

本 milestone 的先进化重点是：
- boundary schema / decoder formalization
- executable architecture policy
- single telemetry exporter truth
- deterministic replay evidence
- AI-debug-ready evidence pack

### 3. HA-only 裁决

本仓库当前只服务 Home Assistant，不追求跨平台 SDK 抽象层。
因此新增能力都必须服务于：
- HA runtime 正式主链
- HA diagnostics / system health / services
- repo-local assurance / verification / AI debug tooling

## North Star 2.0 (AI Debug Ready, HA-only)

在 v1.1 / Phase 8 的裁决下，本仓库新增以下硬性原则：

1. **AI Debug Ready**：exporter / replay / evidence 产物必须结构化、稳定、可版本化、可回放。
2. **HA-only**：不为跨平台预留重型抽象层。
3. **Pull-first observability**：telemetry exporter 与 evidence pack 以 pull 为主，sources 可以维护有界摘要，但不建设事件总线。
4. **Pseudonymous-by-default**：允许 `entry_ref` / `device_ref` 这类报告内稳定、跨报告不可关联的伪匿名引用；真实标识、凭证等价物严禁进入正式输出。
5. **Real timestamps allowed**：真实时间戳允许用于 AI 调试与回放对齐，但仍受 redaction / cardinality / authority 约束。

## Success Definition

当 v1.1 完成时，应能同时回答以下问题：

- 一条 REST/MQTT 输入是由谁 decode、谁拥有 schema authority、由哪个 fixture 证明？
- 哪些架构回退会被 CI / meta guards 自动拦截？
- 当前 runtime/protocol 的关键运维信号，是否已通过单一 exporter 输出？
- 某个协议问题，能否通过 deterministic replay 在本地与 CI 复现？
- AI / 维护者是否能从统一 evidence pack 获得可调试、可追溯、已脱敏的证据？

## Scope

### In Scope

1. **Protocol boundary formalization**
   - schema/decoder family
   - authority / fixture / drift detection

2. **Executable architecture policy**
   - phase/root/surface/authority guards
   - fail-fast local/CI checks

3. **Runtime telemetry exporter**
   - 统一 exporter contracts / sinks / redaction / cardinality
   - diagnostics / system health / developer/CI 共用 truth

4. **Protocol replay harness**
   - deterministic replay corpus + driver
   - canonical / drift / telemetry assertions

5. **AI Debug evidence pack**
   - 从 exporter / replay / governance 真源 pull 证据
   - 输出 AI 可消费、结构化、脱敏的 pack

### Out of Scope

- 跨平台 SDK 适配层
- 全局事件总线 / 全局 DI 容器
- 与里程碑目标无直接关系的大规模换栈
- 为 replay / telemetry / evidence 再造第二套 production 实现

## Constraints

### Technical Constraints

- 必须保持 HA integration 的正式主链不被 replay/evidence 反客为主
- replay / evidence 只能作为 assurance/tooling layer
- 所有新增 public surface 都必须登记到治理真源
- 任何 residual/compat 必须显式记录 owner / phase / delete gate

### Product Constraints

- 不破坏现有可工作的 HA 集成主行为
- 新增能力必须可验证、可回滚、可阶段性交付
- 任何“为了 AI 调试”增加的数据，都必须先通过脱敏与 authority 仲裁

## Target Topology (v1.1 Extension)

1. **Protocol Plane**
   - `core/protocol/boundary/*`
   - `LiproProtocolFacade`
   - authority fixtures / decoders / contracts / replay evidence

2. **Runtime Plane**
   - `Coordinator`（runtime home = `custom_components/lipro/coordinator_entry.py`）
   - 正式 runtime services / orchestration / read-only runtime access

3. **Control Plane**
   - diagnostics / system health / services / runtime access / redaction
   - formal auth/session consumers（`AuthSessionSnapshot` / use-case results）

4. **Assurance Plane**
   - architecture guards / scripts / meta tests
   - telemetry exporter truth
   - replay harness
   - AI debug evidence pack exporter

5. **Governance Layer**
   - `.planning/baseline/*`
   - `.planning/reviews/*`
   - roadmap / requirements / state / phase summaries

## Derived Requirements To Enforce

v1.1 进入执行期后，新增演进必须额外满足：

- **边界 schema 只是 collaborator，不是新 root**
- **telemetry exporter 只是 observer，不得获得编排权**
- **replay harness 属于 assurance plane，不得复制生产主链**
- **AI evidence pack 属于 tooling export，不得变成第二 diagnostics / runtime root**
- **新依赖若引入，只允许局部落在 boundary plane，且必须有 authority / delete gate / rollback story**

## Phase 7.3-10 Arbitration

为避免 `07.3-08` 职责冲突，锁定以下仲裁：

- **`07.3` owns telemetry truth**
  - exporter contracts、redaction、cardinality、timestamp / pseudo-id compatibility 在此锁定；
  - 后续 phase 只能消费，不得私改字段语义。

- **`07.4` owns replay truth**
  - replay manifests、deterministic driver、replay assertions、run summary 在此锁定；
  - 不得改写 boundary authority 或 exporter truth。

- **`07.5` owns governance closeout**
  - 矩阵、owner、delete gate、evidence index、summary 在此锁定；
  - 不得实现 evidence pack exporter。

- **`08` owns AI debug packaging**
  - 只 pull `07.3/07.4/07.5` 正式输出；
  - 不得反向定义 telemetry / replay / governance 真源。

- **`09` owns residual surface closure**
  - formal public surface、compat seam、read-only runtime access 与 outlet-power primitive 在此锁定；
  - 不得重新把 live mutable runtime surface 或 child-defined contract 洗白成正式路径。

- **`10` owns API drift isolation / core-boundary prep**
  - high-drift boundary contracts、`AuthSessionSnapshot`、`core/__init__.py` 去 runtime-root 叙事在此锁定；
  - 未来宿主只能消费 formal boundary/auth/device nucleus，不得反向抽出 HA runtime 形成 second root。

## Execution Doctrine

### Planning Standard

- phase 先对齐 north-star authority，再开始落计划
- 每个 phase 先定 public surface / authority / verification，再写实现
- 先裁决，再迁移；先收口边界，再扩展能力

### Quality Standard

- 每条新主链都必须可观测、可验证、可回放
- 测试不只证明“能跑”，还要证明“没偏航”
- 文档、治理台账、验证证据与代码必须同轮同步

### Governance Standard

- 活跃真源只承认 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` → `.planning/*` → code/tests
- 任何 residual/compat 必须登记 owner、phase、delete gate
- milestone 切换前必须完成归档，不允许新旧里程碑共用一份活跃 roadmap truth

## Primary Sources

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `.planning/MILESTONES.md`
3. `.planning/milestones/v1.0-ROADMAP.md`
4. `.planning/milestones/v1.0-REQUIREMENTS.md`
5. `.planning/ROADMAP.md`
6. `.planning/REQUIREMENTS.md`
7. `.planning/STATE.md`
8. `.planning/baseline/*.md`
9. `.planning/reviews/*.md`
10. `.planning/phases/16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame/16-PRD.md`
11. `.planning/phases/16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame/16-RESEARCH.md`
12. `.planning/phases/16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame/16-VALIDATION.md`
13. `.planning/phases/16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame/16-01-PLAN.md`
14. `.planning/phases/16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame/16-02-PLAN.md`
15. `.planning/phases/16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame/16-03-PLAN.md`
16. `.planning/phases/16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame/16-04-PLAN.md`
17. `.planning/phases/16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame/16-05-PLAN.md`
18. `.planning/phases/16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame/16-06-PLAN.md`

*Last updated: 2026-03-15 after planning Phase 16*
