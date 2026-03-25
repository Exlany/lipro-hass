# Phase 75 Context

## Phase

- **Number:** `75`
- **Title:** `Access-mode truth closure, evidence promotion formalization, and thin-adapter typing hardening`
- **Milestone:** `v1.20 Runtime Bootstrap Convergence, Service-Family Deduplication & Legacy Residual Retirement`
- **Starting baseline:** `v1.20 active / Phase 74 complete / closeout-ready but not archived`
- **Archived reference:** `v1.19 archived / evidence-ready`

## Why This Phase Exists

终极全仓审阅后，主架构主链依旧稳定，但仍有三类不够诚实、会影响开源/治理专业度的尾口：

- **访问模式真相漂移**：仓库当前通过 `gh repo view Exlany/lipro-hass --json visibility,url,isPrivate` 可证实为 `PRIVATE`，但 `README*`、`SUPPORT.md`、`SECURITY.md`、`.github/ISSUE_TEMPLATE/*`、`pyproject.toml` 与 `manifest.json` 仍大量叙述“当前仓库可直接走 HACS / public Releases / public Issues / public Discussions / GitHub Security Advisory”。这会让外部读者看到 404，并误判项目对外可达性。
- **closeout formalization lag**：`v1.20` milestone audit 已采信 `Phase 72/73/74` 的 summary / verification / validation 证据，但 `.planning/reviews/PROMOTED_PHASE_ASSETS.md` 与 `.planning/baseline/VERIFICATION_MATRIX.md` 尚未把这些 phase 的 closeout 资产正式提升到 allowlist / exit contract 层，`STATE.md` 对 phase execution trace 与 promoted evidence 的表述也偏弱。
- **薄适配器 typing 仍可继续诚实化**：`custom_components/lipro/diagnostics.py`、`custom_components/lipro/system_health.py` 与 `custom_components/lipro/flow/options_flow.py` 仍残留局部 `Any` / 宽口 object story；它们不构成架构错误，但在当前 closeout 阶段应进一步收紧，让 public/control thin adapters 与 options schema 更贴近正式 typed contract。
- **历史主链依赖仍要被显式承认**：本 phase 站在 `runtime_access` 已完成 formal-home convergence 的基础上继续做 truth closure，不得回退为第二条 runtime/control 故事线。

## In Scope

- `README.md`
- `README_zh.md`
- `CONTRIBUTING.md`
- `SUPPORT.md`
- `SECURITY.md`
- `docs/README.md`
- `docs/TROUBLESHOOTING.md`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `pyproject.toml`
- `custom_components/lipro/manifest.json`
- `.planning/PROJECT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`
- `custom_components/lipro/diagnostics.py`
- `custom_components/lipro/system_health.py`
- `custom_components/lipro/flow/options_flow.py`
- touched tests in `tests/core/**`, `tests/flows/**`, `tests/meta/**`

## Constraints

- **不编造不存在的 public route**：当前仓库是 private-access；若没有可验证的 public mirror / public release surface，就不能把 HACS、public Discussions、public Issues、GitHub Security Advisory 当成当前仓库默认可用路径继续承诺。
- **不能把 repo visibility 问题伪装成代码问题**：仓库是否转为 public 是 repo setting / owner 决策；仓内本轮只能做到“文档与 metadata 叙事诚实”，不能假装已经修复外部可见性。
- **promoted evidence 只讲 allowlist 真相**：被 Git 跟踪的 phase 文件不自动升级为长期治理证据；allowlist、verification matrix、state wording 必须讲同一条故事。
- **typing hardening 只收紧 formal thin adapters**：不得借 typing 清理重开第二条架构故事线，也不得把 runtime/control/protocol formal homes 重新打散。
- **所有 Python / test / script 命令统一使用 `uv run ...`**。
