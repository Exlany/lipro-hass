# Phase 47: Continuity contract, governance entrypoint compression, and tooling discoverability - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning
**Source:** `Phase 46` remediation roadmap + formalized `v1.7` route

<domain>
## Phase Boundary

本 phase 只处理 `Phase 46` 已明确点名、且可以小范围快速收口的四类治理/入口问题：

1. release custody / delegate / freeze / restoration 真相仍分散在 `SUPPORT.md`、`SECURITY.md`、runbook、CODEOWNERS、issue/PR templates 与 machine-readable registry 之间，虽然故事线大体一致，但还不够压缩、也缺少更强的 machine-checkable alignment；
2. `docs/README.md` 的 docs-index 身份是正确的，但 package metadata、Issue UI 首跳、README bilingual routing 与 support fast-path 仍让新贡献者较难第一时间落到正确入口；
3. `scripts/agent_worker.py` 与 `scripts/orchestrator.py` 仍以 retired compatibility stub 形态与 active tooling 并列，且当前默认 `return 0` 的 no-op 行为会给遗留自动化制造假绿；
4. governance active truth 里仍有少量 drift：release signature identity regex 过宽、`VERIFICATION_MATRIX.md` 残留失效 runnable path、`scripts/check_file_matrix.py` 尚未覆盖该类 active baseline path drift。

本 phase 不处理 `RuntimeAccess` / `Coordinator` hotspot decomposition，也不触碰 mega-test topicization 或 REST typed-surface reduction；这些属于已 formalized 的 `Phase 48 -> 50`。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- continuity / custody / delegate / freeze / restoration 真相必须继续讲 single-maintainer honesty，不得虚构 hidden delegate、backup maintainer、break-glass publish path 或第二套 release story。
- `docs/README.md` 是 docs-index 正式入口；package metadata、Issue UI、README / README_zh 与 contributor-facing 文档应优先把人导向 docs index，而不是直接把 maintainer-only runbook 混进 public first-hop。
- retired compatibility stubs 必须明确标记为非正式入口；若继续保留文件，至少要 fail-fast 或显式告诉调用方它们已退役且不可再当成功路径使用。
- release signature verification 的 certificate identity 必须锚定 tagged release path，不再接受过宽的 `heads/.+` 或任意 ref regex。
- governance drift 修复必须落成 machine-checkable guard：至少通过 meta tests 或 checker 覆盖 docs index / release identity / active baseline path truth。

### Claude's Discretion
- public fast-path 与 maintainer appendix 在文档首页如何分层、表格还是 bullets；
- retired compatibility stubs 是直接 non-zero fail-fast，还是 exit 0 但明显警告（优先 fail-fast，除非会破坏正式 contract）；
- `check_file_matrix.py` 是扫描指定 headings 还是补一个更窄的 verification-matrix path validator。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / governance truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 北极星终态与禁止项
- `AGENTS.md` — governance / docs / command / testing / no-fabrication constraints
- `.planning/PROJECT.md` — `v1.7` formalized route truth
- `.planning/ROADMAP.md` — `Phase 47` goal、requirements 与 plan titles
- `.planning/REQUIREMENTS.md` — `GOV-37 / DOC-06` requirement truth
- `.planning/STATE.md` — next-command / active-baseline truth
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-AUDIT.md` — docs/tooling discoverability 与 continuity gaps
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-03-TOOLCHAIN-OSS-GOVERNANCE-AUDIT.md` — `Documentation URL`、scripts stub、docs index、entry routing 审阅判词
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md` — `Phase 47` outcomes / verify anchors

### Continuity / public-entry surfaces
- `SUPPORT.md` — public support routing + maintainer appendix
- `SECURITY.md` — private disclosure + continuity appendix
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` — release custody / rehearsal / continuity drill truth
- `docs/README.md` — docs index / public-vs-maintainer layering
- `.github/CODEOWNERS` — primary custodian truth
- `.github/ISSUE_TEMPLATE/config.yml` — issue UI first-hop links
- `.github/ISSUE_TEMPLATE/bug.yml` — continuity wording / support routing
- `.github/ISSUE_TEMPLATE/feature_request.yml` — idea intake copy
- `.github/pull_request_template.md` — contributor / continuity contract
- `README.md`
- `README_zh.md`
- `pyproject.toml`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`

### Tooling / release / governance drift targets
- `.github/workflows/release.yml` — cosign identity regex / tagged release verification
- `scripts/agent_worker.py` — retired compatibility stub
- `scripts/orchestrator.py` — retired compatibility stub
- `.planning/baseline/VERIFICATION_MATRIX.md` — active baseline runnable proof truth
- `scripts/check_file_matrix.py` — active governance-doc path validator

### Verify anchors
- `tests/meta/test_toolchain_truth.py`
- `tests/meta/test_governance_release_contract.py`
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_version_sync.py`

</canonical_refs>

<specifics>
## Specific Ideas

- fix `project.urls.Documentation` to point at `docs/README.md` rather than root `README.md`;
- make issue-config documentation contact link land on `docs/README.md` so the docs index, not troubleshooting-only, becomes the first-hop entry;
- compress public first-hop so maintainer-only runbook 不再和普通用户路径放在同一视觉层；
- tighten the release signature identity regex in both workflow and README examples to tagged-release-only semantics;
- classify active scripts (`scripts/setup`, `scripts/develop`, `scripts/lint`) vs retired compatibility stubs (`scripts/agent_worker.py`, `scripts/orchestrator.py`) in docs and machine-readable registry;
- replace silent-success no-op in retired stubs with clear fail-fast exit code and deprecation routing;
- repair stale runnable proof references in `VERIFICATION_MATRIX.md` and extend a checker/test so active baseline path drift is caught automatically.

</specifics>

<deferred>
## Deferred Ideas

- 不在本 phase 内处理 `RuntimeAccess`、`Coordinator`、`EntryLifecycleController`、telemetry surface 的 structural decomposition；这些进入 `Phase 48`。
- 不在本 phase 内执行 mega-test topicization、top-level test re-home 与 failure-localization overhaul；这些进入 `Phase 49`。
- 不在本 phase 内大规模缩减 REST typed-surface `Any` 或 command/result ownership；这些进入 `Phase 50`。
- 不在本 phase 内引入新依赖、新发布渠道或新的 maintainer hierarchy。

</deferred>

---

*Phase: 47-continuity-contract-governance-entrypoint-compression-and-tooling-discoverability*
*Context gathered: 2026-03-20 after Phase 46 audit closeout*
