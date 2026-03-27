# Phase 85: Terminal audit refresh and residual routing - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Source:** v1.23 active-route bootstrap after repo-wide governance/current-truth repair

<domain>
## Phase Boundary

本 phase 是 `v1.23` 的 audit/routing 入口，只处理「全仓终局审计 + 残留归类 + 真源收口」：

- 对 `custom_components/lipro`、`tests`、`docs`、`.planning`、workflow/config 入口做一次 repo-wide terminal audit，把 live residual / hotspot / truth drift 从印象变成 file-level verdict。
- 对已确认的 baseline / governance drift 做“可立即关闭”的收口，优先修正文档真源、自相矛盾叙事与 route/bootstrap contract 漂移。
- 对不能在本 phase 内安全完成的 production / assurance hotspots，必须明确归类为 `close now / route next / explicitly keep`，并登记 owner、exit condition、evidence path；不允许 silent defer。
- 不把 Phase 85 扩大成大规模生产路径 surgery：除非是低风险、真根因清晰、且能直接降低 silent residual / compat debt 的变更，否则把实质性 production refactor 留给 `Phase 86/87`。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- 本 phase 对应 `ROADMAP.md` 中 `Phase 85`，只覆盖 `AUD-04` 与 `GOV-62`。
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 是当前裁决主链；任何 audit verdict 若与旧 baseline/review prose 冲突，以当前主链和正式代码结构为准。
- 当前 active route truth 已固定为 `v1.23 active route / Phase 85 planning-ready / latest archived baseline = v1.22`；`phase_dir` 必须使用 `85-terminal-audit-refresh-and-residual-routing`，不得再写回旧的 inventory-freeze slug。
- repo-wide terminal audit 至少要明确覆盖并裁决下列已观察到的问题：
  - `.planning/baseline/TARGET_TOPOLOGY.md` 仍含 `AuthSession` / `LiproClient` compat shell / 旧 control home 叙事；
  - `.planning/baseline/DEPENDENCY_MATRIX.md` 仍保留 backoff compat surface 旧说法，与现行 `core/utils/backoff.py` 真源冲突；
  - `docs/developer_architecture.md` 与部分 baseline 文档 freshness 标记滞后；
  - `custom_components/lipro/core/anonymous_share/share_client.py` 仍有 silent compat wrapper / delete-gate debt；
  - `custom_components/lipro/runtime_infra.py` 与若干 mega tests 仍是明显热点，但是否立即拆分需要 phase-level routing 决定。
- Phase 85 的输出必须让维护者能直接看到：哪些问题已在本 phase 关闭、哪些被路由到 `Phase 86/87/88`、哪些被明确保留且原因充分。
- 不得把已关闭的 `LiproClient` / `LiproMqttClient` / archived-only route / old bootstrap stories 误写回 active family。

### The Agent's Discretion
- 可以新增一个 phase-local audit artifact（例如 `85-RESEARCH.md` / `85-SUMMARY.md` / `.planning/reviews/V1_23_TERMINAL_AUDIT.md`）来承载 file-level verdict，但不要再造第二套长期治理真源；长期 truth 仍应回写到 baseline/reviews/current-route docs。
- 若某个 silent residual 可以低风险直接删除（例如仅测试引用的 compat alias），允许在本 phase 关闭；否则以诚实路由优先。
- audit verdict 可以按 `close now / route next / explicitly keep` 或类似矩阵呈现，只要 machine-checkable、后续 phase 可直接消费。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Current route / north-star truth
- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/MILESTONES.md`
- `tests/meta/governance_current_truth.py`
- `tests/meta/governance_followup_route_current_milestones.py`

### Baseline / review truth to audit
- `.planning/baseline/TARGET_TOPOLOGY.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/ARCHITECTURE_POLICY.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/V1_22_EVIDENCE_INDEX.md`
- `.planning/v1.22-MILESTONE-AUDIT.md`

### Production / test hotspots already observed
- `custom_components/lipro/core/anonymous_share/share_client.py`
- `custom_components/lipro/runtime_infra.py`
- `tests/core/api/test_api_diagnostics_service.py`
- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/core/coordinator/runtime/test_mqtt_runtime.py`
- `tests/meta/test_phase72_runtime_bootstrap_route_guards.py`
- `tests/meta/test_governance_bootstrap_smoke.py`
- `tests/meta/test_governance_route_handoff_smoke.py`
- `tests/meta/test_governance_closeout_guards.py`

### Audit / routing execution targets
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-CONTEXT.md`
- `.planning/phases/85-terminal-audit-refresh-and-residual-routing/85-RESEARCH.md`

</canonical_refs>

<specifics>
## Specific Ideas

- 先修 baseline/governance 真源漂移：`TARGET_TOPOLOGY.md`、`DEPENDENCY_MATRIX.md`、freshness markers 应与当前 formal homes / route truth 同步。
- repo-wide audit 产物要有明确 verdict 和 phase routing：例如 `close now`（文档真源漂移、低风险 compat alias）、`route next`（runtime_infra / mega-test decomposition）、`explicitly keep`（当前仍有价值但需登记的 carry-forward）。
- focused guards 应锁住本轮 active route、phase slug、baseline drift 与 stale archive projection，避免 audit 结论回头再次漂移。

</specifics>

<deferred>
## Deferred Ideas

- `Phase 86` 负责 production residual eradication / boundary re-tightening；不要在本 phase 把 `runtime_infra.py` 之类热点硬拆到半套状态。
- `Phase 87` 负责 assurance hotspot decomposition；本 phase 可以登记 mega-test hotspots，但不必一次性完成所有 topicization。
- `Phase 88` 负责 governance sync / milestone freeze；本 phase 不直接做 milestone closeout。

</deferred>
