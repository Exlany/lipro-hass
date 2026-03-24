# Lipro Documentation Guide / 文档导航

> 根目录 `docs/` 只保留当前仍需直接阅读的文档，不再保留历史归档副本。  
> The `docs/` root keeps only current, directly consumed documents — not historical archive copies.

## Public Fast Path / 对外快速路径

- `README.md` / `README_zh.md` → `docs/README.md`：公开 first hop；从概览进入 canonical docs map 与 bilingual boundary。  
  Public first hop from overview into the canonical docs map and bilingual boundary.
- `CONTRIBUTING.md` → `.github/pull_request_template.md`：贡献闭环、CI 契约与 PR 约定。  
  Contribution workflow, CI contract, and PR expectations.
- `docs/TROUBLESHOOTING.md` → `SUPPORT.md`：排障、diagnostics 与支持分流。  
  Troubleshooting, diagnostics, and support routing.
- `SECURITY.md`：私密漏洞披露。  
  Private vulnerability disclosure.

## Release Hygiene / 发版清理

- **GitHub-facing release tree / GitHub 发布可见树**：根目录公开入口以 `README.md` / `README_zh.md`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`CHANGELOG.md`、`LICENSE` 与 `docs/` 当前文档为准；`.planning/*` 继续保持 maintainer-facing governance / evidence 身份，不作为 public first hop。  
  Public GitHub release surfaces stay on the root public docs plus current `docs/` pages; `.planning/*` remains maintainer-facing governance/evidence rather than a public first hop.
- **Must not ride along / 不应随发版混入**：本地生成的 `coverage.*`、`.benchmarks/`、`.mypy_cache/`、`.pytest_cache/`、`.ruff_cache/`、`.venv/`、`__pycache__/`、`*.egg-info/`、scratch files 与一次性 research 输出必须在合并主线 / 发版前清走。  
  Local generated artifacts, caches, scratch files, and one-off research output must be removed before merge/release.
- **Execution traces / 执行痕迹**：`.planning/phases/**` 中未被 promoted / referenced 的 `PLAN / CONTEXT / RESEARCH` 仍只是执行痕迹；公开文档不应把它们当作对外发布文档集的一部分。  
  Non-promoted `PLAN / CONTEXT / RESEARCH` phase assets remain execution traces and must not be treated as part of the public release doc set.

## Maintainer Appendix / 维护者附录

- `docs/MAINTAINER_RELEASE_RUNBOOK.md`：维护者专用的发版 / rehearsal / custody 附录，不属于 public first hop。  
  Maintainer-only release, rehearsal, and custody appendix; not part of the public first hop.
- `.planning/baseline/GOVERNANCE_REGISTRY.json`：registry-backed maintainer routing / rehearsal metadata，会投影到 contributor docs 与 GitHub templates 以降低 drift。  
  Registry-backed maintainer routing / rehearsal metadata projected into contributor docs and GitHub templates to reduce drift.
- `.planning/*`：治理、审阅、archive 与 evidence 真源。  
  Governance, review, archive, and evidence truth sources.

## Tooling Entry Points / 工具入口

- **Active local entrypoints / 现役入口**：`./scripts/setup`、`./scripts/develop`、`./scripts/lint`
- **Explicit Python/CI commands / 显式命令真源**：`CONTRIBUTING.md` 中的 `uv run ...` 分组命令
- **Retired compatibility stubs / 退役兼容壳**：`scripts/agent_worker.py`、`scripts/orchestrator.py` —— 仅保留为 unsupported 的 fail-fast deprecation 入口；请改走 `docs/README.md` 与 `CONTRIBUTING.md`

## Current Docs / 当前文档

- `NORTH_STAR_TARGET_ARCHITECTURE.md`：北极星目标架构与长期裁决基线。  
  North-star target architecture and long-term authority baseline.
- `developer_architecture.md`：当前代码分层、主链、边界与开发者入口。  
  Current code layering, main chain, boundaries, and developer entrypoints.
- `TROUBLESHOOTING.md`：用户与贡献者共用的规范排障入口。  
  Shared troubleshooting entry for users and contributors.
- `MAINTAINER_RELEASE_RUNBOOK.md`：单维护者发布、打包与 release gate 运行手册。  
  Single-maintainer release, packaging, and release-gate runbook.
