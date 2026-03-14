# Phase 01: Protocol Contract Baseline - Context

**Gathered:** 2026-03-12
**Status:** Ready for planning / execution
**Decision mode:** North-star arbitration by default
**Source:** `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, existing Phase 01 plans, current contract tests and fixtures

<domain>
## Phase Boundary

本阶段只做一件事：

**在大规模协议平面重构之前，锁定最小但高价值的协议契约真相。**

范围保持刻意收窄，只覆盖：
- `get_mqtt_config`
- `get_city`
- `query_user_cloud`

本阶段的目标不是扩大覆盖面，而是建立一套：
- 可重复执行
- 可回归
- 可脱离当前 `LiproClient` 形态
- 可作为 Phase 2 / 2.5 输入边界

的 protocol contract baseline。

本阶段明确**不做**：
- `LiproClient` 去 mixin 化
- `LiproProtocolFacade` 落地
- MQTT 全面 contract matrix
- capability / runtime / control plane 重构
- 全量 schema 框架引入
</domain>

<decisions>
## Implementation Decisions

### Coverage boundary
- `Phase 1` 继续保持**只锁 3 个高漂移入口**，不扩大到“能测的都先测”
- 这 3 个入口之所以成立，是因为它们同时满足：
  - 位于协议边界
  - 后续重构会直接依赖它们
  - 形态足够代表“多形态返回 + canonicalization + helper contract”
- 新入口只有在满足同等北极星价值时，才允许进入后续 phase，而不是回灌到 `Phase 1`

### Contract truth model
- `get_mqtt_config` 的 `direct` 与 `wrapped` 两种返回形态都视为**正式 contract 输入形态**
- 但它们不是两个不同的业务 contract；它们都必须归一到**同一个 canonical output**
- `Phase 1` 锁定的是：
  - 输入允许多形态
  - 输出必须单真源
  - runtime / domain / future facade 只能消费 canonical contract，而不能消费 vendor noise

### Canonicalization rule
- Contract baseline 必须围绕**canonical output** 建立，而不是围绕当前 `LiproClient`、mixin 层次或 helper 拼装顺序建立
- fixture 与 tests 只表达：
  - 哪些输入形态被接受
  - 最终 canonical output 应是什么
  - 哪些边界约束是不可变事实
- 不把“当前实现细节”误写成“长期 contract 真相”

### Fixed keys / fixed algorithms documentation
- `Phase 1` 必须承认“固定密钥 / 固定算法 / 固定字段约定”属于真实边界约束
- 但本阶段**不应**把敏感字面量、大段算法细节、可复用秘密材料复制到 fixtures、快照或 phase 文档中
- 本阶段应该记录的是：
  - 这些约束确实存在
  - 它们属于 protocol boundary 的 immutable constraints
  - 后续必须集中收口到 protocol plane
  - 所有样例、诊断、快照都必须脱敏
- 换言之：**记录约束类型与治理要求，不扩散敏感实现细节**

### Snapshot strategy
- `Phase 1 / 01-02` 的 snapshot 扩展，应该反映**contract baseline 的 canonical 视角**
- 不应该把 snapshot 做成 vendor payload 样本仓库
- snapshot 的职责是给后续 Phase 2 / 2.5 一个“结构没漂移”的长期观察面，而不是复制 fixture 原文

### Governance outputs for Phase 1 closeout
- `Phase 1` 收尾时，除了测试和 summary，必须至少同步处理以下产物：
  - `.planning/baseline/VERIFICATION_MATRIX.md`
  - `.planning/reviews/FILE_MATRIX.md`
  - `.planning/reviews/RESIDUAL_LEDGER.md`
  - `.planning/reviews/KILL_LIST.md`
- 即使其中某一项“没有新增变化”，也必须在 Phase 1 收尾 summary 里明确写出“已检查、无变化”
- 这不是额外 scope，而是北极星下的 phase 输出合同

### Handoff rule into Phase 2
- `Phase 2` 只能建立在以下条件都成立之后：
  - targeted contract tests 可独立通过
  - snapshot 已反映 canonical contract 视角
  - Phase 1 summary 说明了 baseline 的边界与非目标
  - governance outputs 已至少被检查并回写状态
- 如果上述条件未满足，`Phase 2` 不应开始大规模 protocol refactor

### Claude's discretion
- fixture 文件命名细节
- snapshot 组织形式（专用 snapshot vs 合并到现有 API snapshot）
- Phase 1 summary 的具体结构
- `KILL_LIST` 在本阶段是新增条目还是显式确认“暂无新增”
</decisions>

<specifics>
## Specific Ideas

- `get_mqtt_config` 应继续作为 Phase 1 的代表性“多形态输入 → 单 canonical 输出”样本
- `get_city` 与 `query_user_cloud` 继续作为“helper-level canonical mapping contract”样本
- 如果 Phase 1 需要补一条书面原则，应明确写成：
  - **fixtures 描述边界真相，不描述当前继承结构**
- 如果 Phase 1 需要补一条治理原则，应明确写成：
  - **Phase closeout = tests + summary + governance output check，不允许只关测试不关台账**
- 对技术边界的默认裁决：
  - 使用现有 `TypedDict` / 轻量 typed contract 模式即可
  - 不在 `Phase 1` 引入重型 schema 库
  - 不在 `Phase 1` 展开 `TraceConfig` / 深 observability 设计，这属于后续 assurance plane
</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/core/api/test_protocol_contract_matrix.py`：现有 targeted contract suite，可直接作为 Phase 1 真相载体
- `tests/fixtures/api_contracts/`：golden fixtures 已建立，可继续作为 protocol boundary fixtures 目录
- `custom_components/lipro/core/api/mqtt_api_service.py::_extract_mqtt_config_payload`：当前 `get_mqtt_config` canonicalization 的实际落点
- `custom_components/lipro/core/api/diagnostics_api_service.py::get_city`：当前 city helper contract 的实际落点
- `custom_components/lipro/core/api/diagnostics_api_service.py::query_user_cloud`：当前 cloud helper contract 的实际落点
- `tests/snapshots/test_api_snapshots.py`：现有 snapshot 承载面，可扩展到 canonical contract 视角

### Established Patterns
- protocol boundary 使用 targeted tests + sanitized fixtures，而不是端到端录制
- canonical output 优先于 vendor payload 噪音
- phase 执行输出要求 summary + 验收命令 + handoff，而不只是“测试过了”
- `.planning` 已将 `FILE_MATRIX / RESIDUAL_LEDGER / KILL_LIST / VERIFICATION_MATRIX` 升为 phase 标准输出

### Integration Points
- Phase 1 产物直接喂给 `Phase 1.5` 的 verification matrix 与 baseline asset pack
- Phase 1 的 contract truth 将成为 `Phase 2` 设计 `LiproRestFacade` 的输入边界
- `RESIDUAL_LEDGER` 需要继续把 `LiproClient` compat / mixin inheritance 视为后续待清理残留，而不是在 Phase 1 尝试解决
</code_context>

<deferred>
## Deferred Ideas

- 完整 REST protocol matrix
- MQTT 全量 contract matrix
- `LiproClient` 去 mixin 化
- `LiproProtocolFacade` / `LiproMqttFacade` 统一协议根
- dependency guards / public-surface guards 的正式自动化实现
- protocol boundary 强 schema / decoder 工具引入
- telemetry / observability / architecture enforcement 深化

这些都属于后续 phase，不回灌到 `Phase 1`。
</deferred>

---
*Phase: 01-protocol-contract-baseline*
*Context gathered: 2026-03-12 via north-star arbitration*
