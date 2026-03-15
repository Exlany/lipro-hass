# Lipro Documentation Guide

> 根目录 `docs/` 只保留当前仍需直接阅读的文档，不再保留历史归档副本。

## 当前文档

- `NORTH_STAR_TARGET_ARCHITECTURE.md`：北极星目标架构与长期裁决基线
- `developer_architecture.md`：当前代码分层、主链、边界与开发者入口
- `TROUBLESHOOTING.md`：用户与贡献者共用的规范排障入口
- `MAINTAINER_RELEASE_RUNBOOK.md`：单维护者发布、打包与 release gate 运行手册
- `adr/README.md`：长期有效的架构决策与取舍记录

## 对外导航主链

- 用户排障：`README.md` / `README_zh.md` → `docs/TROUBLESHOOTING.md` → `SUPPORT.md`
- 贡献与评审：`CONTRIBUTING.md` → `.github/pull_request_template.md`
- 漏洞披露：`SECURITY.md`
- 维护者发版：`docs/MAINTAINER_RELEASE_RUNBOOK.md`

## 活跃治理真源

以下内容统一作为当前仓库真源：

- `.planning/PROJECT.md`
- `.planning/MILESTONES.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/milestones/*.md`
- `.planning/baseline/*.md`
- `.planning/reviews/*.md`
- `AGENTS.md`
- `CLAUDE.md`（仅作为 Claude Code 兼容入口）

## Phase 资产身份与开源治理

- **默认身份**：`.planning/phases/**` 是 phase 执行工作区；`*-PLAN.md`、`*-CONTEXT.md`、`*-RESEARCH.md` 与临时过程文件默认属于执行痕迹，不自动升级为长期治理真源。
- **提升条件**：只有被 `.planning/ROADMAP.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/milestones/*.md` 或 `.planning/reviews/*.md` 显式引用的 phase 证据，才作为长期跟踪资产保留。
- **发布门禁**：`.github/workflows/release.yml` 必须复用 `.github/workflows/ci.yml` 的治理与版本守卫，且只能从 `refs/tags/${RELEASE_TAG}` 构建资产，不能旁路发版。
- **对外入口**：贡献与披露契约统一收敛到 `CONTRIBUTING.md`、`docs/TROUBLESHOOTING.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.github/pull_request_template.md`、`.github/ISSUE_TEMPLATE/*.yml` 与 `SECURITY.md`。

## 维护原则

- `docs/` 根目录只保留当前仍需直接消费的文档
- 一次性审计、执行计划、收尾报告不再保留到仓库
- 任务执行过程默认沉淀到 `.planning/*` 的长期真源；phase 过程文件默认不作为 Git 长期跟踪对象
