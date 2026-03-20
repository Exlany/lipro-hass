# Phase 42: Delivery trust gates and validation hardening - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning
**Source:** formalized `v1.6` route from `Phase 41` remediation roadmap

<domain>
## Phase Boundary

本 phase 只处理四类 `v1.6` 的 delivery-trust / validation 尾债：

1. maintainer delegate / security fallback / custody truth 仍过度依赖单维护者隐性记忆；
2. release pipeline 仍缺少对 release artifact 的真实 install / uninstall smoke；
3. coverage 仍以 total floor 为主，缺少 changed-surface diff gate 与 local-vs-CI parity 的强约束；
4. compatibility / deprecation preview lane 尚未形成显式、可审计的前瞻信号。

本 phase 不进入 `control/` ↔ `services/` 解耦，不拆 `RuntimeAccess`，不处理 `.planning/phases/**` 降噪，也不切热点文件；这些分别留给 `Phase 43`、`Phase 44`、`Phase 45`。

</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- continuity / fallback truth 必须诚实：不得虚构隐藏 delegate、未公开 emergency maintainer 或不存在的 backup path。
- release smoke 必须验证“发布产物可用”，而不是只在源码树上重复打包逻辑；优先复用发布的 `install.sh` 与 release zip 语义。
- total coverage floor 继续保持 blocking；diff coverage 只能作为加强，不得以“显式 baseline 缺失”为借口变相放松 touched-surface 质量门禁。
- local tooling、CI workflow、PR template、contributor docs 必须讲同一条质量故事，避免“本地建议”和“CI真实执行”分裂。
- preview / deprecation lane 可以是 scheduled / workflow_dispatch 的非 stable lane，但必须明确不改变 stable support / release contract。

### Claude's Discretion
- compatibility preview lane 放在 `ci.yml` 还是单独 workflow；
- diff coverage 是基于 changed files、显式 baseline 还是二者组合；
- release smoke 的临时 Home Assistant 目录结构与清理方式。

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### North-star / planning truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` — 北极星终态与禁止项
- `AGENTS.md` — authority 顺序、phase trace/promote contract、执行限制
- `.planning/PROJECT.md` — 当前 `v1.6` active milestone truth
- `.planning/ROADMAP.md` — `Phase 42` 正式路线与依赖
- `.planning/REQUIREMENTS.md` — `GOV-34 / QLT-12 / QLT-13 / QLT-14` 真源
- `.planning/STATE.md` — 当前 execution status / next-command truth
- `.planning/phases/41-full-spectrum-architecture-code-quality-and-open-source-audit/41-REMEDIATION-ROADMAP.md` — 审计整改来源
- `.planning/phases/41-full-spectrum-architecture-code-quality-and-open-source-audit/41-AUDIT.md` — 审计结论与风险排序

### Release / continuity / support truth
- `.github/workflows/release.yml` — tagged release pipeline 与 security gate
- `.github/workflows/ci.yml` — current coverage / benchmark / governance / schedule contract
- `.github/CODEOWNERS` — current custody truth
- `SUPPORT.md` — support routing / continuity wording
- `SECURITY.md` — disclosure route / fallback wording
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` — maintainer continuity / release trust / verification story
- `.github/pull_request_template.md` — contributor-declared local quality contract
- `.github/ISSUE_TEMPLATE/bug.yml` — user-facing installation / support path wording
- `CONTRIBUTING.md` — local-vs-CI parity contract

### Tooling / guards
- `scripts/coverage_diff.py` — coverage floor / baseline diff checker
- `scripts/lint` — local quality command aggregator
- `tests/meta/test_governance_release_contract.py` — release/support/governance contract guard
- `tests/meta/test_version_sync.py` — release/runbook/latest-evidence linkage guard
- `tests/meta/test_toolchain_truth.py` — local/CI/tooling truth guard
- `tests/test_refactor_tools.py` — coverage/refactor helper contract

</canonical_refs>

<specifics>
## Specific Ideas

- `release.yml` 的 `security_gate` 应显式 `setup-python`，避免与其他 job 的 Python 选择口径分裂；
- artifact install smoke 可在临时目录下载/组装发布 zip，并通过 `install.sh` 验证安装与清理路径；
- diff coverage 可以延续 `scripts/coverage_diff.py`，但需要补“changed-surface”真义，不让 total coverage 掩盖新增低覆盖代码；
- preview lane 至少应能提前暴露 HA / dependency deprecation 风险，并以 step summary / artifact 给出可追踪信号；
- continuity wording 需要把“无已文档化 delegate”与“显式 fallback path”同时说清，而不是二选一。

</specifics>

<deferred>
## Deferred Ideas

- 不在本 phase 里为 `control/` / `services/` 新增解耦 helper 或 typed runtime read-model；
- 不在本 phase 里清理 `.planning/phases/**` 或术语漂移；
- 不在本 phase 里做热点文件拆薄或 typed result / reason code 重构；
- 不引入与现有 toolchain 风格冲突的新覆盖工具或新依赖，除非当前仓库已有可复用组件无法满足约束。

</deferred>

---

*Phase: 42-delivery-trust-gates-and-validation-hardening*
*Context gathered: 2026-03-20 via the Phase 41 remediation roadmap*
