# Phase 59: Verification localization and governance guard topicization - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning
**Source:** PRD Express Path (`.planning/phases/59-verification-localization-and-governance-guard-topicization/59-PRD.md`) + `v1.12` milestone seed + `Phase 58` remediation route

<domain>
## Phase Boundary

本 phase 是一次 **verification topology refinement**，不是 production architecture rewrite。

1. 必须只处理已被 `Phase 58` 点名的 megaguards / megasuites；
2. 必须沿 stable truth family / concern boundary topicize，而不是按任意文件长度切块；
3. 必须同步更新 current-story docs 与 verification truth，避免 split 只存在于文件层而治理层失真；
4. 不得新增新的 public helper root、duplicate truth file 或 second governance story。

</domain>

<decisions>
## Locked Decisions

- `tests/meta/test_public_surface_guards.py`、`tests/meta/test_governance_phase_history.py`、`tests/meta/test_governance_followup_route.py` 与 `tests/core/test_device_refresh.py` 是当前最高优先级热点。
- split 优先目标是 **failure localization** 与 **ownership clarity**，不是追求机械平均行数。
- 若需要抽公共 helper，必须优先复用现有 `tests/helpers/**` 或保持 file-local private helper；禁止创造新的长期 truth root。
- `.planning/baseline/VERIFICATION_MATRIX.md` 与 current-story docs 必须反映新的 runnable topology 与 focused command story。

### Claude's Discretion
- 可按 topic / concern / truth family 拆分 test modules，只要命名与边界清晰。
- 可把 route / history / public-surface assertions 从 giant guard 中抽成更窄套件，但必须保留原 guard intent。
- 可在 Phase 59 内顺手修正文档里的 verification command anchors，只要不越界到 `Phase 60` tooling surgery。

</decisions>

<canonical_refs>
## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-REMEDIATION-ROADMAP.md`
- `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-SUMMARY.md`
- `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-VERIFICATION.md`

## Hotspot Observations

- `tests/meta/test_public_surface_guards.py` 约 `758` 行，混合 public surface、naming、review-ledger、phase note 等多种 truth family。
- `tests/meta/test_governance_phase_history.py` 约 `773` 行，跨越多代 phase execution evidence 与 closeout truth。
- `tests/meta/test_governance_followup_route.py` 约 `612` 行，兼顾多代 milestone continuation 与 current route。
- `tests/core/test_device_refresh.py` 约 `756` 行，混合 filter parsing、device filter semantics 与 runtime behavior。

</canonical_refs>

<execution_shape>
## Recommended Execution Shape

- `59-01`：先 topicize governance/public-surface/follow-up-route guards
- `59-02`：再 split `test_device_refresh.py`
- `59-03`：最后把 verification topology / current-story docs / matrices 写回并补 focused guards

</execution_shape>
