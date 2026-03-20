# Phase 44: Governance asset pruning and terminology convergence - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning
**Source:** `v1.6` roadmap after `Phase 42 complete`

<domain>
## Phase Boundary

本 phase 只处理三类治理/文档噪音问题：

1. `.planning/phases/**` 的 execution-trace / promoted-asset / authority 边界仍需要继续收紧，避免 phase 目录资产反向冒充 current truth；
2. façade 时代术语仍有 `client / mixin / forwarding` 等历史残留，current docs / ADR / comments / guards 尚未完全收口到 `protocol / facade / operations`；
3. contributor fast-path、maintainer appendix 与 bilingual boundary policy 仍偏混杂，外部贡献者容易过早接触维护者治理语义或多余上下文。

本 phase 不解 control/services/runtime 边界，不拆热点代码，不重新定义 release/security/support contract；这些由 `Phase 43` / `Phase 45` 与已完成的 `Phase 42` 负责。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- `.planning/phases/**` 默认身份必须继续是 execution trace；只有 allowlist / promoted 资产可以进入长期治理 / CI truth。
- authority order 必须维持 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` → active planning truth → baseline / reviews 的裁决链，phase trace 不得反向充当 authority。
- façade 时代官方术语统一为 `protocol / facade / operations`；`client / mixin / forwarding` 只允许留在历史档案、残留账本或明确记录的兼容上下文。
- contributor fast-path 必须低噪声、可直达，maintainer appendix 与治理附录必须分区明确；双语边界策略要可链接、可守卫、不可凭口头记忆维持。
- phase 必须同步 docs、review ledgers、baseline docs 与 meta guards，不允许只改单点文案而让守卫/索引继续漂移。

### Claude's Discretion
- contributor fast-path / maintainer appendix 是通过拆文档章节、独立附录文件还是导航重构来达成；
- terminology convergence 是 repo-wide 批量收口还是先收 current truth + touched docs/comments；
- promoted-asset 守卫应补到哪些 matrix / history tests / allowlist 文件上。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / active truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 北极星终态与 authority 禁止项
- `AGENTS.md` — authority 顺序、phase trace/promote contract、formal terminology guidance
- `.planning/PROJECT.md` — 当前 `v1.6` milestone truth
- `.planning/ROADMAP.md` — `Phase 44` 正式路线与 success criteria
- `.planning/REQUIREMENTS.md` — `GOV-35 / RES-11 / DOC-04` 真源
- `.planning/STATE.md` — current mode / next-command truth
- `.planning/phases/42-delivery-trust-gates-and-validation-hardening/42-SUMMARY.md` — 当前 active milestone 的最近完成态
- `.planning/phases/39-governance-current-story-convergence-control-home-clarification-and-mega-test-decomposition/39-05-PLAN.md` — phase asset promotion / current story 收口的先例

### Governance / review truth
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` — `.planning/phases/**` promoted allowlist
- `.planning/baseline/AUTHORITY_MATRIX.md` — authority chain 真源
- `.planning/baseline/VERIFICATION_MATRIX.md` — promoted verification contract
- `.planning/baseline/PUBLIC_SURFACES.md` — public surface 当前登记
- `.planning/baseline/DEPENDENCY_MATRIX.md` — dependency truth 当前登记
- `.planning/reviews/FILE_MATRIX.md` — repo file governance inventory
- `.planning/reviews/RESIDUAL_LEDGER.md` — residual / retireable debt 真源
- `.planning/reviews/KILL_LIST.md` — delete gate / residual kill truth
- `docs/developer_architecture.md` — façade-era terminology / topology 说明

### Contributor / doc entrypoints
- `README.md` — public English entrypoint
- `README_zh.md` — public Chinese entrypoint
- `docs/README.md` — docs index
- `CONTRIBUTING.md` — contributor fast-path / CI contract / appendix 入口
- `SUPPORT.md` — public support routing
- `SECURITY.md` — private disclosure routing

### Tests / guards
- `tests/meta/test_governance_closeout_guards.py` — closeout / promoted-asset / current story 守卫
- `tests/meta/test_governance_phase_history.py` — phase history/promote contract 守卫
- `tests/meta/test_governance_phase_history_runtime.py` — runtime/governance history 守卫
- `tests/meta/test_governance_phase_history_topology.py` — topology/history drift guards
- `tests/meta/test_toolchain_truth.py` — docs/tooling/current-truth 守卫

</canonical_refs>

<specifics>
## Specific Ideas

- 先把 `.planning/phases/**` 的 promoted allowlist / verification matrix / roadmap-state references 讲成一条 story，再去清 terminology 与 contributor fast-path；
- current docs / review ledgers / comments 中的 `client / mixin / forwarding` 残留需要清单化，不要盲目 repo-wide 替换；
- contributor fast-path 应优先保留最短上手路径，把 maintainer-only appendix / governance explanation 下沉到附录或链接区；
- bilingual policy 不只是 README 双语，而应明确哪些文档必须双语、哪些可 maintainer-only English。

</specifics>

<deferred>
## Deferred Ideas

- 不在本 phase 里改 control/runtime/service 代码边界；
- 不在本 phase 里拆 `rest_decoder_support.py` / `diagnostics_api_service.py` / `share_client.py` / `message_processor.py` 等热点；
- 不在本 phase 里新增第二套 governance registry 或新的 authority root；
- 不把 archive snapshots 与 active truth 混写成同一种文档身份。

</deferred>

---

*Phase: 44-governance-asset-pruning-and-terminology-convergence*
*Context gathered: 2026-03-20 after Phase 42 completion*
