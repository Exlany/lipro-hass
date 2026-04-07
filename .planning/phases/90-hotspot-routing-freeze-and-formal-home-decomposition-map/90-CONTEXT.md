# Phase 90: Hotspot routing freeze and formal-home decomposition map - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning
**Source:** Auto context synthesis from repo-wide architecture audit and current codebase maps

<domain>
## Phase Boundary

`Phase 90` 的职责不是提前实现 `Phase 91 -> 93` 的重构，而是把本轮 repo-wide 终审结论压缩成一份 **可 machine-check、可回写 current-route truth、可直接指导后续计划与执行** 的 hotspot decomposition map。

本 phase 只做四件事：
- 冻结 `HOT-40` 涉及的热点 formal-home 归属与 inward-split 边界；
- 明确哪些模块继续是 protected thin shell / projection，不允许重新吸附 orchestration；
- 明确 residual / compat / naming debt 的 delete-gate 规则与后续 phase owner；
- 把上述结论同步到 planning / baseline / review truth，避免后续计划又长出第二条故事线。

本 phase **不**提前实现以下内容：
- `ARC-24` / `TYP-23` 的 typed boundary hardening 实施；
- `SEC-01` / `TST-29` 的 redaction convergence 与 assurance topicization；
- `QLT-37` 的最终质量冻结与全量 quality story 收口。

</domain>

<decisions>
## Implementation Decisions

### Hotspot ownership freeze
- **D-01:** `custom_components/lipro/core/coordinator/runtime/command_runtime.py`、`custom_components/lipro/core/api/rest_facade.py`、`custom_components/lipro/core/api/request_policy.py`、`custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py`、`custom_components/lipro/core/anonymous_share/manager.py` 全部继续保留为 **formal homes**，不在 `Phase 90` 叙述为 thin shell 或 file-level delete target。
- **D-02:** 这些热点的正确演进路径统一为 **保留 outward home + 沿 sibling/support family inward split**；不得通过新增 public root、compat shell、second control story、second runtime story 或 helper-owned truth 来“拆大文件”。

### REST and runtime decomposition line
- **D-03:** `custom_components/lipro/core/api/rest_facade.py` 继续是 canonical REST child façade composition home；`custom_components/lipro/core/api/client.py` 继续只是 stable import shell，不得重新长成第二 REST/public root。
- **D-04:** `custom_components/lipro/core/api/request_policy.py` 独占 `429 / busy / pacing` policy truth；generic backoff、mapping/auth-aware retry orchestration 不得回流成第二 policy home，仍分别归于 `request_policy_support.py`、`request_gateway.py` 与 `transport_executor.py`。
- **D-05:** `custom_components/lipro/core/coordinator/runtime/command_runtime.py` 继续拥有 command orchestration、failure summary、confirmation coordination；新纯 helper 或 stage-specific 逻辑只允许下沉到 `custom_components/lipro/core/coordinator/runtime/command/*` 相邻家族。
- **D-06:** `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` 继续拥有 MQTT runtime orchestration、background-task ownership 与 failure summary；message/dedup/reconnect/connection 继续留在 `custom_components/lipro/core/coordinator/runtime/mqtt/*`，不得再外扩第二运行根。

### Thin-shell protection line
- **D-07:** `custom_components/lipro/__init__.py`、`custom_components/lipro/control/runtime_access.py`、`custom_components/lipro/entities/base.py`、`custom_components/lipro/entities/firmware_update.py` 在本里程碑中统一视为 **protected thin adapter / projection / typed access** surfaces；任何后续计划都不得把新的 orchestration、protocol internals 或 cross-plane truth 上浮回这些 outward shells。
- **D-08:** 若后续 phase 需要切薄这些文件，只能通过 inward split 或 narrower typed projection 实现，不能通过 public surface 漂移、module alias、second helper story 达成“看起来更薄”。

### Anonymous-share and redaction boundary
- **D-09:** `custom_components/lipro/core/anonymous_share/manager.py` 继续是 protocol-plane formal home；submit flow 继续以 `custom_components/lipro/core/anonymous_share/manager_submission.py` 为 inward collaborator，不在 `Phase 90` 把 ownership 迁移到 control/redaction family。
- **D-10:** diagnostics / anonymous-share redaction contract convergence 被登记为 `SEC-01 / Phase 92` 的前置语义约束；`Phase 90` 只冻结 home 与边界，不提前重写 redaction topology。

### Delete-gate and execution sequencing
- **D-11:** 若 `Phase 90` 审阅中发现新的 compat / naming / residual shell，只允许以显式 `owner + target phase + delete gate + evidence pointer` 的形式登记到 review ledgers；默认不把本轮 5 个 hotspots 写成 delete target。
- **D-12:** 本里程碑执行顺序固定为：`Phase 90` 冻结 map → `Phase 91` 处理 protocol/runtime + typing → `Phase 92` 处理 control/entity/redaction + focused regressions → `Phase 93` 做 assurance topicization 与质量冻结；不得跳过 map 直接做自由式 repo-wide 手术。

