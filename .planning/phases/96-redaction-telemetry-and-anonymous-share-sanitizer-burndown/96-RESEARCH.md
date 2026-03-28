# Phase 96: Redaction, telemetry, and anonymous-share sanitizer burndown - Research

**Researched:** 2026-03-28
**Domain:** shared redaction truth / telemetry sanitization / anonymous-share convergence
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- `Phase 96` 只覆盖 `HOT-41` 与 `SEC-02`，目标是继续烧掉 shared redaction / sanitizer 热点，而不是另起一条 diagnostics / telemetry / anonymous-share 的平行主链。
- shared redaction registry 是唯一裁决源；任何新 helper 都只能消费 `custom_components/lipro/core/utils/redaction.py`，不能再私造 secret-like key truth。
- complexity burn-down 必须通过 inward split / pure helper / normalized contract 完成，不能用新 wrapper 或新 outward root 掩盖热点。
- diagnostics / telemetry / anonymous-share 的 redaction 与 sanitizer 语义必须可由 focused tests 直接证明，且 fail-closed 规则不能放宽。
- 正式 formal homes 不可漂移：`custom_components/lipro/control/redaction.py` 仍是 diagnostics/control redaction home；`custom_components/lipro/core/telemetry/exporter.py` 仍是 telemetry exporter home；`custom_components/lipro/core/anonymous_share/manager.py` 仍是 anonymous-share aggregate manager home。

### the agent's Discretion
- 可以继续把纯 helper inward split 到现有 sibling/support files，但不要创造新的 plane root。
- 可以新增 focused tests 或补齐现有 tests 的 concern-local cases，但不要再造 mega guard；route/governance freeze 继续留给 `Phase 97`。
- 若 `manager.py` / `exporter.py` / `redaction.py` 的热点可以通过同文件私有 helper 明显变薄，优先保持文件 owner 不变，再决定是否借现有 support modules 承载稳定 support logic。

### Deferred Ideas (OUT OF SCOPE)
- `.planning/*`、baseline/review docs、route smoke、open-source contract freeze 属于 `Phase 97`，本 phase 不抢跑治理收官。
- 不做 release/public-entry 层面的开源文档整改；这些属于后续 governance/open-source 合同同步。
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HOT-41 | `control/redaction.py`、`core/telemetry/exporter.py`、`core/anonymous_share/manager.py` 及相邻 helpers 的热点复杂度继续 inward split / shrink，formal home 不漂移。 | `## Hotspot Findings`、`## Recommended Plan Decomposition` |
| SEC-02 | diagnostics / anonymous-share / telemetry / control redaction 路径必须继续对齐 shared redaction registry 与 fail-closed sanitizer contract。 | `## Shared Contract Findings`、`## Validation Architecture` |
</phase_requirements>

## Summary

`Phase 96` 的本质不是“再写一层 redaction wrapper”，而是把 **三条已经存在的 sanitization 逻辑** 讲成 **同一条 shared-policy 故事**。当前仓库的 shared classifier 已经很成熟：`custom_components/lipro/core/utils/redaction.py` 提供 key normalization、secret-like key detection、literal/text redaction 与 sink-specific marker palette；但 diagnostics/control、telemetry、anonymous-share 仍各自保留一段较厚的递归/预算/结构保持逻辑。问题不在“缺 redaction 功能”，而在 **热点仍然局部过厚，且不同 plane 的 fail-closed 细节还没有完全 topicize 到最合适的 helper home**。

最明显的热点有三处：
- `custom_components/lipro/control/redaction.py` 只有 148 行，但 `redact_property_value()` 同时承担 key-classification、JSON-string parse、list/dict recursion、literal/text masking 与 marker selection，属于典型“短文件大热点”。
- `custom_components/lipro/core/telemetry/exporter.py` 239 行里同时承担 snapshot export、reference alias/cache、mapping traversal、string redaction、marker summary budget 与 truncation 规则，formal home 正确但 sanitizer choreography 仍可继续 inward split。
- `custom_components/lipro/core/anonymous_share/manager.py` 虽然已经把 submit / support 拆到 `manager_submission.py` 与 `manager_support.py`，但本体仍 459 行，聚合视图、state facade、report build、submit outcome、cache load/save 与 threshold wiring 全部堆在同一 formal owner 上，仍有继续变薄空间。

