# Phase 58: Repository audit refresh and next-wave routing - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning
**Source:** PRD Express Path (`.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-PRD.md`) + `v1.11` milestone seed + current truth reread

<domain>
## Phase Boundary

本 phase 是一次 **fresh current-state repo audit + formal routing**，不是趁审计顺手扩成大重构。交付边界锁定如下：

1. 必须重新审阅 `custom_components/lipro/**`、`tests/**`、`scripts/**`、root docs、root config / packaging、`.planning` governance truth；
2. 必须对架构、formal roots、命名、目录结构、旧新代码边界、refactor residue、热点复杂度、验证可维护性、开源成熟度给出 **file-aware verdict**；
3. 必须把 refreshed verdict 收束成 `58-AUDIT.md`、`58-SCORE-MATRIX.md`、`58-REMEDIATION-ROADMAP.md` 与 `Phase 59+` remediation route；
4. 必须把 `v1.11 / Phase 58` 冻结到 current-story docs、promoted evidence 与相应 meta guards，避免 refreshed audit 继续停留在 conversation memory；
5. 默认不做 broad code refactor，不重开已关闭 residual family，除非当前代码直接证明旧 closeout 叙事已失真。

本 phase 允许产出新的 audit artifacts、score matrix、route docs、summary / verification 与最小必要的 current-truth 同步；不允许借“审计”名义凭空发明 maintainer、support、release 或 upstream promises。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- 以 **当前仓库文件** 为唯一审阅对象，不依赖旧对话记忆或 stale snapshot 想象。
- 审阅必须同时对照 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、Home Assistant integration norms、international open-source best practices 与仓库自述 contract。
- 结果必须以 evidence tables、severity-ranked verdicts、显式 remediation route 为主，不接受 narrative-only prose 充当正式结论。
- 诚实记录“good but still large / correct but hotspot-heavy / converged but noisy”等结论；禁止为了整齐而伪造 residual、伪造 perfection、伪造 kill target。
- refreshed audit 必须覆盖所有 in-scope Python / docs / config / governance surfaces，并为每个区域留下 verdict 或范围说明，不能有 silent blind spot。
- 不得重新打开已经关闭的 residual family，除非 current repo evidence 明确证明既有 closeout 叙事为假。
- 不得编造新的 maintainer、支持渠道、release promise、兼容承诺或上游 roadmap。
- deliverables 必须覆盖：architecture/code audit、governance/open-source audit、next-wave remediation route、truth freeze、closeout evidence。

### Claude's Discretion
- 可以把 refreshed audit 拆成 inventory / architecture-code shard / governance-OSS shard / master audit / score matrix / route / closeout package，只要 3 个 plans 的依赖关系清晰且可执行。
- 可以使用三档、五档或矩阵式评分，但必须能回指具体文件与理由。
- 若 current-story docs 与 closeout guards 存在已知漂移，可在 truth-freeze 计划中优先修复最小必要范围，而不是顺手大扫除。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star and current truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 单一正式主链与五大平面裁决第一真源
- `AGENTS.md` — 仓库级执行契约、phase 资产身份、验证命令统一规则
- `docs/developer_architecture.md` — 当前 formal topology / ownership / verification fast-path 导航
- `.planning/PROJECT.md` — `v1.11` milestone seed 已种入 current-story project truth
- `.planning/ROADMAP.md` — `Phase 58` 的 goal / requirements / 3-plan skeleton / success criteria
- `.planning/REQUIREMENTS.md` — `AUD-03 / ARC-10 / OSS-06 / GOV-42` 的正式 requirement contract
- `.planning/STATE.md` — 当前仍停在 `v1.10` closeout pointer；`Phase 58` truth freeze 必须诚实收束此漂移
- `.planning/reviews/V1_11_MILESTONE_SEED.md` — refreshed audit 的 immediate milestone seed 与 deliverable expectations
- `.planning/phases/58-repository-audit-refresh-and-next-wave-routing/58-PRD.md` — 本 phase 的 PRD / scope / locked decisions / acceptance criteria

