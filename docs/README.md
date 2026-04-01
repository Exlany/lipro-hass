# Lipro Documentation Guide / 文档导航

> 根目录 `docs/` 只保留当前仍需直接阅读的文档，不再保留历史归档副本。
> The `docs/` root keeps only current, directly consumed documents — not historical archive copies.

## Public Fast Path / 对外快速路径

- `README.md` / `README_zh.md` → `docs/README.md`：公开 first hop；从概览进入 canonical docs map 与 bilingual boundary。
  Public first hop from overview into the canonical docs map and bilingual boundary.
- `CONTRIBUTING.md` → `.github/pull_request_template.md`：贡献闭环、CI 契约与 PR 约定。
  Contribution workflow, CI contract, and PR expectations.
- `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`：面向贡献者的架构变更地图，解释允许改动边界、证据落点与 focused validation。
  Contributor-facing architecture change map for allowed change families, evidence destinations, and focused validation.
- `docs/TROUBLESHOOTING.md` → `SUPPORT.md`：排障、diagnostics 与支持分流。
  Troubleshooting, diagnostics, and support routing.
- `SECURITY.md`：私密漏洞披露。
  Private vulnerability disclosure.

## First-Hop Matrix / 首跳矩阵

- **Distribution / install / docs map / 分发、安装与文档总览**：`README.md` / `README_zh.md` → `docs/README.md`
  Canonical docs-first entry for every reader of this checkout.
- **Troubleshooting / bug triage / 排障与 Bug 分流**：`docs/TROUBLESHOOTING.md` → `SUPPORT.md`
  Issue forms are follow-up intake only when the current access mode exposes them.
- **Feature ideas / usage questions / 功能想法与使用问题**：`SUPPORT.md`
  GitHub Discussions are optional and only apply when the route is visible in the current access mode or a future public mirror preserves it.
- **Security reports / 安全问题**：`SECURITY.md`
  Private disclosure stays separate from the public bug / support route.

Current access-mode truth: this repository is private-access. GitHub-hosted Issues / Discussions / Releases / Security UI are therefore conditional follow-up surfaces, while the docs files above remain the only guaranteed first hop for every reader of this checkout.
当前访问模式真相：本仓库是 private-access，因此 GitHub 承载的 Issues / Discussions / Releases / Security UI 都只是条件性的后续入口；上面的文档文件才是当前 checkout 内对所有读者都保证成立的 first hop。

## Community-Health Contract / 社区协作契约

- `CONTRIBUTING.md`：贡献流程、PR intake，以及 boundary / impact / validation 的 review expectations。
  Contribution workflow, PR intake, and the review expectations for boundary / impact / validation.
- `SUPPORT.md`：公开 support routing、triage priority 与 continuity truth；安全问题仍先走 `SECURITY.md`。
  Public support routing, triage priority, and continuity truth; security reports still start with `SECURITY.md`.
- `SECURITY.md`：私密安全披露入口，不属于公开 issue first hop。
  Private security disclosure entry, not a public-issue first hop.

## Start Here by Role / 按角色分流

| Role / 角色 | Primary entry / 首选入口 | Next stop / 下一站 |
| --- | --- | --- |
| User / evaluator | `README.md` / `README_zh.md` | `docs/README.md` → `docs/TROUBLESHOOTING.md` → `SUPPORT.md` |
| Contributor | `CONTRIBUTING.md` | `.github/pull_request_template.md` |
| Architecture contributor | `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md` | `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` / `docs/developer_architecture.md` |
| Security reporter | `SECURITY.md` | private advisory route when reachable |
| Maintainer | `docs/MAINTAINER_RELEASE_RUNBOOK.md` | internal governance truth (maintainer-only) |

## Current Docs / 当前文档

- `NORTH_STAR_TARGET_ARCHITECTURE.md`：北极星目标架构与长期裁决基线。
  North-star target architecture and long-term authority baseline.
- `developer_architecture.md`：当前代码分层、主链、边界与开发者入口。
  Current code layering, main chain, boundaries, and developer entrypoints.
