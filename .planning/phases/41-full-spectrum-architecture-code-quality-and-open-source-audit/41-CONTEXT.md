# Phase 41: Full-spectrum architecture, code quality, and open-source audit - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning
**Source:** v1.6 audit milestone initialization from direct user request

<domain>
## Phase Boundary

本 phase 只做两件事：

1. 以顶级架构师视角对 `lipro-hass` 全仓执行一次全谱系终极审阅；
2. 把审阅结论收束为可执行的分层整改路线图。

本 phase 不直接进行大规模实现重构，不隐式开启后续 remediation phase，不把 phase 临时资产误升为长期治理真源。
</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- 审阅必须覆盖 `custom_components/lipro/**`、`tests/**`、`docs/**`、`.github/**`、`scripts/**`、核心配置文件与 planning truth，不得只看代码目录。
- 审阅必须同时报告亮点与缺陷，且所有重要问题都要给出 severity、根因、受影响文件与整改方向。
- 审阅必须同时参考 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`docs/developer_architecture.md`、baseline/reviews 治理资产与现有实现/test truth，而非单点裁决。
- 输出必须严格区分 active truth、archived evidence、execution trace 与 repo hygiene noise。
- 最终 deliverables 固定为 `41-AUDIT.md`、`41-REMEDIATION-ROADMAP.md`、`41-SUMMARY.md`、`41-VERIFICATION.md`。

### Claude's Discretion
- 审阅问题的聚类方式与章节结构。
- quick wins / medium-term / long-term 的分组与排序。
- 是否把个别检查发现写入 summary，还是仅放入 audit 正文。
</decisions>

<canonical_refs>
## Canonical References

### North-star / governance truth
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `AGENTS.md`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`
- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`

### Source / tests / tooling
- `custom_components/lipro/**`
- `tests/**`
- `scripts/**`
- `.github/workflows/**`
- `pyproject.toml`
- `.pre-commit-config.yaml`
- `install.sh`

### Open-source / product surfaces
- `README.md`
- `README_zh.md`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`
- `CHANGELOG.md`
- `docs/**`
- `.github/ISSUE_TEMPLATE/**`
- `.github/pull_request_template.md`
- `hacs.json`
- `.devcontainer.json`
</canonical_refs>

<specifics>
## Specific Ideas

- 明确哪些目录/模块已经体现出高成熟度的 north-star 收敛，哪些仍只是“能跑但不够优雅”。
- 量化超大模块、广义异常捕获、stale naming、缓存/构建产物、测试巨石与 CI 复杂度。
- 特别关注开源项目的“第一次接触体验”：安装、贡献、问题反馈、安全披露、发布证据、双语一致性。
- 审阅路线图必须可执行，不能停留在抽象口号。
</specifics>

<deferred>
## Deferred Ideas

- 不在本 phase 内直接大规模重构 `custom_components/lipro/**`。
- 不在本 phase 内修改 baseline/review 真源来“粉饰”审阅结果。
- 不在本 phase 内重新定义 v1.5 的 archived story。
</deferred>

---

*Phase: 41-full-spectrum-architecture-code-quality-and-open-source-audit*
*Context gathered: 2026-03-20 via direct audit mandate*
