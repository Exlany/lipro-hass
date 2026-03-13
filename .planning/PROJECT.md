# Lipro-HASS North Star Rebuild

## Current Milestone: v1.1 Protocol Fidelity & Operability

**Goal:** 把 `protocol truth`、`architecture policy`、`runtime telemetry export`、`replay evidence`、`ai-debug evidence pack` 五条演进线统一纳入北极星主链，进入“可保真、可观测、可仲裁、可回放、可给 AI 调试/分析”的下一里程碑。

**Target features:**
- protocol boundary schema / decoder family，仅在协议边界局部增强，不扩散第二真源
- stronger architecture enforcement，把 plane/root/surface/authority 规则升级为更强自动守卫
- runtime telemetry exporter，把当前 snapshot/diagnostics 进化为正式导出面
- protocol replay / simulator harness，把逆向协议证据沉淀为可重复回放的 assurance asset
- AI debug evidence pack：把 telemetry/replay/边界库存统一导出为“可给 AI 分析”的脱敏证据包

## North Star 2.0 Addendum (HA-only)

在 `v1.1` 范围内，本项目继续坚持“只服务 Home Assistant”的最佳终态：先进性不来自重型框架，而来自 **边界契约化 + 单主链收敛 + 可观测/可回放证据**。

- **AI 可分析优先**：telemetry/export/replay/evidence 的产物必须机器友好（结构化、稳定 schema、可版本化、带时间戳、带事件序列），同时严格脱敏。
- **Exporter 以 pull 为主**：exporter 只读 protocol/runtime sources；sources 可维护有界事件 ring-buffer，避免把 exporter 变成事件总线。
- **伪匿名化优先**：允许输出“伪装字符/伪匿名标识”（报告内稳定、跨报告不可关联），禁止 token/secret/`password_hash` 等凭证等价物进入任何 sink。

**Shipped milestone:** `v1.0 North Star Rebuild` 已于 `2026-03-13` 归档，见 `.planning/MILESTONES.md` 与 `.planning/milestones/v1.0-ROADMAP.md`。

## What This Is

这是一个面向 **Home Assistant** 的 `Lipro` 智能家居平台自定义集成重构项目。

本项目不是“在旧代码上继续打补丁”，而是以 **脱离历史成本约束的终态设计基准** 为前提，重新定义这类 HA 插件在协议边界、运行时编排、领域建模、控制平面、保障平面上的最佳实现方式，再分阶段把现有仓库收敛到该目标。

它有几个不可回避的现实边界：

- 上游接口并非官方公开 SDK，而是基于 App 逆向与抓包整理出的协议集合
- 部分签名算法、请求字段、固定密钥与设备约定属于供应商协议事实，而不是本项目可自由设计的内容
- 运行环境必须服从 Home Assistant 的集成模型、生命周期、质量尺度与用户体验约束
- 代码与测试代码都要一起现代化，不能出现“生产代码新架构、测试仍围着旧结构打补丁”的双轨状态

## Core Value

把 `lipro-hass` 收敛成一个：

- **终态明确**：先定义正确架构，再安排迁移
- **边界清晰**：供应商协议、HA 适配、运行时编排、领域能力、保障约束各归其位
- **实现优雅**：显式组合、单一正式主链、低认知负担、易推断
- **可持续演进**：任何迁移残留都有台账、删除条件和最终去向
- **全仓一致**：全部 `412` 个 Python 文件均纳入治理矩阵，包含 `165` 个测试文件

## North Star Product Framing

### Product Type

- Home Assistant custom integration
- Reverse-engineered protocol adapter for Lipro cloud / IoT / MQTT
- Coordinator-centered runtime system with domain projections to HA entities/platforms

### Users and Maintainers

- **终端用户**：希望稳定接入 Lipro 设备、状态同步及时、命令反馈可靠
- **维护者**：需要低心智负担地定位协议问题、运行时问题、能力模型问题与 HA 生命周期问题
- **重构执行者**：需要明确知道哪些文件保留、哪些迁移、哪些删除、哪些仅作 compat shell

## Architectural North Star

### Formal Planes

1. **Protocol Plane**
   - 终态唯一正式根：`LiproProtocolFacade`
   - 子门面：`LiproRestFacade`、`LiproMqttFacade`
   - 职责：协议 IO、认证恢复、请求策略、归一化、compat adapter 收口

2. **Runtime Plane**
   - 终态唯一编排根：`Coordinator`
   - 装配根：`RuntimeOrchestrator`
   - 回调注入边界：`RuntimeContext`
   - 运行时组件：命令、设备刷新、状态写入、MQTT 生命周期、状态轮询、调优

