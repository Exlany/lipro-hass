# Phase 01 Immutable Constraints

**Purpose:** 记录 Phase 01 已确认的协议边界不可变事实，只保留约束类型、不可变原因与治理规则，不扩散敏感实现细节。
**Status:** Baseline locked
**Updated:** 2026-03-12

## Scope

本台账只覆盖 Phase 01 锁定的三条高价值协议边界：

- `get_mqtt_config`
- `get_city`
- `query_user_cloud`

它描述的是 **canonical contract baseline**，不是完整 vendor API 规范，也不是当前 `LiproClient` / mixin 结构说明。

## Immutable Constraint Classes

| Constraint type | What stays immutable | Why it is immutable | Governance rule |
|---|---|---|---|
| Credential field class | `get_mqtt_config` canonical output 仍需表达 access/secret 类语义字段 | 上游协议与后续 façade 都依赖这组语义槽位，而不是依赖当前 transport 包裹形式 | fixture / snapshot / summary 只保留脱敏占位值；秘密材料继续留在 runtime 配置或协议实现内部 |
| Envelope + field-shape class | `get_mqtt_config` 允许 `direct` / `wrapped` 两种输入形态，但必须归一到单一 canonical output；`get_city` 与 `query_user_cloud` 保持 helper-level mapping contract | 这是调用边界真相，Phase 2/2.5 重构时不能把 vendor noise 当作新 contract 真相 | 用 targeted tests + canonical snapshots 锁边界；不得把当前继承层次写成长期 contract |
| Fixed request-form convention | `query_user_cloud` 的空字符串请求形态、`get_city` 的空 mapping 请求形态属于现有边界约定 | 上游 endpoint 已对这些请求形态形成稳定期待，重构只能封装不能改写 | 保持 helper seam 断言；若未来要变更，必须先更新 baseline fixtures / tests / summaries |
| Algorithm / signing category | 协议面存在固定算法类别、签名类别、派生步骤等真实约束 | 这些约束直接影响互通性，但复制细节会扩大敏感实现表面 | Phase 01 只记录“约束存在且必须集中收口到 protocol plane”；不在 fixture / snapshot / phase docs 中抄录具体算法细节 |
| Path / topic convention | 固定 path、topic、包裹族类属于协议路由事实 | 调用链和 future façade 需要围绕这些稳定标识建模 | 文档只记录“存在此类约束”；具体常量沿用代码内既有公开常量，不在台账中重复扩散 |

## Sanitization Rules

- 所有 fixture、snapshot、summary 只允许使用脱敏占位值，不允许写入真实密钥、真实 token、真实 broker/topic 标识。
- Snapshot 只展示 canonical output 和接受的输入形态，不复制 vendor payload 原文。
- Summary 只记录约束类型、影响范围与治理要求，不记录可复用秘密材料。
- 若后续 phase 需要补充实现细节，应收口到 protocol plane 代码与受控测试中，而不是扩散到 `.planning` 叙述文档。

## Handoff Implications

- **Phase 1.5** 消费本台账来构建 baseline asset pack 与 verification matrix，不再依赖对话记忆判断“哪些约束不能漂移”。
- **Phase 2** 在执行 REST façade / demixin 时，必须保持已锁定的 accepted input shapes 与 canonical outputs，不得把 mixin 组织方式当成 contract。
- **Phase 2.5** 在统一 protocol root 时，需要把算法/route/topic 这类不可变约束集中收口，但继续遵守脱敏治理规则。

## Non-Goals

- 不扩展为完整 vendor API 手册
- 不抄录敏感字面量、算法细节、可复用密钥材料
- 不提前实现 `LiproRestFacade`、`LiproProtocolFacade` 或其它 Phase 2+ 结构
