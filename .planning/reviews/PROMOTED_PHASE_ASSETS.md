---
policy:
  default_identity: execution-trace
  promotion_contract: Only assets listed under `phases` count as long-term governance/CI evidence for `.planning/phases/**`.
  promotion_sources:
    - .planning/ROADMAP.md
    - .planning/baseline/VERIFICATION_MATRIX.md
    - .planning/milestones/*.md
    - .planning/reviews/*.md
phases:
  07.5-integration-governance-verification-closeout:
    - 07.5-SUMMARY.md
    - 07.5-01-SUMMARY.md
    - 07.5-02-SUMMARY.md
    - 07.5-VALIDATION.md
    - 07.5-VERIFICATION.md
  08-ai-debug-evidence-pack:
    - 08-01-SUMMARY.md
    - 08-02-SUMMARY.md
    - 08-VALIDATION.md
    - 08-VERIFICATION.md
  15-support-feedback-contract-hardening-governance-truth-repair-and-maintainability-follow-through:
    - 15-01-SUMMARY.md
    - 15-02-SUMMARY.md
    - 15-03-SUMMARY.md
    - 15-04-SUMMARY.md
    - 15-05-SUMMARY.md
    - 15-VALIDATION.md
    - 15-VERIFICATION.md
  16-post-audit-truth-alignment-hotspot-decomposition-and-residual-endgame:
    - 16-01-SUMMARY.md
    - 16-02-SUMMARY.md
    - 16-03-SUMMARY.md
    - 16-04-SUMMARY.md
    - 16-05-SUMMARY.md
    - 16-06-SUMMARY.md
    - 16-VALIDATION.md
    - 16-VERIFICATION.md
  17-final-residual-retirement-typed-contract-tightening-and-milestone-closeout:
    - 17-01-SUMMARY.md
    - 17-02-SUMMARY.md
    - 17-03-SUMMARY.md
    - 17-04-SUMMARY.md
    - 17-VALIDATION.md
    - 17-VERIFICATION.md
  19-headless-consumer-proof-adapter-demotion:
    - 19-01-SUMMARY.md
    - 19-02-SUMMARY.md
    - 19-03-SUMMARY.md
    - 19-04-SUMMARY.md
    - 19-VALIDATION.md
    - 19-VERIFICATION.md
  21-replay-exception-taxonomy-hardening:
    - 21-01-SUMMARY.md
    - 21-02-SUMMARY.md
    - 21-03-SUMMARY.md
    - 21-VERIFICATION.md
  22-observability-surface-convergence-and-signal-exposure:
    - 22-01-SUMMARY.md
    - 22-02-SUMMARY.md
    - 22-03-SUMMARY.md
    - 22-VERIFICATION.md
  23-governance-convergence-contributor-docs-and-release-evidence-closure:
    - 23-01-SUMMARY.md
    - 23-02-SUMMARY.md
    - 23-03-SUMMARY.md
    - 23-VERIFICATION.md
  24-final-milestone-audit-archive-readiness-and-v1-3-handoff-prep:
    - 24-01-SUMMARY.md
    - 24-02-SUMMARY.md
    - 24-03-SUMMARY.md
    - 24-04-SUMMARY.md
    - 24-05-SUMMARY.md
    - 24-VERIFICATION.md
  30-protocol-control-typed-contract-tightening:
    - 30-VERIFICATION.md
  31-runtime-service-typed-budget-and-exception-closure:
    - 31-VERIFICATION.md
  32-truth-convergence-gate-honesty-and-quality-10-closeout:
    - 32-VERIFICATION.md
  33-contract-truth-unification-hotspot-slimming-and-productization-hardening:
    - 33-SUMMARY.md
    - 33-VERIFICATION.md
  34-continuity-and-hard-release-gates:
    - 34-SUMMARY.md
    - 34-VERIFICATION.md
  35-protocol-hotspot-final-slimming:
    - 35-01-SUMMARY.md
    - 35-02-SUMMARY.md
    - 35-03-SUMMARY.md
    - 35-SUMMARY.md
    - 35-VERIFICATION.md
  36-runtime-root-and-exception-burn-down:
    - 36-01-SUMMARY.md
    - 36-02-SUMMARY.md
    - 36-03-SUMMARY.md
    - 36-SUMMARY.md
    - 36-VERIFICATION.md
  37-test-topology-and-derived-truth-convergence:
    - 37-01-SUMMARY.md
    - 37-02-SUMMARY.md
    - 37-03-SUMMARY.md
    - 37-SUMMARY.md
    - 37-VERIFICATION.md
  38-external-boundary-residual-retirement-and-quality-signal-hardening:
    - 38-SUMMARY.md
    - 38-VERIFICATION.md
---

# Promoted Phase Assets

此白名单是 `.planning/phases/**` 的显式提升登记册。

- 仅 frontmatter `phases` 下列出的 phase 资产，才视为长期治理 / CI 证据。
- 未列出的 `*-PLAN.md`、`*-CONTEXT.md`、`*-RESEARCH.md`、`*-PRD.md`、`*-ARCHITECTURE.md`、`*-UAT.md` 默认仍是执行痕迹。
- 若未来要把新的 phase 资产纳入长期守卫，必须先在 `ROADMAP` / `VERIFICATION_MATRIX` / 里程碑文档 / reviews 文档中显式拉升，再更新此清单。