- `adr/README.md`：长期有效的架构决策与取舍记录。  
  Long-lived architecture decisions and trade-offs.

## Bilingual Boundary / 双语边界

- **必须镜像的公开入口**：`README.md` 与 `README_zh.md` 必须保持等价的 public entry navigation、安装契约与外部链接。  
  `README.md` and `README_zh.md` must keep equivalent public-entry navigation, install contract, and outbound links.
- **必须保持等价指导的入口**：`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`.github/pull_request_template.md` 与 `.github/ISSUE_TEMPLATE/*.yml` 必须给出一致的 contributor / support / security routing，即使具体实现为双语单文件。  
  Contributor / support / security routing must stay equivalent across these surfaces even when implemented as bilingual single files.
- **允许 maintainer-only 的附录**：`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.planning/*`、milestone audit 与 phase evidence 索引可以保持维护者取向；公开入口可按需显式链接过去，但不得让其取代 public first hop。  
  Maintainer-only appendices may stay maintainer-facing, but public entrypoints may link there only when needed and must not let them replace the public first hop.

## Maintainer Truth Sources / 维护者真源

以下 `.planning/*` 与治理契约主要服务维护者 / 评审者，不是普通用户排障入口；用户仍应优先沿 README → troubleshooting → support 主链导航。

以下内容统一作为当前仓库真源：

- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/*.md`
- `.planning/baseline/GOVERNANCE_REGISTRY.json`
- `.planning/reviews/*.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`（`.planning/phases/**` promoted allowlist）
- `AGENTS.md`
- `CLAUDE.md`（仅作为 Claude Code 兼容入口）

## Historical Archive Reference / 历史归档参考

以下资产保留 archive / evidence / continuity 身份，供维护者审计、追溯与 handoff 使用，但**不是**当前治理真源：

- 最新 archive-ready governance baseline：`.planning/v1.16-MILESTONE-AUDIT.md`、`.planning/reviews/V1_16_EVIDENCE_INDEX.md`、`.planning/milestones/v1.16-ROADMAP.md`、`.planning/milestones/v1.16-REQUIREMENTS.md`
- 当前 active milestone route：`v1.17 / Phase 69` 已完成 `5/5` plans、focused proof、静态门禁与 final phase gate，并进入 closeout-ready；latest archived closeout pointer 保持为 `.planning/reviews/V1_16_EVIDENCE_INDEX.md`，下一步治理动作是 `$gsd-complete-milestone v1.17`，current-story 仍以 `.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md` 与 `.planning/STATE.md` 为准
- `.planning/MILESTONES.md`
- `.planning/milestones/*.md`
- `.planning/v1.16-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_16_EVIDENCE_INDEX.md`
- `.planning/v1.12-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_12_EVIDENCE_INDEX.md`
- `.planning/v1.6-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_6_EVIDENCE_INDEX.md`
- `.planning/v1.5-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_5_EVIDENCE_INDEX.md`

## Phase 资产身份与开源治理 / Phase Asset Identity and Open Source Governance

- **默认身份**：`.planning/phases/**` 是 phase 执行工作区；`*-PLAN.md`、`*-CONTEXT.md`、`*-RESEARCH.md` 与临时过程文件默认属于执行痕迹，不自动升级为长期治理真源。
- **提升条件**：只有被 `.planning/ROADMAP.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/milestones/*.md` 或 `.planning/reviews/*.md` 显式引用的 phase 证据，才作为长期跟踪资产保留。
- **发布门禁**：`.github/workflows/release.yml` 必须复用 `.github/workflows/ci.yml` 的治理与版本守卫，且只能从 `refs/tags/${RELEASE_TAG}` 构建资产，不能旁路发版。
- **对外入口**：贡献与披露契约统一收敛到 `CONTRIBUTING.md`、`docs/TROUBLESHOOTING.md`、`SUPPORT.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.github/pull_request_template.md`、`.github/ISSUE_TEMPLATE/*.yml` 与 `SECURITY.md`。

## Maintainer Rules / 维护者规则

- `docs/` 根目录只保留当前仍需直接消费的文档。
- 一次性审计、执行计划、收尾报告不再保留到仓库。
- phase 过程文件默认是 execution trace；只有 promoted / referenced evidence 才作为 Git 长期跟踪对象。
