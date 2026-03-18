# Phase 34 Context

**Phase:** `34 Continuity and hard release gates`
**Milestone:** `v1.4 seed — Sustainment, Trust Gates & Final Hotspot Burn-down`
**Date:** `2026-03-18`
**Status:** `planned — context captured, ready for execution planning`
**Source:** `.planning/{ROADMAP,REQUIREMENTS,STATE,PROJECT}.md` + `.planning/v1.3-MILESTONE-AUDIT.md` + full-repo terminal audit + current green governance/toolchain gates

## Why Phase 34 Exists

`v1.3` 的真实裁决已经不是“还有 formal gap 没补”，而是“requirements / phases / integration / Nyquist 均闭环，但 retained tech debt 仍值得继续 burn-down”。

在这些 retained debts 中，最不适合继续拖延的两项是：

1. **release hardening 还未封顶**：仓库当前已经有 `SHA256SUMS`、`SBOM`、GitHub artifact `attestation` / `provenance` 与 tagged runtime security gate，但 `artifact signing` 与 hard `code scanning` 仍是显式 defer。
2. **maintainer continuity 仍然只停留在诚实记录**：README / SUPPORT / SECURITY / runbook / CODEOWNERS 已如实承认单维护者现实，但 bus factor 仍主要依赖“冻结承诺”，尚未形成真正的 custody / delegate / freeze-escalation contract。

这两项问题若继续只停留在“文档诚实”，仓库就会长期卡在 `9.x/10`，而无法达到契约者要求的 10 分终态。

## Goal

1. 把 continuity / custody / freeze posture 从叙述性文档升级为可审计、可验证、可演练的正式合同。
2. 在不破坏当前 `attestation` / `provenance` 故事线的前提下，为 release identity 增加 machine-verifiable signing，并把 code scanning / release trust 升级为明确 hard gate 或 blocking contract。
3. 让 README / README_zh / SUPPORT / SECURITY / runbook / CODEOWNERS / workflow / meta guards 讲同一条、非夸大、可机读的 release + continuity 故事线。

## Decisions (Locked)

- `v1.3` 仍保持 `tech_debt / closeout-eligible` 的审计结论；Phase 34 不回写 `v1.3` 为 failed audit。
- 不允许虚构“隐藏备用维护者”或未真实存在的 custody delegate；若当前客观上仍缺冗余，必须用 **freeze contract + escalation truth** 诚实表达。
- 不允许把 `attestation/provenance` 与 `artifact signing` 混为一谈；若新增 signing，文档必须明确区分两者职责。
- 不允许把 hard gate 写进文档却不落到 workflow / guards；同样，也不允许 workflow 已实施而文档仍自称 defer。
- 不允许把 vendor-constrained crypto（如 MD5 登录路径）偷塞进本 phase；它不属于当前仓库可独立消灭的 release/continuity debt。

## Non-Negotiable Constraints

- 不得新增第二套 release story、第二套 security story 或第二套 maintainer custody 叙事。
- 不得通过放宽现有 release/truth wording 来“伪完成” signing 或 code scanning。
- 不得为了 continuity 表面好看而引入不真实的 CODEOWNERS / delegate 承诺。
- 不得削弱现有 runtime `pip-audit`、governance guards、version truth 与 release identity evidence 的可信度。

## Canonical References

### Route / Governance Truth
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/PROJECT.md`
- `.planning/v1.3-MILESTONE-AUDIT.md`

### Release / Support / Security Truth
- `README.md`
- `README_zh.md`
- `SUPPORT.md`
- `SECURITY.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `.github/CODEOWNERS`
- `.github/workflows/release.yml`
- `.github/workflows/ci.yml`

### Existing Guards / Truth Tests
- `tests/meta/test_governance_closeout_guards.py`
- `tests/meta/test_governance_release_contract.py`
- `tests/meta/test_toolchain_truth.py`
- `tests/meta/test_version_sync.py`
- `tests/meta/test_public_surface_guards.py`

## Expected Scope

### In scope
- continuity / custody / freeze-escalation contract
- artifact signing design + workflow landing
- hard code-scanning / release gate truth
- public docs / runbook / guards convergence

### Out of scope
- vendor protocol crypto replacement
- runtime/protocol hotspot slimming
- broad-exception burn-down
- giant test third-wave topicization

## Open Planning Questions

1. continuity 的最低真实可落地形态，是 documented delegate、escrow-like custody，还是 freeze-escalation + explicit unavailability posture？
2. signing 的最小硬化方案，是 GitHub-native signing/verification，还是独立 artifact signature + published verification path？
3. code scanning 应成为 PR gate、release gate，还是两者都要有不同 blocking contract？
4. 哪些 meta guards 最适合承载“hard gate 已存在”与“continuity truth 不得漂移”的 no-regression contract？

---

*Phase directory: `34-continuity-and-hard-release-gates`*
*Context gathered: 2026-03-18 from retained tech-debt routing and current governance truth.*