### Governance baselines and review ledgers
- `.planning/baseline/PUBLIC_SURFACES.md` — public surface / promoted-evidence boundary truth
- `.planning/baseline/DEPENDENCY_MATRIX.md` — plane dependency direction / forbidden edges
- `.planning/baseline/VERIFICATION_MATRIX.md` — phase acceptance / promoted evidence / runnable proof contract
- `.planning/baseline/AUTHORITY_MATRIX.md` — authority layering / source-of-truth 仲裁
- `.planning/baseline/GOVERNANCE_REGISTRY.json` — governance artifact registry / ownership hints
- `.planning/reviews/FILE_MATRIX.md` — file-level governance ownership truth
- `.planning/reviews/RESIDUAL_LEDGER.md` — residual / sustainment debt inventory
- `.planning/reviews/KILL_LIST.md` — delete / retire gate truth
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` — phase closeout artifact allowlist

### Historical audit baselines and recent closeout evidence
- `.planning/phases/41-full-spectrum-architecture-code-quality-and-open-source-audit/41-REMEDIATION-ROADMAP.md` — 最早 full-spectrum audit 的 remediation routing baseline
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-02-ARCHITECTURE-CODE-AUDIT.md` — 最近一次 repo-wide architecture/code verdict baseline
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-SUMMARY.md` — `Phase 46` strengths / core risks / next-step snapshot
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-VERIFICATION.md` — `Phase 46` deliverable set / promoted-evidence / verification contract
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md` — `Phase 47 -> 50` route source；本 phase 应把其当 baseline 而非 eternal truth
- `.planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-SUMMARY.md` — 最新 closeout-ready feature hardening baseline
- `.planning/phases/57-command-result-typed-outcome-and-reason-code-hardening/57-VERIFICATION.md` — 当前 promoted closeout evidence / governance sync baseline

### Mandatory audit surfaces
- `custom_components/lipro/**` — production Python / protocol / runtime / control / domain / platform surfaces
- `tests/**` — verification topology / meta-guard / mega-suite / failure-localization surfaces
- `scripts/**` — local tooling / governance helpers / developer-path clarity
- `README.md`, `README_zh.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md`, `CHANGELOG.md` — root public / contributor / support / release-facing docs
- `pyproject.toml`, `.pre-commit-config.yaml`, `.devcontainer.json`, `custom_components/lipro/manifest.json`, `custom_components/lipro/quality_scale.yaml` — packaging / tooling / distribution / Home Assistant contract
- `custom_components/lipro/services.yaml`, `custom_components/lipro/translations/**`, `blueprints/**` — user-facing surface clarity / bilingual and configuration edge coverage
- `tests/meta/test_governance_closeout_guards.py`, `tests/meta/test_governance_followup_route.py`, `tests/meta/test_governance_phase_history.py`, `tests/meta/test_governance_phase_history_runtime.py`, `tests/meta/test_version_sync.py` — truth-freeze machine guards

</canonical_refs>

<specifics>
## Specific Ideas

- `Phase 58` 最优拆法是 **Wave 1 并行双审计**（architecture/code 与 governance/OSS），然后 **Wave 2 做 master verdict + remediation route + truth freeze**。
- 建议沿用 `Phase 46` 的窄提升策略：只提升最终 audit bundle 与 closeout proof，不把 `58-CONTEXT.md`、`58-VALIDATION.md`、`58-0x-PLAN.md` 误洗成长期治理真源。
- `STATE.md` 目前仍以 `v1.10 / Phase 57` 作为 current milestone status，而 `PROJECT.md` / `ROADMAP.md` / `REQUIREMENTS.md` 已显式种出 `v1.11 / Phase 58`；`58-03` 必须诚实修复这一 current-story drift，但不能伪造“已发货”叙事。
- refreshed audit 应保留“strengths / closed debts / active risks / later-route opportunities”四分法，避免把所有问题都写成 must-fix-now。

</specifics>

<deferred>
## Deferred Ideas

- broad code refactor before the refreshed master verdict exists
- reopening already closed residual families without fresh contradictory evidence
- inventing new maintainer / support / release / compatibility promises not grounded in repo assets
- turning audit findings directly into implementation changes inside `Phase 58`

</deferred>

---

*Phase: 58-repository-audit-refresh-and-next-wave-routing*
*Context gathered: 2026-03-22 via PRD Express Path + v1.11 seed + current-truth reread*