最优策略不是横向新建“统一 sanitizer service”，而是 **沿当前 formal homes inward split**：
1. 先把 diagnostics/control redaction 里的递归/JSON-string 分支压到局部纯 helper；
2. 再把 telemetry exporter 的 sanitize/reference/budget 细节拆成可单测的私有 helper 或现有 sibling collaborator；
3. 最后继续收薄 anonymous-share manager outward shell，让 aggregate/report/submit state 继续留在 support/submission 层，manager 只保留 formal orchestration 与 typed facade。

## Hotspot Findings

### 1. `custom_components/lipro/control/redaction.py`
- 主要热点是 `redact_property_value()`；它同时处理 key fail-closed、嵌套 dict/list、JSON 字符串递归解析、literal redaction 与 text redaction。
- 当前实现已经正确依赖 shared utilities，但 helper 颗粒度不足，后续任何 diagnostics redaction 增量都容易再次把这个函数变厚。
- 这里最值得抽出的不是 public API，而是：
  - string-path decision helper
  - JSON-string parse + round-trip helper
  - nested mapping/list traversal helper
  - secret-key fail-closed gate helper

### 2. `custom_components/lipro/core/telemetry/exporter.py`
- `export_snapshot()`/`_sanitize_mapping()`/`_sanitize_value()`/`_build_reference()` 构成一个小型 sanitizer pipeline。
- 当前问题不是 root 错位，而是 export + sanitize + budget summary 混在一个类里，导致 `RuntimeTelemetryExporter` 既像 orchestrator，又像 sanitizer kernel。
- 这里最值得收口的是：
  - reference resolution / caching helper
  - string sanitization + summary budget helper
  - sequence/mapping traversal helper
  - entry-ref resolution helper 与 main export orchestration 进一步解耦

### 3. `custom_components/lipro/core/anonymous_share/manager.py`
- 该文件虽然已经比早期版本好很多，但依旧是 phase96 最大热点：state facade、aggregate/scoped view、report build、submit facade、load/save cache、pending logic 全部被类内属性包装包住。
- `manager_support.py` 与 `manager_submission.py` 已经存在，说明最优路线不是再建新 support file，而是继续把 state/submit/report/persistence 细节向这两个现有 support homes 收拢。
- 这里最值得继续收口的是：
  - `build_report()` / aggregate payload selection 的局部 support helper化
  - cache load/save / pending state facade 的进一步薄化
  - `submit_report()` / `submit_if_needed()` outward shell 继续压到 typed outcome story 上

## Shared Contract Findings

- shared redaction truth 现在分三层：
  - `core/utils/redaction.py`：唯一 classifier / marker / alias / literal/text redaction 真源；
  - `control/redaction.py`：diagnostics/control 面上的结构化 redaction adapter；
  - `core/anonymous_share/sanitize.py` 与 `core/telemetry/exporter.py`：各自 sink-specific sanitizer。
- 当前最大风险不是“某个字段没被遮盖”，而是 **同一类 secret-like key 在三个路径里再次被不同局部规则解释**。因此 phase96 的目标应是减少“自己判断敏感字段”的逻辑，把所有 key semantics 尽量收回 shared registry。
- sink-specific marker palette 必须保留差异：diagnostics 使用 `**REDACTED**`，anonymous-share / telemetry 使用 share markers；phase96 只统一 classifier 与 traversal/fail-closed contract，不统一展示字符串。

## Best-Practice Notes

- 对照成熟开源项目的安全实践，本 phase 应继续遵守 **shared classifier + sink-local presentation** 模式，而不是单纯复用一个全局 marker。
- 对照良好的可维护性实践，热点 burn-down 的标准不是“文件数变多”，而是：主函数更短、职责更清楚、测试更能按 concern family 解释行为。
- 对照北极星架构，本 phase 只允许 inward split，不允许任何 control/runtime/protocol new root 或 cross-plane shortcut。

## Recommended Plan Decomposition

| Plan | Wave | Depends on | Scope | Output |
|------|------|------------|-------|--------|
| `96-01` diagnostics/control redaction inward split | Wave 1 | none | 收薄 `control/redaction.py`，把递归/JSON-string/fail-closed helper 纯化，并补 focused diagnostics redaction proof | `control/redaction.py` + diagnostics redaction tests |
| `96-02` telemetry exporter sanitizer topicization | Wave 1 | none | 把 exporter 的 sanitize/reference/budget 流水线 inward split 到私有 helper 或现有 sibling support，同时保持 exporter 为唯一 formal home | `core/telemetry/exporter.py` + telemetry integration/focused tests |
| `96-03` anonymous-share manager shell slimming | Wave 2 | `96-01`, `96-02` | 继续把 manager outward shell 压薄，让 report/submit/persistence state 细节更多落在已有 support/submission/sanitize homes，并补 aggregate/scoped fail-closed proof | `manager.py` / `manager_support.py` / `manager_submission.py` / `sanitize.py` + focused anonymous-share tests |

