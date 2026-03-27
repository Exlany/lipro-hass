# Phase 82 Research — Release operations closure and evidence-chain formalization

## Summary

`Phase 81` 已把 public entry / contributor route 收口完成；`Phase 82` 的真实缺口不在生产代码，而在 maintainer-facing release route 与 archived evidence pull-chain 之间仍有几处叙事分叉。最佳策略不是重写 workflow，而是把 runbook / changelog / docs appendix / archive evidence / planning truth / focused guards 收口为单一路由，并让历史档案退回 archive-only 身份。

## What the current repo already gets right

- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 已是很强的 maintainer release home：清楚声明 CI reuse、tagged `pip-audit`、tagged `CodeQL` gate、`SHA256SUMS`、`SBOM`、artifact attestation / provenance、`cosign` signing、release identity manifest 与 compatibility preview advisory lane
- `.github/workflows/release.yml` 与 `.github/workflows/ci.yml` 已在实现上承认同一条 tagged release gate；没有发现必须立即调整的 workflow drift
- `tests/meta/test_governance_release_contract.py`、`tests/meta/test_governance_release_docs.py`、`tests/meta/test_version_sync.py` 已提供很好的 focused guard foundation
- `docs/README.md` 已把 runbook 放进 maintainer appendix，而不是 public first hop

## Concrete gaps found

### 1. Archived evidence docs still leak live-route wording

