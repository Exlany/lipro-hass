# Lipro Documentation Guide

> 根目录 `docs/` 只保留当前仍需直接阅读的文档，不再保留历史归档副本。

## 当前文档

- `NORTH_STAR_TARGET_ARCHITECTURE.md`：北极星目标架构与长期裁决基线
- `developer_architecture.md`：当前代码分层、主链、边界与开发者入口
- `adr/README.md`：长期有效的架构决策与取舍记录

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

## 维护原则

- `docs/` 根目录只保留当前仍需直接消费的文档
- 一次性审计、执行计划、收尾报告不再保留到仓库
- 任务执行过程默认沉淀到 `.planning/*` 的长期真源；phase 过程文件默认不作为 Git 长期跟踪对象