**Why this is optimal:** Wave 1 先分别削掉 control 与 telemetry 两个最独立的 sanitizer hotspots；Wave 2 再把 anonymous-share manager 对齐到已经清晰的 shared contract，上下游语义更稳定，且不需要反复改同一套 tests。

## Minimal Sufficient Validation Checklist

- `uv run pytest -q tests/core/test_diagnostics_redaction.py tests/core/test_diagnostics.py tests/core/test_diagnostics_config_entry.py tests/core/test_diagnostics_device.py`
- `uv run pytest -q tests/integration/test_telemetry_exporter_integration.py tests/core/anonymous_share/test_observability.py tests/core/test_anonymous_share_cov_missing.py`
- `uv run ruff check custom_components/lipro/control/redaction.py custom_components/lipro/core/telemetry/exporter.py custom_components/lipro/core/anonymous_share/manager.py custom_components/lipro/core/anonymous_share/manager_support.py custom_components/lipro/core/anonymous_share/manager_submission.py custom_components/lipro/core/anonymous_share/sanitize.py tests/core/test_diagnostics_redaction.py tests/integration/test_telemetry_exporter_integration.py tests/core/test_anonymous_share_cov_missing.py`
- `uv run mypy custom_components/lipro/control/redaction.py custom_components/lipro/core/telemetry/exporter.py custom_components/lipro/core/anonymous_share/manager.py custom_components/lipro/core/anonymous_share/manager_support.py custom_components/lipro/core/anonymous_share/manager_submission.py custom_components/lipro/core/anonymous_share/sanitize.py`

## Validation Architecture

### Key files already available
- `custom_components/lipro/core/utils/redaction.py` — shared redaction classifier / marker source
- `custom_components/lipro/control/redaction.py` — diagnostics/control sink adapter
- `custom_components/lipro/core/telemetry/exporter.py` — telemetry export + sanitize formal home
- `custom_components/lipro/core/anonymous_share/sanitize.py` — anonymous-share sink sanitizer helper home
- `custom_components/lipro/core/anonymous_share/manager_support.py` — manager state/report mechanics support home
- `custom_components/lipro/core/anonymous_share/manager_submission.py` — manager submit-flow support home

### Wave 0 gaps
- 无新增 framework 缺口；当前仓库已有足够 focused tests 与 static gates 支撑 Phase 96。
- 真正缺的是：把 shared redaction policy 如何被 diagnostics / telemetry / anonymous-share 三条路径共同消费，写成更薄、更易验证的实现。

## Sources

### Primary (HIGH confidence)
- `AGENTS.md`
- `.planning/STATE.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/phases/96-redaction-telemetry-and-anonymous-share-sanitizer-burndown/96-CONTEXT.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `custom_components/lipro/core/utils/redaction.py`
- `custom_components/lipro/control/redaction.py`
- `custom_components/lipro/core/telemetry/exporter.py`
- `custom_components/lipro/core/anonymous_share/manager.py`
- `custom_components/lipro/core/anonymous_share/manager_support.py`
- `custom_components/lipro/core/anonymous_share/manager_submission.py`
- `custom_components/lipro/core/anonymous_share/sanitize.py`
- `custom_components/lipro/diagnostics.py`
- `tests/core/test_diagnostics_redaction.py`
- `tests/integration/test_telemetry_exporter_integration.py`
- `tests/core/test_anonymous_share_cov_missing.py`
- `tests/core/anonymous_share/test_observability.py`

## Metadata

**Confidence breakdown:**
- Hotspot diagnosis: HIGH — 直接来自当前文件结构、函数分布与 formal-home baseline。
- Plan decomposition: HIGH — 与 `ROADMAP.md` 的 `Phase 96` 目标、requirements 与现有 support topology 一致。
- Exact helper boundaries during implementation: MEDIUM — 需要在执行时根据 touched tests 与实际局部分支形状微调。

**Research date:** 2026-03-28
**Valid until:** `Phase 96` 计划创建完成或 active-route 切换（以先到者为准）