当前 `.planning/reviews/V1_21_EVIDENCE_INDEX.md` 与 `.planning/v1.21-MILESTONE-AUDIT.md` 仍保留 `no active milestone route / next = $gsd-new-milestone` 这一类 closeout 时态叙事。`

问题不在于这段历史结论“曾经错误”，而在于 active milestone 已切到 `v1.22` 后，这些 archive-only assets 还在直接说“当前治理状态 / 下一步”。这会造成 maintainer 看到两套 current truth：

1. planning route contract 说当前是 `v1.22 active route / Phase 81 complete`
2. archive evidence / audit 又说当前是 `no active milestone route`

正确做法：保留历史 closeout 结论，但改为 archive-time / historical wording，禁止继续承担 live truth。

### 2. Authority matrix still over-explains active truth from the archive-evidence row

`.planning/baseline/AUTHORITY_MATRIX.md` 已正确声明 planning governance-route contract family 才是 live current truth 的 formal home，但 archive-evidence 行仍直接写出 active route 与 default-next。这个行项目的职责应退回“历史证据，不是 active truth”，不要再混放 live route。

### 3. Maintainer appendix still misses an explicit archived-evidence pull pointer

`docs/README.md` 已把 runbook 归为 maintainer appendix，但 هنوز缺少一条显式说明：若维护者需要 pull latest archived evidence / milestone audit，应从 `.planning/reviews/V1_21_EVIDENCE_INDEX.md` 与 `.planning/v1.21-MILESTONE-AUDIT.md` 进入，而且这是 maintainer-only appendix，不是 public first hop。

### 4. Changelog is not yet telling the same release story as the workflows/runbook

workflow 和 runbook 已落地的 release hardening 包括：
- CI reuse before release
- tagged runtime `pip-audit`
- fail-closed tagged `CodeQL` gate
- tagged build from `refs/tags/${RELEASE_TAG}`
- `SHA256SUMS` + install smoke
- `SBOM`
- attestation / provenance verification
- keyless `cosign` signing + verification
- release identity manifest
- verify-only / non-publish rehearsal
- compatibility preview advisory lane

但 `CHANGELOG.md` 的 `Unreleased` 尚未统一记账。对于开源维护者而言，这会形成“workflow exists but changelog forgot”的运营落差。

### 5. Focused guards need to freeze the post-Phase-82 truth

一旦 `Phase 82` 完成，至少以下 truth 需要一并冻结：
- `CURRENT_ROUTE = v1.22 active route / Phase 82 complete / latest archived baseline = v1.21`
- `CURRENT_MILESTONE_DEFAULT_NEXT = $gsd-discuss-phase 83`
- `GOV-60` / `ARC-21` 从 Planned → Completed
- GSD progress 从 `completed_phases = 1 / completed_plans = 3` → `completed_phases = 2 / completed_plans = 6`
- `phase-plan-index 82` 全部 `has_summary = true`
- archived evidence pointer 仍是 `.planning/reviews/V1_21_EVIDENCE_INDEX.md`

## File-level implementation advice

### Release route surfaces
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
  - 强化 Truth Sources 与 Preconditions，使其直接承认 changelog / version-sync triad / archived evidence pointer / docs appendix
  - 让本地 preflight 与 `ci.yml` governance lane 的实际 contract 保持单一路径
- `CHANGELOG.md`
  - 在 `Unreleased` 增补一组 maintainer-facing release-operations hardening notes
- `docs/README.md`
  - 在 Maintainer Appendix 中新增 archived evidence index + milestone audit reachability；明确 maintainer-only / not public first hop

### Archive-only evidence surfaces
- `.planning/baseline/AUTHORITY_MATRIX.md`
  - 把 archive-evidence row 改成纯 archive identity 说明，不再承担 current route
- `.planning/reviews/V1_21_EVIDENCE_INDEX.md`
  - 将“当前治理状态 / 下一条正式路线”改成 historical closeout wording
- `.planning/v1.21-MILESTONE-AUDIT.md`
  - Cross-Surface Integration / Next Step 一并改成 historical wording

### Freeze / guard surfaces
- `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`
  - route contract 前推到 `Phase 82 complete`
  - roadmap 把 `Phase 82` 标为 complete，并把 default next 改到 `83`
  - requirements 将 `GOV-60` / `ARC-21` 标为 completed，coverage 计数更新为 `4 complete / 4 pending`
- `.planning/baseline/VERIFICATION_MATRIX.md`
  - 更新 `v1.21 Milestone Closeout Contract` 的 current mutable story
  - 新增 `Phase 82 Release Operations Contract`
- `.planning/reviews/FILE_MATRIX.md`
  - 更新相关 docs/tests 的 phase ownership 描述，补充 `Phase 82`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
  - allowlist `Phase 82` 的 summary / verification / validation
- `tests/meta/governance_current_truth.py`
  - machine-readable current truth 前推到 `Phase 82 complete`
- `tests/meta/test_governance_release_contract.py`
  - 守卫 runbook / changelog / workflow / archive pointer 的单一路由
- `tests/meta/test_governance_release_docs.py`
  - 守卫 docs appendix reachability 与 archive pointer not-public-first-hop posture
- `tests/meta/test_governance_route_handoff_smoke.py`
  - GSD progress / next-phase / phase-plan-index 前推到 `82`
- `tests/meta/governance_followup_route_current_milestones.py`
  - active milestone / requirements coverage / route truth 前推到 `Phase 82`

## Verification strategy

优先运行 focused suites，再做 GSD fast-path truth proof：

```bash
uv run pytest -q tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_version_sync.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py
uv run python scripts/check_file_matrix.py --check
node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress
node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" phase-plan-index 82
```

如 touched scope 扩到 broader planning/review truth，可再补：

```bash
uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_milestone_archives.py tests/meta/test_governance_release_continuity.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_version_sync.py
```

## Risks and mitigations

- **Risk: archive docs lose historical honesty**
  - Mitigation: 保留“在 v1.21 closeout 时”的结论，只删除 current/live wording
- **Risk: docs appendix leaks into public first hop**
  - Mitigation: 只在 `docs/README.md` maintainer appendix 添加 archive pointer，不回流 root README
- **Risk: workflow/docs/tests three-way drift**
  - Mitigation: 优先增加 focused assertions，不轻易改 workflow YAML
- **Risk: Phase 82 scope bleed into Phase 83/84**
  - Mitigation: 不动 issue/PR/security templates，不做 full open-source guard expansion，只冻结 release route truth

## Rejected alternatives

- **直接重写 `release.yml` / `ci.yml`**：拒绝；当前实现已较成熟，收益低于重新引入 drift 的风险。
- **把 archived evidence pointer 放回根 README**：拒绝；这会污染 public first hop。
- **保留 archive docs 中的“当前治理状态”并靠读者理解它是历史语态**：拒绝；这会继续制造 parallel current truth。
- **顺手一起完成 Phase 83 的 intake/stewardship work**：拒绝；会模糊 GOV-60 / ARC-21 的验收边界。
