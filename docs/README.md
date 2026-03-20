# Lipro Documentation Guide

> 根目录 `docs/` 只保留当前仍需直接阅读的文档，不再保留历史归档副本。

## Public Fast Path

- `README.md` / `README_zh.md`：公开概览、安装契约与贡献/支持/安全入口
- `CONTRIBUTING.md` → `.github/pull_request_template.md`：贡献闭环与 PR 契约
- `docs/TROUBLESHOOTING.md` → `SUPPORT.md`：排障、diagnostics 与支持分流
- `SECURITY.md`：私密漏洞披露
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`：维护者专用的发版 / rehearsal / custody 附录

## Current Docs

- `NORTH_STAR_TARGET_ARCHITECTURE.md`：北极星目标架构与长期裁决基线
- `developer_architecture.md`：当前代码分层、主链、边界与开发者入口
- `TROUBLESHOOTING.md`：用户与贡献者共用的规范排障入口
- `MAINTAINER_RELEASE_RUNBOOK.md`：单维护者发布、打包与 release gate 运行手册
- `adr/README.md`：长期有效的架构决策与取舍记录

## Bilingual Boundary

- **必须镜像的公开入口**：`README.md` 与 `README_zh.md` 必须保持等价的 public entry navigation、安装契约与外部链接。
- **必须保持等价指导的入口**：`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`.github/pull_request_template.md` 与 `.github/ISSUE_TEMPLATE/*.yml` 必须给出一致的 contributor / support / security routing，即使具体实现为双语单文件。
- **允许 maintainer-only 的附录**：`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.planning/*`、milestone audit 与 phase evidence 索引可以保持维护者取向，但公开入口需要在需要时显式链接过去。

## Maintainer Appendix

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

## Historical Archive Reference

以下资产保留 archive / evidence / continuity 身份，供维护者审计、追溯与 handoff 使用，但**不是**当前治理真源：

- `.planning/MILESTONES.md`
- `.planning/milestones/*.md`
- `.planning/v1.6-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_6_EVIDENCE_INDEX.md`
- `.planning/v1.5-MILESTONE-AUDIT.md`
- `.planning/reviews/V1_5_EVIDENCE_INDEX.md`

## Phase 资产身份与开源治理 / Phase Asset Identity and Open Source Governance

- **默认身份**：`.planning/phases/**` 是 phase 执行工作区；`*-PLAN.md`、`*-CONTEXT.md`、`*-RESEARCH.md` 与临时过程文件默认属于执行痕迹，不自动升级为长期治理真源。
- **提升条件**：只有被 `.planning/ROADMAP.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/milestones/*.md` 或 `.planning/reviews/*.md` 显式引用的 phase 证据，才作为长期跟踪资产保留。
- **发布门禁**：`.github/workflows/release.yml` 必须复用 `.github/workflows/ci.yml` 的治理与版本守卫，且只能从 `refs/tags/${RELEASE_TAG}` 构建资产，不能旁路发版。
- **对外入口**：贡献与披露契约统一收敛到 `CONTRIBUTING.md`、`docs/TROUBLESHOOTING.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.github/pull_request_template.md`、`.github/ISSUE_TEMPLATE/*.yml` 与 `SECURITY.md`。

## Maintainer Rules

- `docs/` 根目录只保留当前仍需直接消费的文档。
- 一次性审计、执行计划、收尾报告不再保留到仓库。
- 任务执行过程默认沉淀到 `.planning/*` 的长期真源；phase 过程文件默认不作为 Git 长期跟踪对象。