- `CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`：面向贡献者的变更边界、证据回写位置与验证入口。
  Contributor-facing change boundaries, evidence destinations, and validation entrypoints.
- `TROUBLESHOOTING.md`：用户与贡献者共用的规范排障入口。
  Shared troubleshooting entry for users and contributors.
- `MAINTAINER_RELEASE_RUNBOOK.md`：单维护者发布、打包与 release gate 运行手册。
  Single-maintainer release, packaging, and release-gate runbook.
- `adr/README.md`：长期有效的架构决策与取舍记录。
  Long-lived architecture decisions and trade-offs.

## Release Hygiene / 发版清理

- **GitHub-facing release tree / GitHub 发布可见树**：根目录公开入口以 `README.md` / `README_zh.md`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`CHANGELOG.md`、`LICENSE` 与 `docs/` 当前文档为准；内部 governance / evidence 记录继续保持 maintainer-facing 身份，不作为 public first hop。
  Public GitHub release surfaces stay on the root public docs plus current `docs/` pages; internal governance/evidence records remain maintainer-facing rather than a public first hop.
- **Public release notes / 公开发布说明**：`CHANGELOG.md` 只承担对外 release notes summary；维护者侧 archived evidence、milestone audit 与 route-selector 细节继续留在 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 与 `.planning/` maintainer truth 中。
  `CHANGELOG.md` is the public release-notes summary only; maintainer-only archived evidence, milestone audits, and route-selector details stay in `docs/MAINTAINER_RELEASE_RUNBOOK.md` plus `.planning/` governance truth.
- **Metadata traceability / 元数据可追溯性**：`pyproject.toml::project.urls` 与 `custom_components/lipro/manifest.json` 中投影出去的 docs/support/security URL 必须跟随当前 package semver 指向对应 Git tag，而不是漂浮在 `main` 上。
  Docs/support/security metadata projections in `pyproject.toml::project.urls` and `custom_components/lipro/manifest.json` must track the current package Git tag rather than float on `main`.
- **Must not ride along / 不应随发版混入**：本地生成的 `coverage.*`、`.benchmarks/`、`.mypy_cache/`、`.pytest_cache/`、`.ruff_cache/`、`.venv/`、`__pycache__/`、`*.egg-info/`、scratch files 与一次性 research 输出必须在合并主线 / 发版前清走。
  Local generated artifacts, caches, scratch files, and one-off research output must be removed before merge/release.
- **Execution traces / 执行痕迹**：未被 promoted / referenced 的 `PLAN / CONTEXT / RESEARCH` 仍只是执行痕迹；公开文档不应把它们当作对外发布文档集的一部分。
  Non-promoted `PLAN / CONTEXT / RESEARCH` phase assets remain execution traces and must not be treated as part of the public release doc set.

## Tooling Entry Points / 工具入口

- **Active local entrypoints / 现役入口**：`./scripts/setup`、`./scripts/develop`、`./scripts/lint`
- **Explicit Python/CI commands / 显式命令真源**：`CONTRIBUTING.md` 中的 `uv run ...` 分组命令
- **Retired compatibility stubs / 退役兼容壳**：`scripts/agent_worker.py`、`scripts/orchestrator.py` —— 仅在维护中的文档 / 自动化仍需要这些名称作为 unsupported 的 fail-fast migration hint 时保留；它们不是 supported workflow，请改走 `docs/README.md` 与 `CONTRIBUTING.md`

## Bilingual Boundary / 双语边界

- **必须镜像的公开入口**：`README.md` 与 `README_zh.md` 必须保持等价的 public entry navigation、安装契约与外部链接。
  `README.md` and `README_zh.md` must keep equivalent public-entry navigation, install contract, and outbound links.
