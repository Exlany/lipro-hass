# Phase 51: Continuity automation, governance-registry projection, and release rehearsal hardening - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning
**Source:** `v1.8` milestone seed + `Phase 46 -> 50` closeout evidence + targeted governance/readiness reread

<domain>
## Phase Boundary

本 phase 只处理 `v1.8` 首轮、且在不触碰 runtime/protocol formal-root 代码的前提下即可显著提高仓库可持续性的三类问题：

1. maintainer-unavailable / delegate / custody / freeze / restoration 目前仍主要是多份文档之间的约定；它们需要升级成更可演练、更低摩擦、更 machine-checkable 的 continuity contract；
2. `.planning/baseline/GOVERNANCE_REGISTRY.json` 虽已成为 machine-readable truth，但下游 docs / templates / contributor guidance 仍存在手工同步成本，后续 drift 风险仍偏高；
3. release trust 虽然很强，但 verify-only / non-publish rehearsal 仍不够一等公民，且按变更类型给出最小充分本地验证矩阵的 contributor guidance 仍偏弱。

本 phase 不处理 `LiproProtocolFacade` second-round slimming、`Coordinator` / `__init__.py` / `EntryLifecycleController` 限流、`AnonymousShareManager` / diagnostics helper hotspot formalization，或 mega-test topicization round 2；这些进入 `Phase 52 -> 55`。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- continuity truth 必须继续保持 single-maintainer honesty，不得暗示 hidden delegate、备用发布人、或第二条维护主线。
- governance registry 若继续承担 projection truth，必须是“减少手工同步的 single source helper”，而不是反向创造第二套 public truth。
- verify-only / non-publish rehearsal 必须保持“验证但不发布”语义，不能削弱现有 tagged release / publish gate。
- change-type validation guidance 必须优先复用现有 CI / meta guard / docs truth，不新增一套与 CI 分离的 folklore checklist。
- `v1.6` 继续是 latest shipped archive baseline；`v1.7` closeout truth 不得因 `v1.8` 启动而被改写为 active execution story。

### Claude's Discretion
- continuity drill 是通过更清晰的 docs contract、模板约束、runbook checklist 还是 registry-backed helper 收口；
- governance-registry projection 是通过生成脚本、集中 helper 还是更窄的 shared metadata block 完成；
- change-type validation guidance 是表格、decision tree 还是 fast-path bullets；只要可维护、可守卫即可。

</decisions>

<canonical_refs>
## Canonical References

- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/reviews/V1_8_MILESTONE_SEED.md`
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-AUDIT.md`
- `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-SCORE-MATRIX.md`
- `.planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-SUMMARY.md`
- `.planning/phases/50-rest-typed-surface-reduction-and-command-result-ownership-convergence/50-VERIFICATION.md`
- `SUPPORT.md`
- `SECURITY.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `CONTRIBUTING.md`
- `docs/README.md`
- `.github/CODEOWNERS`
- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/pull_request_template.md`
- `.github/workflows/release.yml`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
- `tests/meta/test_governance_release_contract.py`
- `tests/meta/test_toolchain_truth.py`
- `tests/meta/test_governance_followup_route.py`
- `tests/meta/test_version_sync.py`

</canonical_refs>

<specifics>
## Specific Ideas

- 把 maintainer-unavailable story 明确成“谁记录、谁接管、谁冻结、谁恢复、谁验证”的 drill，而不是分散在 support/security/runbook 的 prose；
- 给 governance registry 一个更显式的 projection role，让 contributor / maintainer-facing metadata surfaces 不必各自手填同一批 truth；
- release workflow 增加 verify-only / non-publish rehearsal path，并在 CONTRIBUTING 中按 docs-only / governance-only / release-only 等 change type 给出最小验证命令；
- 保持公开 fast-path 与 maintainer appendix 分层，不把 runbook 内幕重新推回普通贡献者入口首层。

</specifics>

<deferred>
## Deferred Ideas

- 不在本 phase 内做 protocol root second-round slimming（`Phase 52`）。
- 不在本 phase 内做 runtime / entry-root second-round throttling（`Phase 53`）。
- 不在本 phase 内做 anonymous-share / diagnostics helper hotspot decomposition（`Phase 54`）。
- 不在本 phase 内做 second-wave mega-test topicization 或 repo-wide typing metric stratification（`Phase 55`）。

</deferred>

---

*Phase: 51-continuity-automation-governance-registry-projection-and-release-rehearsal-hardening*
*Context gathered: 2026-03-21 from v1.8 seed + post-Phase-50 governance reread*
