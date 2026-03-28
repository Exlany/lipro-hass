# Phase 102: Governance Portability, Verification Stratification & Open-Source Continuity Hardening - Context

**Gathered:** 2026-03-28
**Status:** Completed / archived-only closeout

<domain>
## Phase Boundary

本 phase 不再改动生产业务 formal homes；只处理 archived-only closeout 仍残留的治理脆弱点：
- governance/meta smoke 对本机 `node` / `gsd-tools.cjs` 的硬依赖
- `.planning/baseline/VERIFICATION_MATRIX.md` 当前真相与 historical closeout note 的混排
- docs-first / maintainer appendix / archived evidence wording 的 portability drift
- latest archived baseline 从 `v1.27 / Phase 101` 前推到 `v1.28 / Phase 102`

</domain>

<decisions>
## Locked Decisions

- `v1.28` 采用 archived-only closeout 风格，不保留 active milestone 终态。
- `Phase 102` 为单 phase closeout，3 个计划，最终状态必须回到 `no active milestone route / latest archived baseline = v1.28`。
- `v1.27` 继续保留 previous archived baseline 身份；不得回写其 audit/evidence verdict。
- 缺少 `node` 或 `gsd-tools` 时，只允许 skip fast-path smoke，不允许跳过 docs / baseline / route-contract truth 校验。
- `.planning/codebase/*.md` 继续只是 derived collaboration maps，不得升级为 authority chain。

</decisions>

<canonical_refs>
## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — north-star authority chain
- `.planning/PROJECT.md` — current archived-only baseline story
- `.planning/ROADMAP.md` — milestone/phase archive topology
- `.planning/REQUIREMENTS.md` — archived requirement basket / traceability
- `.planning/STATE.md` — parser-facing archived state and continuity order
- `.planning/baseline/VERIFICATION_MATRIX.md` — current truth vs historical closeout stratification
- `.planning/reviews/V1_27_EVIDENCE_INDEX.md` — previous archived bundle pull contract

</canonical_refs>
