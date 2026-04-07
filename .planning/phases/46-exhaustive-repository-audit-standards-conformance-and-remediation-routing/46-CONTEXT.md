# Phase 46: Exhaustive repository audit, standards conformance, and remediation routing - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning
**Source:** User request + v1.6 archive truth

<domain>
## Phase Boundary

本 phase 不是再开一轮零散重构，而是对 `lipro-hass` 做一次覆盖全仓的正式终极审阅：

- 审阅范围必须覆盖所有 Python 源码、测试、文档、配置、工作流与 `.planning` 治理真源
- 审阅维度必须覆盖架构先进性、formal root 正确性、目录结构、命名规范、热点复杂度、残留/旧代码、类型/异常预算、测试拓扑、OSS 开源成熟度、发布/支持/安全路径、文档一致性
- 产物必须形成可长期引用的正式证据，而不是 conversation-only 点评
- 审阅结论必须最终收口到 `Phase 47+` remediation roadmap、优先级矩阵与明确 verify commands

本 phase 允许生成审阅报告、评分矩阵、文件级索引、整改路线与必要的轻量治理同步；默认不做大规模实现重写，除非执行中发现必须立即修补的 current-story truth drift。

</domain>

<decisions>
## Implementation Decisions

### Audit Posture
- 审阅必须以 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 为第一裁决基线，再对照 `.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 与 baseline/review docs 进行仲裁。
- 审阅不是重新发明架构；禁止恢复第二条正式主链，禁止把 archive/phase workspace 派生资产误写成 current truth。
- 审阅必须明确区分：正式 root、child façade、adapter、helper、execution trace、promoted evidence、archive snapshot、derived map。

### Coverage Expectations
- 每个受 Git 跟踪的 Python / docs / config / workflow / governance 文件都必须被纳入某种 file-level 审阅分类，不允许留下“未看”“待以后再看”的盲区。
- Python 文件审阅至少要覆盖：formal ownership、命名、边界、依赖方向、复杂度热点、typed debt、exception semantics、旧残留回流风险。
- 测试文件审阅至少要覆盖：topicization 质量、失败定位体验、断言噪音、与治理真源的耦合度、是否仍是 mega-test hotspot。
- docs/config/workflow 审阅至少要覆盖：对外入口清晰度、OSS 成熟度、发布/支持/安全路径一致性、国际化/双语边界、maintainer cost。

### Deliverables
- 需要形成一份 master audit report，能回答“优点是什么、缺陷是什么、哪些是高优先级、为什么”。
- 需要形成 file review index / scorecard，按目录或主题聚合 strengths、gaps、risk、action。
- 需要形成正式 remediation roadmap，把后续工作拆成 `Phase 47+` 路线，而不是停留在审阅结论。
- 若发现 current truth drift，允许做最小治理修补，但修补必须服务于审阅证据可信度。

### Claude's Discretion
- 审阅分组可以按 `formal roots / tests / docs-config / governance` 或其他更优组织方式拆分，但必须保证全仓覆盖与最终汇总。
- 评分体系可使用 3 档、5 档或分数制，但必须可解释、可追溯、可复核。
- 是否生成 machine-readable 清单可由 planner 决定，但最终证据至少要有稳定 Markdown 真源。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star and current truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 单一正式主链与架构裁决第一真源
- `.planning/PROJECT.md` — 当前 archived truth + future route seed
- `.planning/ROADMAP.md` — `Phase 46` goal、requirements、depends-on 与 future milestone route
- `.planning/REQUIREMENTS.md` — `GOV-36, ARC-05, DOC-05, RES-12, TST-08, TYP-11, QLT-16` 的正式 requirement contract
- `.planning/STATE.md` — archived baseline 与 future route context

### Governance baselines
- `.planning/baseline/AUTHORITY_MATRIX.md` — authority/source-of-truth layering
- `.planning/baseline/PUBLIC_SURFACES.md` — formal public surface / archive / audit identity rules
- `.planning/baseline/DEPENDENCY_MATRIX.md` — cross-plane dependency rules
- `.planning/baseline/VERIFICATION_MATRIX.md` — promoted phase evidence 与 verification contract

### Review ledgers and audit anchors
- `.planning/reviews/FILE_MATRIX.md` — file-level governance truth
- `.planning/reviews/RESIDUAL_LEDGER.md` — residual / type / exception sustainment debt inventory
- `.planning/reviews/KILL_LIST.md` — delete / retire dispositions
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` — promoted phase evidence allowlist
- `.planning/reviews/V1_6_EVIDENCE_INDEX.md` — latest closeout evidence pointer
- `.planning/v1.6-MILESTONE-AUDIT.md` — latest shipped verdict home

### Architecture and maintainer surfaces
- `docs/developer_architecture.md` — current codebase architecture explanation
- `docs/README.md` — docs entry topology / active vs archive boundary
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` — release/support/security operational contract
- `CONTRIBUTING.md` — contributor path and open-source posture
- `README.md`
- `README_zh.md`
- `SUPPORT.md`
- `SECURITY.md`

### Audit focus hints from existing evidence
- `.planning/phases/41-full-spectrum-architecture-code-quality-and-open-source-audit/41-AUDIT.md` — previous full-spectrum audit baseline
- `.planning/phases/41-full-spectrum-architecture-code-quality-and-open-source-audit/41-REMEDIATION-ROADMAP.md` — already executed remediation route that became phases 42-45
- `.planning/phases/42-delivery-trust-gates-and-validation-hardening/42-SUMMARY.md` — v1.6 delivery trust evidence
- `.planning/phases/43-control-services-boundary-decoupling-and-typed-runtime-access/43-SUMMARY.md` — runtime/control boundary evidence
- `.planning/phases/44-governance-asset-pruning-and-terminology-convergence/44-SUMMARY.md` — governance/noise/terminology evidence
- `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-SUMMARY.md` — hotspot/type/benchmark evidence

</canonical_refs>

<specifics>
## Specific Ideas

- 契约者要求“每一处细节都要看到”，因此执行方案必须显式切分审阅波次，保证整个仓库被扫描，而不是只看热点文件。
- 子代理要充分利用，但主代理必须做仲裁与收敛，避免多份报告互相冲突。
- 输出需要兼顾：总览结论、分主题深审、文件级索引、后续 phase 计划。
- 推荐优先留意的三个高杠杆主题：formal root 热点瘦身与边界再裁决、mega-test / verification topology 再 topicize、类型/异常预算扩围 + 治理真源压缩审阅。

</specifics>

<deferred>
## Deferred Ideas

- 大规模代码重构、hotspot 物理拆分、mega-test 真正 topicization、repo-wide typed debt 清零，都应在 `Phase 47+` 按 remediation roadmap 落地。
- 本 phase 若无 current-story truth drift，不主动触碰 production 行为。

</deferred>

---

*Phase: 46-exhaustive-repository-audit-standards-conformance-and-remediation-routing*
*Context gathered: 2026-03-20 via user-driven audit charter*
