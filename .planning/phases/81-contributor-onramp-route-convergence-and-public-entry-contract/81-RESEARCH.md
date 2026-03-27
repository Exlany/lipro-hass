# Phase 81 Research

## Audit signals

- `README.md`、`README_zh.md`、`docs/README.md`、`CONTRIBUTING.md`、`SUPPORT.md` 与 `SECURITY.md` 已各自具备较高质量内容，但 contributor / maintainer 的 first-hop 叙事仍分散在多个 section；读者需要跨文档自行拼接路由。
- `docs/README.md` 已明确 public fast path 与 bilingual boundary，是最适合承接统一入口矩阵的 canonical docs map；根 README 仍更像“产品概览 + 安装/使用说明”，适合保留 overview 身份而非承载过多 contributor 细节。
- `docs/developer_architecture.md` 与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 已提供 maintainer/developer 深层架构真相，但缺少一份 contributor-facing 的“允许改什么 / 不能越界什么 / 改完回写哪里”的变更地图。
- `SUPPORT.md`、`SECURITY.md` 与 `.github/ISSUE_TEMPLATE/*.yml` 已基本对齐 docs-first / private-access 事实；Phase 81 只需补强 contributor route 可达性，不应重开 Phase 83 的 intake 字段设计。
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 已形成 maintainer appendix，必须继续保持非 public first hop 身份；Phase 81 只能在 public docs 中把它描述为 maintainer-only appendix，而不能让其变成外部贡献者的默认入口。

## Chosen direction

### 1. Build one public/contributor entry matrix
把 `docs/README.md` 提升为唯一 canonical navigation map：
- 根 README / 中文 README 只保留 overview + 快速分流；
- `docs/README.md` 负责统一说明“用户从哪里开始、贡献者从哪里开始、维护者附录在哪里”；
- `CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md` 各自保留本领域契约，但在开头显式回链到同一入口矩阵。

### 2. Add a contributor-facing architecture change map
新增一份公开可链接、但不暴露 internal bootstrap folklore 的文档，建议落在：
- `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`

原因：
- 位于 `docs/` 下，天然属于 public docs tree；
- 不与 `developer_architecture.md`、`NORTH_STAR_TARGET_ARCHITECTURE.md` 争夺 authority，而是作为 contributor routing layer；
- 可被 README、docs index 与 CONTRIBUTING 三处稳定链接，在两跳内到达。

### 3. Keep Phase 81 scope honest
本 phase 只做：
- public first-hop convergence
- contributor-facing architecture change map
- focused guards 与 planning truth 的同步

本 phase 不做：
- release runbook / release evidence-chain 重写（Phase 82）
- issue / PR / security intake 字段扩张与 maintainer stewardship contract（Phase 83）
- open-source/governance 全量 guard freeze（Phase 84）
- 任何 runtime / protocol / control 生产代码重构

## Recommended information architecture

### Public routing
- `README.md` / `README_zh.md`
  - 保留项目概览、安装、功能、使用、支持/安全快速入口
  - 增加清晰的 contributor / maintainer route callout，统一指向 `docs/README.md`
- `docs/README.md`
  - 新增 “Start here / 从这里开始” 角色矩阵（user / contributor / maintainer）
  - 链接 `CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`docs/TROUBLESHOOTING.md`、新 architecture change map
- `CONTRIBUTING.md`
  - 开头明确先读 `docs/README.md`
  - 新增 architecture change map fast path
  - 保持 CI / lint / test / review contract 主体不变
- `SUPPORT.md` / `SECURITY.md`
  - 开头回链 `docs/README.md`
  - 明确“贡献问题先去 CONTRIBUTING，架构改动先看 architecture change map”

### Architecture change map structure
建议内容结构：
1. Why this page exists / 何时需要读这页
2. Five change families：protocol / runtime / control / external-boundary / governance
3. For each family:
   - allowed story
   - do-not-do list
   - canonical code/doc homes
   - required evidence destinations
   - recommended focused validation commands
4. Cross-links to `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` and `docs/developer_architecture.md`
5. Explicit non-goals：不暴露 active-route / archived pointer / GSD internal workflow

## File-level execution advice

### Plan 81-01
- 收口 README / README_zh / docs index / CONTRIBUTING / SUPPORT / SECURITY 的统一 first-hop story
- 避免在每个文件重复完整 routing prose，优先使用统一矩阵 + 定位清晰的短 callout

### Plan 81-02
- 新增 `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`
- 只在 README / docs index / CONTRIBUTING 添加必要入口，不把 SUPPORT / SECURITY 变成架构文档副本

### Plan 81-03
- focused guards 验证：
  - 双语 README 与 docs index 能到达 contributor / support / security / architecture map
  - architecture map 覆盖五类 change families
  - public docs 不把 `.planning/*` / internal governance 命令流当作 public first hop
- 同步基线与 review truth：`PUBLIC_SURFACES`、`VERIFICATION_MATRIX`、`FILE_MATRIX`、必要的 promoted asset / summary / verification

## Verification strategy

- 文档一致性：`uv run python scripts/check_file_matrix.py --check`
- focused tests：新增或扩展 docs/governance meta tests，覆盖 public entry links、architecture map reachability、bilingual route truth
- targeted suite：`uv run pytest -q tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_contract.py tests/meta/test_version_sync.py`
- 如新增专用 docs guard，则将其纳入 focused suite

## Risks and mitigations

- **Risk: public docs over-link internal governance**
  - Mitigation: architecture map 只引用公开 docs 与 contributor-visible obligations，不直接公开 `.planning/*` current-route 细节
- **Risk: README 与 docs index 双重成为 canonical**
  - Mitigation: README 只做 overview + routing，明确 docs index 是 canonical navigation map
- **Risk: scope bleed into Phase 82/83**
  - Mitigation: 不修改 maintainer release 流程正文，不扩张 issue/PR template 采集字段，仅在现有 public route 文案内保持一致

## Rejected alternatives

- **把 architecture map 写进 `developer_architecture.md`**：拒绝；那会把 maintainer/developer current topology 与 contributor routing 混在一起，降低外部贡献者可读性。
- **在 README 中完整复制 contributor rules**：拒绝；会加重 bilingual drift，并让 `docs/README.md` 失去 canonical map 身份。
- **本 phase 顺手重写 issue / PR templates**：拒绝；这是 Phase 83 的范围，会让 contributor route 与 intake contract 同轮耦合过深。
