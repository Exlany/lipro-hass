# Phase 46 Score Matrix

| Dimension | Score | Grade | Current strengths | Current gaps | Primary evidence | Routed follow-up |
|---|---:|---|---|---|---|---|
| Architecture | 8.5/10 | A- | single protocol/runtime root still holds; dependency direction guarded; adapters mostly thin | formal roots and helper homes still thick; command ownership drift not fully closed | `46-02-ARCHITECTURE-CODE-AUDIT.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `.planning/baseline/PUBLIC_SURFACES.md` | `Phase 48`, `Phase 50` |
| Tests | 7.8/10 | B+ | topology is rich and intentional; protocol replay and boundary assurance are strong | governance megaguards and several runtime/platform megas still hurt failure localization | `46-02-ARCHITECTURE-CODE-AUDIT.md`, `tests/meta/test_governance_closeout_guards.py`, `tests/core/test_coordinator.py` | `Phase 49` |
| Typing | 7.6/10 | B+ | `mypy strict`; production `type: ignore=0`; broad catch nearly gone | `Any` remains concentrated in REST child-facade family and projection-heavy helpers | `46-02-ARCHITECTURE-CODE-AUDIT.md`, `pyproject.toml`, `tests/meta/test_phase31_runtime_budget_guards.py`, `tests/meta/test_phase45_hotspot_budget_guards.py` | `Phase 50` |
| Docs | 8.3/10 | A- | public fast-path is clear; maintainer appendix is isolated; bilingual public docs are usable | docs discoverability can improve; README remains heavy; maintainer appendix is Chinese-heavy | `46-03-TOOLCHAIN-OSS-GOVERNANCE-AUDIT.md`, `README.md`, `README_zh.md`, `docs/README.md` | `Phase 47` |
| Workflow | 9.1/10 | A | CI/release gates are mature; release trust and supply-chain evidence are exceptionally strong | fork/private-repo resilience is weaker; release trust story is strong but complex | `46-03-TOOLCHAIN-OSS-GOVERNANCE-AUDIT.md`, `.github/workflows/ci.yml`, `.github/workflows/release.yml` | `Phase 47` |
| Governance | 8.9/10 | A- | authority layering, promoted-asset registry, and ledgers are rigorous and machine-auditable | navigation cost is high; continuity truth still requires multi-file manual sync | `46-03-TOOLCHAIN-OSS-GOVERNANCE-AUDIT.md`, `.planning/baseline/AUTHORITY_MATRIX.md`, `.planning/reviews/PROMOTED_PHASE_ASSETS.md` | `Phase 47` |
| OSS maturity | 7.4/10 | B | contributor/support/security/release routes are honest and coherent; project feels trustworthy | bus factor and custody continuity are the main maturity constraint | `46-03-TOOLCHAIN-OSS-GOVERNANCE-AUDIT.md`, `SUPPORT.md`, `SECURITY.md`, `.github/CODEOWNERS` | `Phase 47` |

## Dimension Notes

- `Architecture` 已经从“是否正确”进入“是否还能继续瘦身且不回流第二故事线”的阶段。
- `Tests` 的问题不在 coverage 缺失，而在 megaguard / megatest failure UX。
- `Typing` 的最难部分已经从 broad catch 与 `type: ignore` 清理转移到局部 `Any` 集中削减。
- `Docs` 与 `Workflow` 本身都很强，但 `OSS maturity` 被 single-maintainer continuity 明显拉低。
- `Governance` 的 rigor 已很高，下一步的价值在于降噪与降低 onboarding friction，而不是继续增加新真源层。

## Overall Score

- 加权总评：`8.2/10`
- 综合等级：`A- / 高成熟度，但仍受 continuity、formal-root density、mega-test topology 与 REST typed-surface debt 约束`