### the agent's Discretion
- 可在 `Phase 90` 中增加更精细的 hotspot 子分类（如 stage host、policy owner、aggregate manager、protected thin shell），前提是这些分类不改变 formal-home ownership。
- 可把 repo-wide 终审发现浓缩为 risk ranking、evidence matrix 或 freeze table，只要长期真源仍回写到 planning/baseline/review docs。
- 可把 `.planning/codebase/*.md` 的现有审阅结论作为导航输入，但不能让它们越权成为新的 authority chain。

</decisions>

<specifics>
## Specific Ideas

- 本轮 repo-wide 审阅已经确认：当前最需要治理的不是“还有没有遗漏的 archived wording”，而是少数仍然偏厚、但 formal home 已经正确的大文件与边界家族。
- `command_runtime.py`、`mqtt_runtime.py`、`rest_facade.py`、`request_policy.py`、`anonymous_share/manager.py` 都属于 **formal homes with further inward-split budget**，不是“删掉就赢了”的对象。
- 用户的全仓终审诉求在本里程碑中的正确落点是：先把所有热点与壳层的裁决冻结为唯一 current truth，再让后续 phases 以该真相为约束做彻底重构，而不是边改边改写故事。
- 保护线必须同时锁住：`__init__.py`、`runtime_access.py`、`entities/base.py`、`entities/firmware_update.py` 不能因为“顺手拆分”重新长出 orchestration、service backdoor 或 raw vendor payload projection。

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star and current-route truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 北极星终态架构与单一正式主链原则。
- `AGENTS.md` — 当前工作树级执行契约与工具/验证规范。
- `lipro-hass/AGENTS.md` — 仓库级 formal-home、thin-shell、baseline/review 回写规则。
- `.planning/PROJECT.md` — `v1.25` 里程碑意图、north-star fit 与 current-route truth。
- `.planning/ROADMAP.md` — `Phase 90 -> 93` 边界、success criteria 与 phase sequencing。
- `.planning/REQUIREMENTS.md` — `HOT-40` / `ARC-24` / `TYP-23` / `SEC-01` / `TST-29` / `QLT-37` 的分配关系。
- `.planning/STATE.md` — 当前里程碑位置、默认 next command 与 continuity anchors。
- `.planning/MILESTONES.md` — latest archived baseline 与 current-route handoff 历史真值。

### Baseline and review truth
- `.planning/baseline/PUBLIC_SURFACES.md` — public surface 与 protected outward homes。
- `.planning/baseline/DEPENDENCY_MATRIX.md` — plane/dependency truth，防止 second story 回流。
- `.planning/baseline/VERIFICATION_MATRIX.md` — phase acceptance / handoff 的正式验证基线。
- `.planning/baseline/AUTHORITY_MATRIX.md` — authority order 与 external-boundary 真源约束。
- `.planning/reviews/FILE_MATRIX.md` — hotspot 文件 ownership、formal-home / thin-shell / support-only 裁决。
- `.planning/reviews/RESIDUAL_LEDGER.md` — residual / delete-gate 当前台账与已关闭条目。
- `.planning/reviews/KILL_LIST.md` — 可删目标与 delete-gate 管理。
- `.planning/reviews/V1_24_EVIDENCE_INDEX.md` — 当前 latest archived baseline 的 pull-only evidence index。
- `.planning/v1.24-MILESTONE-AUDIT.md` — `v1.24` closeout 结论与 carry-forward 判断。

### Repo-wide codebase review inputs
- `.planning/codebase/ARCHITECTURE.md` — 当前五平面结构、formal homes 与主要 data flow。
- `.planning/codebase/STRUCTURE.md` — 目录归属、support-only split 模式与 hotspot 清单。
- `.planning/codebase/CONCERNS.md` — repo-wide concern ranking、热点/风险/残留证据。
- `.planning/codebase/CONVENTIONS.md` — 命名、error handling、hotspot decomposition 约定。
- `.planning/codebase/TESTING.md` — focused suite / regression / governance guard 结构。

### Relevant prior phase context
- `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-CONTEXT.md` — 对 formal-home inward slimming 的既有裁决。
- `.planning/phases/65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure/65-CONTEXT.md` — runtime-access / anonymous-share 的 recent boundary decisions。
- `.planning/phases/71-audit-driven-final-hotspot-decomposition-and-governance-truth-projection/71-CONTEXT.md` — hotspot decomposition 与 current-route truth 的先例。
- `.planning/phases/89-runtime-boundary-tightening-tooling-decoupling-and-open-source-entry-convergence/89-CONTEXT.md` — latest archived baseline 之后的直接 carry-forward 输入。

