# CLAUDE.md

> Compatibility pointer for Claude Code — `AGENTS.md` remains the canonical repository contract.

## Purpose

- 让 Claude Code 能通过 `CLAUDE.md` 找到与其他代理一致的仓库规则。
- 不新增第二套规则，不覆盖 `AGENTS.md`、`docs/*` 或 `.planning/*` 真源。

## Read Order

1. `AGENTS.md`
2. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
3. `.planning/MILESTONES.md`
4. `.planning/PROJECT.md`
5. `.planning/ROADMAP.md`
6. `.planning/REQUIREMENTS.md`
7. `.planning/STATE.md`
8. `.planning/milestones/v1.0-ROADMAP.md`
9. `.planning/milestones/v1.0-REQUIREMENTS.md`
10. `.planning/baseline/*.md`
11. `.planning/reviews/*.md`
12. `docs/developer_architecture.md`
13. `docs/adr/README.md`

## Rules

- 若 `CLAUDE.md` 与 `AGENTS.md` 冲突，以 `AGENTS.md` 为准。
- `CLAUDE.md` 只为 Claude Code 兼容，不单独定义 truth source。
- 不再创建或依赖 `agent.md`。

## Current Focus

- 当前里程碑、阶段、推荐下一步以 `.planning/STATE.md` 为准。