3. **Domain Plane**
   - 单一能力真源
   - 统一设备聚合、能力快照、命令模型、属性描述
   - 平台层只做投影，不二次定义领域规则

4. **Control Plane**
   - `config entry`、`options`、`diagnostics`、`system health`、`services`、`reauth` 形成单一叙事
   - 控制面通过稳定 public surface 与运行面对接

5. **Assurance Plane**
   - 契约测试、架构守卫、快照、集成验证、质量门禁、残留台账
   - 目标不是“有测试”，而是“能裁决架构回退”

### Non-Negotiable Design Laws

- 显式组合优于继承聚合
- 单一正式主链优于多套并行合法入口
- 协议边界归一化优于原始 payload 内部漫游
- 领域单一真源优于平台/实体重复表达
- compat 只允许作为**显式、可计数、可删除**的过渡残留
- 历史债只影响迁移顺序，不参与终态正确性裁决

## Immutable Constraints

以下约束必须被承认、隔离并制度化，而不是在代码中零散扩散：

1. **逆向协议约束**
   - 请求路径、字段、密钥、签名算法、设备 topic 规则可能是固定事实
   - 这些约束必须集中在 protocol boundary，不得扩散进 entity / service / runtime 内部

2. **Home Assistant 约束**
   - 必须遵循 config flow、DataUpdateCoordinator、entity lifecycle、diagnostics redaction、quality scale 等最佳实践
   - 不允许为了“更先进”而违背 HA 集成生态的自然边界

3. **安全约束**
   - 固定密钥与敏感字段不可出现在日志、诊断、测试快照明文中
   - 所有协议样例必须经过脱敏与固定化处理

4. **演进约束**
   - 不接受“新架构 + 旧兼容 + 半迁移中间态”长期并存
   - 每个阶段都必须更新治理矩阵、残留台账与删除触发条件

## Baseline Asset Package

为了让 `.planning/` 不只是“强路线图”，还成为“强基准”，本项目将以下资产视为正式工程真源：

- `.planning/baseline/TARGET_TOPOLOGY.md` — 五平面目标拓扑、正式组件与目标目录映射
- `.planning/baseline/DEPENDENCY_MATRIX.md` — 允许/禁止的依赖方向矩阵
- `.planning/baseline/PUBLIC_SURFACES.md` — 各平面的 canonical public surfaces
- `.planning/baseline/VERIFICATION_MATRIX.md` — requirement → artifact → test → doc → phase 的验证闭环
- `.planning/baseline/AUTHORITY_MATRIX.md` — 文档、fixtures、generated、implementation 的权威来源与同步方向

这些资产必须早于大规模重构落地，作为 Phase 1.5 的正式交付物。

## Required Governance Artifacts

除基准资产外，以下治理产物同样属于正式工程真源：

- `.planning/reviews/FILE_MATRIX.md` — 全仓 Python 文件治理矩阵
- `.planning/reviews/RESIDUAL_LEDGER.md` — 迁移残留与退出条件台账
- `.planning/reviews/KILL_LIST.md` — 已裁定应删除对象的正式清单

每个 phase 完成时，必须显式回写这三类治理产物或说明“本 phase 无新增变化”。

## Success Definition

本项目完成时，应满足以下终态信号：

- `LiproClient` 不再是正式架构根，最多只剩短期 compat shell，最终清零
- `REST / MQTT` 统一收口到 `LiproProtocolFacade`
- control / runtime / domain / assurance 各平面拥有单一正式 public surface
- 新增协议变体时，只需要在 boundary family 内扩展，不再向 runtime/entity/control 泄漏原始形态
- 架构回退、兼容层回流、边界漂移、未登记残留，都会被 meta guards / CI / ledger 明确阻断

## Derived Requirements To Enforce

v1.1 进入执行期后，新增演进必须额外满足：

- **边界 schema 只是 collaborator，不是新 root**
- **telemetry exporter 只是 observer，不得获得编排权**
- **replay harness 属于 assurance plane，不得复制生产主链**
- **新依赖若引入，只允许局部落在 boundary plane，且必须有 authority / delete gate / rollback story**

## Out of Scope

- 为了“更先进”而引入全局事件总线、全局 DI 容器、全域重型 schema 框架
- 复制第二套 protocol/runtime truth 给 simulator、fixtures、diagnostics 或 exporter
- 与北极星口径无关的大规模换栈

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
10. `docs/FINAL_CLOSEOUT_REPORT_2026-03-13.md`

*Last updated: 2026-03-13 after v1.0 archival and v1.1 milestone initialization*