### Target hotspot families
- `custom_components/lipro/core/coordinator/runtime/command_runtime.py` — command orchestration formal home。
- `custom_components/lipro/core/coordinator/runtime/command/` — command-runtime inward collaborators family。
- `custom_components/lipro/core/coordinator/runtime/mqtt_runtime.py` — MQTT runtime orchestration formal home。
- `custom_components/lipro/core/coordinator/runtime/mqtt/` — MQTT runtime inward collaborators family。
- `custom_components/lipro/core/api/rest_facade.py` — REST child façade composition home。
- `custom_components/lipro/core/api/client.py` — stable import shell for `LiproRestFacade`。
- `custom_components/lipro/core/api/request_policy.py` — pacing / busy / 429 policy home。
- `custom_components/lipro/core/api/request_policy_support.py` — support-only pacing mechanics。
- `custom_components/lipro/core/api/request_gateway.py` — mapping/auth-aware retry orchestration。
- `custom_components/lipro/core/api/transport_executor.py` — transport execution home。
- `custom_components/lipro/core/anonymous_share/manager.py` — scoped/aggregate manager home。
- `custom_components/lipro/core/anonymous_share/manager_submission.py` — submit-flow collaborator。
- `custom_components/lipro/core/anonymous_share/sanitize.py` — anonymous-share sanitizer family。
- `custom_components/lipro/control/redaction.py` — control-plane redaction contract home。
- `custom_components/lipro/__init__.py` — HA root adapter / protected thin shell。
- `custom_components/lipro/control/runtime_access.py` — control-to-runtime read surface / protected thin shell。
- `custom_components/lipro/entities/base.py` — entity projection base / protected thin shell。
- `custom_components/lipro/entities/firmware_update.py` — firmware projection shell / hotspot protected boundary。

### Verification and guard surfaces
- `tests/meta/governance_current_truth.py` — current-route machine-readable truth。
- `tests/meta/test_governance_route_handoff_smoke.py` — current-route / GSD fast-path smoke guard。
- `tests/meta/governance_followup_route_current_milestones.py` — current milestone / archived baseline follow-up truth。
- `tests/meta/test_dependency_guards.py` — dependency/backflow guard。
- `tests/meta/test_public_surface_guards.py` — public surface / export guard。
- `tests/meta/test_governance_bootstrap_smoke.py` — bootstrap / route truth smoke guard。

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `custom_components/lipro/core/coordinator/runtime/command/`：command runtime 已经存在 builder / sender / confirmation / retry 等相邻 collaborator，可继续作为 inward split 的主落点。
- `custom_components/lipro/core/coordinator/runtime/mqtt/`：MQTT runtime 已有 connection / dedup / message_handler / reconnect 家族，说明当前正确方向是继续下沉到 runtime-local family，而非搬迁 ownership。
- `custom_components/lipro/core/api/request_policy_support.py`：request policy 已经有 support-only mechanics，表明 policy home 与 support home 的边界模式是可复用的。
- `custom_components/lipro/core/anonymous_share/manager_submission.py`：anonymous-share submit flow 已从 manager outward home 中拆出第一层 collaborator，可继续作为后续 slimming 的切分模板。
- `custom_components/lipro/control/runtime_access_support.py` 与 `custom_components/lipro/control/runtime_access_types.py`：runtime-access 已展示 protected outward home + inward support/type families 的薄壳模式。

### Established Patterns
- 正式 outward homes 保留稳定 import / ownership，厚逻辑沿 sibling support families inward split，例如 `runtime_access.py -> runtime_access_support*.py`、`share_client.py -> share_client_submit.py`。
- 薄壳根模块不允许重新吸附 orchestration，尤其是 `__init__.py`、control readers、entity bases、platform shells。
- baseline / review docs 才是长期治理真源；`.planning/codebase/*.md` 是 derived collaboration maps，只能导航与辅证，不能越权。
- 当前仓库对“重构正确姿势”的统一定义是：**保留 formal home，切分 concern，补 focused guard，同步 truth docs**。

### Integration Points
- `Phase 90` 的主要交付将落在 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/reviews/{FILE_MATRIX,RESIDUAL_LEDGER,KILL_LIST}.md` 与相应 `tests/meta` guards。
- 后续 `Phase 91` 会直接消费本 context 中的 hotspot ownership 与 thin-shell protection 线，决定实际 refactor 的 task slicing。
- `Phase 92` 会消费 anonymous-share / redaction 的 boundary 冻结结论，避免在 redaction convergence 时误迁 ownership。

</code_context>

<deferred>
## Deferred Ideas

- `ARC-24` / `TYP-23` 的真实代码改造与 no-growth guard 细化，延后到 `Phase 91`。
- `SEC-01` / `TST-29` 的 redaction registry convergence 与 assurance topicization，延后到 `Phase 92`。
- `QLT-37` 的最终质量冻结、microbenchmark budget story 与 milestone closeout proof，延后到 `Phase 93`。
- repo-wide 开源入口 / continuity / archive wording 的进一步 polishing 保持 deferred；本里程碑不重开 `v1.22 -> v1.24` 已冻结的路线故事。
- `outlet_power` legacy side-car fallback 的最终物理删除继续 deferred，直到形成零命中 / 零写回证据。

</deferred>

---

*Phase: 90-hotspot-routing-freeze-and-formal-home-decomposition-map*
*Context gathered: 2026-03-28 via auto-synthesized repo-wide audit*
