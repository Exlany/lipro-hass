# Phase 46 Documentation, Toolchain, Workflow, Governance, and Open-Source Maturity Audit

## Scope and Method

- 审阅对象覆盖根入口与对外契约（`README.md`、`README_zh.md`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`）、文档索引与维护者附录（`docs/**`）、社区模板与工作流（`.github/**`）、本地工具链与安装路径（`pyproject.toml`、`.pre-commit-config.yaml`、`hacs.json`、`install.sh`、`scripts/**`），以及当前治理真源（`.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`、baseline / reviews 文件）。
- 总体结论：这是一个**发布/安全治理成熟度很高，但 continuity 明显受单维护者约束**的中高成熟开源仓库。
- 关键判断：本仓库最强项是 release-security-first 的严治理链路；最短板不是“缺文档/缺流程”，而是“接棒与连续性 contract 仍偏弱”。

## Public Entrypoints and Navigation

### Strengths

- `README.md` / `README_zh.md` 提供了清晰的 public fast-path：功能概览、安装、排障、支持与安全路由都在主入口中可见，且双语入口显式可达。
- `docs/README.md` 已把“公开入口”和“维护者附录”做了明确分层：普通贡献者/用户不需要先穿过 `.planning/*` 才能找到使用与贡献入口。
- `README.md` 没有把 maintainer-only 细节硬塞给普通用户；runbook、north-star、developer architecture 等较重材料被留在 `docs/README.md` 的深层入口中，这符合优秀开源项目的分层习惯。
- Troubleshooting、Support、Security、Contributing 和 GitHub 模板之间的导航关系已经形成链路，而不是互相孤立的“散页”。

### Gaps

- package metadata 中 `Documentation` URL 仍指向根 `README.md`，而不是更像 docs index 的 `docs/README.md`。这会让新贡献者较难第一时间发现 maintainer appendix 与治理索引。
- 根入口虽然克制，但 README 体量已达 `400+` 行，随着 release trust、advanced preview、diagnostics escalation 持续追加，后续仍需防止它再次长成“入口巨石”。
- `docs/README.md` 的 authority/索引角色是正确的，但 casual contributor 仍需理解一组较厚的治理文件，认知负担偏高。

### Verdict

- **Public fast-path：`A-`** —— 已达到成熟开源项目水平。
- **发现性：`B+`** —— 仍有 docs index 暴露不够直接的问题。

## Contributor and Maintainer Routing

### Strengths

- `CONTRIBUTING.md` 与 `.github/pull_request_template.md`、`.github/ISSUE_TEMPLATE/bug.yml`、`.github/ISSUE_TEMPLATE/config.yml` 的语言高度一致，能把贡献者引向 diagnostics、governance、release-trust 与验证矩阵，而不是靠口头默契。
- Support / Security / Runbook / Templates 共享同一条 continuity 叙事：公开 issue intake、私密安全披露、release custody truth、maintainer unavailable 时冻结新 tagged release 的约束都被明说了。
- `scripts/setup`、`scripts/develop`、`scripts/lint` 为本地开发提供了 uv 驱动的 setup / smoke / full lane，说明仓库并不是只关心 CI，不关心本地 DX。

### Gaps

- `CONTRIBUTING.md` 的验证矩阵很完整，但对 drive-by contributor 仍偏重；“认真贡献者友好”与“偶发贡献者低门槛”之间还有优化空间。
- `.pre-commit-config.yaml` 更多把重 gate 放在 pre-push，这有利于质量，但也意味着第一次贡献的反馈往往偏后。
- `scripts/agent_worker.py` 与 `scripts/orchestrator.py` 这类退役兼容 stub 仍与 active scripts 混放，会让首次维护者误判哪些脚本是当前主路径。

### Verdict

- **贡献路由：`A-`** —— 合同一致、约束明确。
- **维护成本：`B`** —— 路由强，但 cognitive load 依然高。

## Support Security and Release Continuity

### Strengths

- `.github/workflows/release.yml` 复用 `.github/workflows/ci.yml` 的治理门禁，而不是建立旁路发版故事线；这一点非常成熟。
- 发布链已经形成完整闭环：tagged CI reuse、runtime `pip-audit`、tagged CodeQL gate、tag/version matching、install smoke、SBOM、attestation/provenance、cosign sign/verify、release identity manifest。
- `README.md`、`SUPPORT.md`、`SECURITY.md`、runbook、bug 模板都明确区分 stable release path 与 preview / unsupported path，这比许多开源项目诚实得多。
- `install.sh` 会对本地 verified release assets 做 fail-closed checksum 验证，支持路径和风险提示基本明确。

### Gaps

- **最大 continuity 风险是 single-maintainer / no delegate**：`SUPPORT.md`、`SECURITY.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.github/CODEOWNERS` 都已诚实写出这一点，但也说明仓库的长期连续性强依赖单人。
- `install.sh` 在 remote 模式下默认解析最新 tagged release（`latest`），而 stable public guidance 更偏向 pinned / verified release assets。这不是文档错误，但确实会制造“方便路径”和“稳定契约”之间的张力。
- continuity 真相虽然统一，但仍需要在 `SUPPORT` / `SECURITY` / `runbook` / `CODEOWNERS` / `templates` / `GOVERNANCE_REGISTRY.json` 多处手工同步，维护成本高。

### Verdict

- **Release / supply-chain maturity：`A`** —— 仓库亮点之一。
- **Continuity / custody resilience：`C+`** —— 不是流程缺失，而是接棒 contract 偏弱。

## Bilingual Boundary and Audience Segmentation

### Strengths

- `README.md` 与 `README_zh.md` 的公开导航边界大体镜像，用户层的中英双语体验清楚。
- `CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、模板等允许在单文件中双语表达，这种策略比完全复制双份文件更低维护。
- `docs/README.md` 已明确 maintainer appendix 不强制镜像，这对减少文档噪音是正确取舍。

### Gaps

- maintainer appendix 与治理真源明显以中文为主；这不会伤害终端用户，但会增加未来非中文 delegate / custodian 的接棒摩擦。
- 当前双语边界“策略上正确”，但仍高度依赖维护者自觉保持同步；随着 runbook / support / security contract 继续深化，未来仍需 guard against bilingual drift。

### Verdict

- **Public bilingual boundary：`A-`** —— 已可公开消费。
- **Maintainer-globalization readiness：`B-`** —— 下一步更适合做英文摘要/索引，而不是全文镜像。

## Workflow and Release Trust

### Strengths

- `pyproject.toml`、`hacs.json`、README、Support、Security、governance registry 在最低 HA / Python 版本真相上保持一致。
- `ci.yml` 的 lane 分工成熟：lint、governance、security、test、benchmark、compatibility preview、validate(HACS/Hassfest) 各自承担单一职责。
- 质量门禁不止于“能跑”：还包含 changed-surface coverage、benchmark baseline compare、compatibility preview advisory lane 等高级质量信号。
- `release.yml` 上的“复用 CI + tagged hard gates”是国际优秀开源案例级别的做法。

### Gaps

- private repo / fork 场景下 HACS validation 会被跳过；这对主仓无害，但会弱化下游 fork 的一层 guard。
- benchmark / governance / release truth 链路已经很强，但同时意味着仓库更偏“高治理工程资产”，而不是“低门槛社区玩具”；需要在对外沟通上持续保持诚实。

### Verdict

- **Workflow discipline：`A`**
- **Fork / derivative resilience：`B`**

## Toolchain and Config Discipline

### Strengths

- `uv` 已成为一等执行面：README、Contributing、pre-commit、CI、脚本基本都围绕 `uv run` / `uv sync` 组织。
- `pyproject.toml` 同时收敛了 pytest、mypy、ruff 规则，`mypy strict = true` 与多条 lint 规则说明静态约束不是表面工程。
- `.pre-commit-config.yaml` 同步了 ruff format/check、mypy、translations、architecture policy、file matrix、pytest gates，形成了本地与 CI 一致的 guard story。
- `install.sh` 的风控意识很强：fail-closed、最小 Python 版本校验、archive/tag 语义区分、mirror opt-in 警告都清楚。

### Gaps

- `scripts/` 中 active tooling 与 retired stubs 并存，建议显式标记 active/deprecated，或将退役脚本挪至单独子目录以降低噪音。
- `Documentation` URL 指向根 README 而非 docs index，是一个小但真实的配置体验缺口。
- 本地验证体验虽然不差，但“默认快路”和“完整 CI-like 路径”的心智模型仍可进一步压缩，例如把 `./scripts/lint --full` 更明确地提升为单一推荐入口。

### Verdict

- **Toolchain clarity：`A-`**
- **Config discoverability：`B+`**

## Planning Truth and Promoted Evidence

### Strengths

- `.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`、baseline matrix、review ledgers 形成了强治理真源体系。
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 清楚限定了哪些 phase 资产能被长期引用，这对避免 phase workspace 污染 current truth 非常关键。
- `v1.6` archived truth 已与 `v1.7 / Phase 46` future route 种入对齐，说明仓库不会随意复活旧审计 story。
- `docs/README.md` 已正确把 `.planning/*` 定义为维护者 / 审阅层入口，而不是面向普通用户的第一层文档。

### Gaps

- 治理真源数量很大；“有 authority matrix”不等于“新维护者很容易第一时间找到 authority matrix”。
- continuity / release / contributor / archive promotion 故事线已经被压成多文件协同，优点是严谨，代价是同步成本高。
- `.planning/codebase/*` 与 phase workspace 的派生/执行痕迹边界虽然已有文字说明，但对首次维护者仍然偏厚。

### Verdict

- **Governance truth rigor：`A`**
- **Governance navigation cost：`B`**

## Priority Findings

### P0

1. **建立 documented delegate / successor / release custody recovery contract**：这是当前最真实的仓库级 continuity 风险，优先级高于再加更多 guard。
2. **把 continuity truth 从“诚实披露”升级为“可执行 custody plan”**：至少要明确 delegate 缺位、custody freeze、handoff 条件、最小替补职责与对应文档同步点。

### P1

1. **压缩 `scripts/` 噪音**：为 active / deprecated tooling 建正式索引，或把退役 stub 挪到单独 home。
2. **评估 installer stable/preview 语义**：考虑是否进一步降低 remote unpinned `latest` 的产品化歧义。
3. **继续压缩 contributor DX 心智负担**：让本地“一键 full lane”更显眼，减少贡献者在 README / CONTRIBUTING / scripts 之间来回跳转。

### P2

1. **把 `project.urls.Documentation` 指向 `docs/README.md`**，提升文档发现性。
2. **为 maintainer appendix 提供英文摘要索引**，降低未来非中文 custodian 的接棒摩擦。
3. **继续保持 `.planning` 索引优先、证据后置**，避免 casual contributor 被 phase/milestone 文件海淹没。