- **必须保持等价指导的入口**：`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`.github/pull_request_template.md` 与 `.github/ISSUE_TEMPLATE/*.yml` 必须给出一致的 contributor / support / security routing，即使具体实现为双语单文件。
  Contributor / support / security routing must stay equivalent across these surfaces even when implemented as bilingual single files.
- **允许 maintainer-only 的附录**：`docs/MAINTAINER_RELEASE_RUNBOOK.md`、内部 governance 记录、milestone audit 与 phase evidence 索引可以保持维护者取向；公开入口可按需显式链接过去，但不得让其取代 public first hop。
  Maintainer-only appendices may stay maintainer-facing, but public entrypoints may link there only when needed and must not let them replace the public first hop.

## Maintainer Appendix / 维护者附录

- `docs/MAINTAINER_RELEASE_RUNBOOK.md`：维护者专用的发版 / rehearsal / custody / pull-only archived evidence 附录，不属于 public first hop。
  Maintainer-only release, rehearsal, custody, and pull-only archived-evidence appendix; not part of the public first hop.
- Registry-backed maintainer routing / rehearsal metadata 会投影到 contributor docs 与 GitHub templates 以降低 drift。
  Registry-backed maintainer routing / rehearsal metadata is projected into contributor docs and GitHub templates to reduce drift.
- **Archived evidence route / 归档证据路由**：latest archived evidence index 与 archived milestone audit 继续以 pull-only 方式由 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 维护；docs index 只保留 maintainer appendix reachability，不直接暴露 internal governance paths。
  The latest archived evidence index and archived milestone audit stay pull-only through `docs/MAINTAINER_RELEASE_RUNBOOK.md`; the docs index keeps appendix reachability without exposing internal governance paths directly.
- **Package semver / 包版本真源**：release-compatible package version 必须同步于 `pyproject.toml`、`custom_components/lipro/manifest.json` 与 `custom_components/lipro/const/base.py`。
  Release/package semver must stay synchronized across `pyproject.toml`, `custom_components/lipro/manifest.json`, and `custom_components/lipro/const/base.py`.
- **Internal governance milestones / 内部治理里程碑**：`v1.20`、`Phase 74` 之类标识只表示内部治理路线，不表示 package release semver，也不能替代 Git tag / package version。
  Milestone/phase identifiers such as `v1.20` or `Phase 74` are internal governance route IDs, not package release semver.
- **Maintainer truth sources / 维护者真源**：维护者真相保留在 active internal governance set，以及 `AGENTS.md` 与 `CLAUDE.md`（仅 Claude Code 兼容入口）。
  Maintainer truth lives in the active internal governance set plus `AGENTS.md` and `CLAUDE.md` compatibility entrypoints.

## Phase 资产身份与开源治理 / Phase Asset Identity and Open Source Governance

- **默认身份**：`.planning/phases/**` 默认是执行工作区；`*-PLAN.md`、`*-CONTEXT.md`、`*-RESEARCH.md` 与临时过程文件默认属于执行痕迹，不自动升级为长期治理真源。
- **提升条件**：只有被 `.planning/ROADMAP.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/milestones/*.md` 或 `.planning/reviews/*.md` 显式引用的 phase 资产，才作为长期治理 / CI 证据保留。
- **发布门禁**：`.github/workflows/release.yml` 必须复用 `.github/workflows/ci.yml` 的治理与版本守卫，且只能从 `refs/tags/${RELEASE_TAG}` 构建资产，不能旁路发版。
- **对外入口**：贡献者契约统一收敛到 `CONTRIBUTING.md`、`.github/pull_request_template.md`、`.github/ISSUE_TEMPLATE/*.yml` 与 `SECURITY.md`；`docs/TROUBLESHOOTING.md`、`SUPPORT.md` 与 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 分别承担排障、支持分流与 maintainer appendix，不属于 public first hop。

## Maintainer Rules / 维护者规则

- `docs/` 根目录只保留当前仍需直接消费的文档。
- 一次性审计、执行计划、收尾报告不再保留到仓库。
- phase 过程文件默认是 execution trace；只有 promoted / referenced evidence 才作为 Git 长期跟踪对象。
