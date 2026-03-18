# Codebase Maps

> Snapshot: `2026-03-18`
> Freshness: Phase 37 对齐刷新；本目录只在 `AGENTS.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md`、`docs/developer_architecture.md` 与当前 CI/release/public-doc truth 所代表的截面上成立。上述真源一旦变化，本目录必须同步刷新或标记为历史观察。
> Derived collaboration map: `.planning/codebase/*.md` 是受约束的协作图谱 / 派生视图，用于帮助贡献者快速建立局部心智模型。
> Authority order: `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` -> `.planning/ROADMAP.md` -> `.planning/REQUIREMENTS.md` -> `.planning/STATE.md` -> `.planning/baseline/*.md` -> `.planning/reviews/*.md` -> `docs/developer_architecture.md` -> `AGENTS.md`。
> Conflict rule: 若本目录与上述权威链冲突，必须以后者为准；本目录不得自称当前治理真源，并应立即更新或明确标记为历史/过时观察。

## Usage

- 面向贡献者、审阅者与局部实现者；帮助导航目录、热点与测试镜像。
- 不反向定义 public surface、dependency、authority、residual 或 delete gate 真相。
- 不把 phase-local 过程资产升级成长期治理真源；长期仲裁仍以 baseline/review/roadmap/state 为准。

## Refresh Policy

- 当 active governance truth、toolchain truth、file ownership 或 residual judgment 变化时，本目录必须同步刷新。
- 已关闭残留不得继续写成 active concern / active residual / active kill target。
- 若某条观察仅具历史价值，必须显式写明 `Historical` / `历史观察`，不能悬空漂移。
