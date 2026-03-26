# Contributing to Lipro Smart Home Integration / 贡献给 Lipro 智能家居集成

Thank you for your interest in contributing to the Lipro Smart Home integration!
感谢您有兴趣为 Lipro 智能家居集成做出贡献！

## Development Setup / 开发环境设置

### Prerequisites / 前置条件

- Python 3.14.2+
- uv (Astral)
- Git

### Version Truth / 版本真源

- Canonical minimum supported Home Assistant version: `2026.3.1` from `hacs.json`, kept in sync with the `pyproject.toml` dev pin (`homeassistant==2026.3.1`).
- Canonical Python toolchain truth: minimum Python `3.14.2`, with development / CI targeting Python `3.14` (`requires-python`, `mypy`, `ruff`, `pre-commit`, devcontainer, and CI stay aligned under that contract).
- 唯一 Python 工具链真相：最低 Python `3.14.2`，开发 / CI 目标为 Python `3.14`（`requires-python`、`mypy`、`ruff`、`pre-commit`、devcontainer 与 CI 都遵守这条契约）。
- 唯一最低支持 Home Assistant 版本真源：`pyproject.toml` 中的 `homeassistant==2026.3.1`。
- Private repository / fork note: CI skips HACS validation because HACS only supports public GitHub repositories.
- 私有仓库 / fork 说明：CI 会跳过 HACS validation，因为 HACS 只支持公开 GitHub 仓库。

### Quick Start / 快速开始

1. **Clone the repository / 克隆仓库**
   ```bash
   git clone https://github.com/Exlany/lipro-hass.git
   cd lipro-hass
   ```

2. **Set up development environment / 设置开发环境**
   ```bash
   ./scripts/setup
   ```
   This runs `uv sync --frozen --extra dev` and installs `pre-commit` hooks.
   该脚本会运行 `uv sync --frozen --extra dev` 并安装 `pre-commit` hooks。

3. **Start Home Assistant for development / 启动 Home Assistant 进行开发**
   ```bash
   ./scripts/develop
   ```

   The development entrypoint keeps other `config/custom_components/*` integrations intact and only refreshes `config/custom_components/lipro` before starting Home Assistant with `uv run hass -c config`.
   该开发入口会保留其他 `config/custom_components/*` 集成，仅刷新 `config/custom_components/lipro`，然后用 `uv run hass -c config` 启动 Home Assistant。

   For a non-destructive smoke check, run:
   如需执行非破坏性 smoke 验证，可运行：
   ```bash
   LIPRO_DEVELOP_SMOKE_ONLY=1 ./scripts/develop
   ```

   Access Home Assistant at http://localhost:8123
   在 http://localhost:8123 访问 Home Assistant

### 10-Minute Contribution Path / 10 分钟贡献路径

For a focused contribution loop, use this order:
如需走最短贡献闭环，建议按这个顺序执行：

1. `./scripts/setup`
2. `uv run pytest -q <targeted-tests>` for the files you changed / 针对改动文件先跑定向测试
3. `uv run ruff check . && uv run mypy` before opening a PR / 提交 PR 前至少跑一次静态检查
4. Run the full CI-equivalent suite only when the change touches shared runtime, protocol, governance, or release paths / 仅当改动触及共享 runtime、protocol、governance、release 路径时，再补全量验证

Need routing help? Use `SUPPORT.md`. Need maintainer continuity or release custody context? Use `docs/MAINTAINER_RELEASE_RUNBOOK.md`.
如需支持路由，请看 `SUPPORT.md`；如需维护者连续性或发版托管上下文，请看 `docs/MAINTAINER_RELEASE_RUNBOOK.md`。

Need the full docs map or bilingual boundary? Start with `docs/README.md`. Public troubleshooting / support routing stays on `docs/TROUBLESHOOTING.md` → `SUPPORT.md`, while `docs/MAINTAINER_RELEASE_RUNBOOK.md` remains a maintainer-only appendix.
如需文档总索引或双语边界，请先看 `docs/README.md`。公开排障 / 支持分流统一走 `docs/TROUBLESHOOTING.md` → `SUPPORT.md`，`docs/MAINTAINER_RELEASE_RUNBOOK.md` 则继续保持 maintainer-only appendix 身份。

Retired compatibility stubs such as `scripts/agent_worker.py` and `scripts/orchestrator.py` remain unsupported fail-fast entrypoints.
`scripts/agent_worker.py` 与 `scripts/orchestrator.py` 之类退役兼容壳继续作为 unsupported 的 fail-fast 入口保留。

## Navigation Boundaries / 导航边界

### Public contributor path / 对外贡献主链

- Public overview and first hop: `README.md`, `README_zh.md` → `docs/README.md`
- Contributor workflow and PR contract: `CONTRIBUTING.md` → `.github/pull_request_template.md`
- Troubleshooting and routing: `docs/TROUBLESHOOTING.md` → `SUPPORT.md`
- Private vulnerability disclosure: `SECURITY.md`

Current access-mode note: this repository is private-access. Treat the docs files in this checkout as the canonical first hop; GitHub issue / discussion / security UI routes only apply when your current access mode exposes them or when a future public mirror preserves the same contract.
当前访问模式说明：本仓库当前是 private-access。请把当前 checkout 中的文档文件视为唯一正式 first hop；GitHub issue / discussion / security UI 路径只有在你当前访问模式可见，或未来 public mirror 保持同一契约时才成立。

### Maintainer appendix / 维护者附录

- Release / rehearsal / custody continuity: `docs/MAINTAINER_RELEASE_RUNBOOK.md` (maintainer-only, not a public first hop)
- Registry-backed governance truth: `.planning/baseline/GOVERNANCE_REGISTRY.json`, projected into `CONTRIBUTING.md`, `docs/README.md`, and GitHub templates to reduce drift

### Bilingual Boundary / 双语边界

- `README.md` 与 `README_zh.md` 必须保持镜像的 public entry navigation / release-install contract。
- `CONTRIBUTING.md`、`SUPPORT.md` 与 `SECURITY.md` 必须保持等价的 contributor/support/security guidance，即使具体实现为单文件双语结构。
- `docs/MAINTAINER_RELEASE_RUNBOOK.md` 与 `.planning/*` 可保持 maintainer-only；公开入口可按需显式链接过去，但不得取代 public first hop。

- If you touch `README.md` / `README_zh.md` / `CONTRIBUTING.md` / `SUPPORT.md` / `SECURITY.md` / `.github/*` / release workflow, update `docs/README.md`, `docs/TROUBLESHOOTING.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, and `.planning/baseline/GOVERNANCE_REGISTRY.json` together, and do not leave silent defer behind.
- Public bug reports should start with diagnostics; developer report / one-click feedback is an escalation path only when diagnostics are insufficient or a maintainer explicitly asks for deeper debugging.
- Supported shell/manual install docs now start from verified release assets (`install.sh` + release zip + `SHA256SUMS`); `ARCHIVE_TAG=main` and mirror/branch fallback paths are preview-only and should not be documented as stable support routes.
- Continuity / custody truth stays in `SUPPORT.md`, `SECURITY.md`, and `docs/MAINTAINER_RELEASE_RUNBOOK.md`; do not duplicate the full maintainer appendix in root overview docs.

## Code Standards / 代码规范

### Linting and Formatting / 代码检查和格式化

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:
我们使用 [Ruff](https://docs.astral.sh/ruff/) 进行代码检查和格式化：

```bash
# Run local static/security checks / 运行本地静态+安全检查
./scripts/lint

# Run the full CI-like local matrix / 运行接近 CI 的完整本地矩阵
./scripts/lint --full

# Auto-fix issues / 自动修复问题
uv run ruff check . --fix

# Format code / 格式化代码
uv run ruff format .

# Type checking / 类型检查
uv run mypy
```

Notes:
说明：

- `./scripts/lint` 默认运行本地 static + translation + shell + runtime security smoke；它**不会**默认运行 governance 或 pytest。
  `./scripts/lint` runs local static + translation + shell + runtime security smoke by default; it does **not** run governance or pytest unless asked.
- `./scripts/lint --full` 会在默认检查之上补跑 architecture/file-matrix、governance guards、完整测试覆盖率门禁，以及 total + changed-surface coverage / refactor floor 校验。
  `./scripts/lint --full` extends the default checks with architecture/file-matrix validation, governance guards, the full test coverage gate, plus total + changed-surface coverage and refactor floor validation.
- To also audit dev dependencies locally (may be noisy), set `PIP_AUDIT_INCLUDE_DEV=1`; the dev audit checks the installed environment so security overrides are honored.
  如需在本地额外审计 dev 依赖（可能较吵），可设置 `PIP_AUDIT_INCLUDE_DEV=1`；dev 审计会检查已安装环境，以便安全覆盖版本生效。
- CI 的正式裁决仍以下面的显式 `uv run ...` 命令分组为准；`./scripts/lint` 只是维护者入口，不再暗示“默认已跑完整矩阵”。
  The canonical CI contract remains the explicit grouped `uv run ...` commands below; `./scripts/lint` is only a maintainer entrypoint and no longer implies the full matrix by default.

### Testing / 测试

Run tests with `uv` (same as CI):
使用 `uv` 运行测试（与 CI 一致）：

```bash
# Full test suite (same as CI)
uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing

# Snapshot coverage is already included above / snapshot 覆盖已包含在上面的命令中

# Prepare the changed coverage surface (same contract as CI) / 生成与 CI 一致的 changed coverage surface
git diff --name-only --diff-filter=AMRT "$(git merge-base origin/main HEAD)...HEAD" > .coverage-changed-files

# Total + changed-surface coverage gates (same as CI) / 总覆盖率 + changed-surface 覆盖率门禁（与 CI 一致）
uv run python scripts/coverage_diff.py coverage.json --minimum 95 --changed-files .coverage-changed-files --changed-minimum 95

# Quick local run (no coverage gate) / 本地快速跑（不含覆盖率门禁）
uv run pytest tests/

# Diagnostics focused tests (same target as pre-push hook)
uv run pytest -q -x tests/core/test_diagnostics_config_entry.py::TestAsyncGetConfigEntryDiagnostics::test_collects_and_redacts_diagnostics
uv run pytest -q -x tests/core/test_diagnostics_config_entry.py::TestAsyncGetConfigEntryDiagnostics::test_handles_no_devices
uv run pytest -q -x tests/core/test_diagnostics_config_entry.py::TestAsyncGetConfigEntryDiagnostics::test_diagnostics_snapshot

# Targeted protocol/auth/control public-surface regression / 定向 protocol/auth/control public-surface 回归
uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/test_auth.py tests/flows/test_flow_schemas.py tests/flows/test_config_flow_user.py tests/flows/test_config_flow_reauth.py tests/flows/test_config_flow_reconfigure.py tests/flows/test_options_flow.py tests/meta/test_public_surface_guards.py tests/core/test_coordinator_entry.py
```

Notes:
说明：

- Init / lifecycle / service-handler 改动建议优先跑 `tests/core/test_init*.py` 与 `tests/core/test_init_service_handlers*.py`，不要再把专题用例回灌到单一 mega-test 文件。
- Phase-history / governance closeout 改动建议补跑 `tests/meta/test_governance_phase_history*.py`，以保持 topicized closeout guards 与实际 phase 证据一致。

### CI Contract / CI 契约

Use the same command groups as GitHub Actions:
请与 GitHub Actions 使用同一组命令：

- **lint**: `uv run ruff check .`、`uv run ruff format --check .`、`uv run mypy`、`uv run python scripts/check_translations.py`；translation truth 属于 blocking lint lane，不再只是“改到文案时可选”
- **governance**: `uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q -x tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`
- **pre-push**: `uv run --extra dev python scripts/check_translations.py`、`uv run --extra dev python scripts/check_architecture_policy.py --check`、`uv run --extra dev python scripts/check_file_matrix.py --check`、`uv run --extra dev pytest -q -x tests/core/test_diagnostics_config_entry.py::TestAsyncGetConfigEntryDiagnostics::test_collects_and_redacts_diagnostics tests/core/test_diagnostics_config_entry.py::TestAsyncGetConfigEntryDiagnostics::test_handles_no_devices tests/core/test_diagnostics_config_entry.py::TestAsyncGetConfigEntryDiagnostics::test_diagnostics_snapshot`、`uv run --extra dev pytest -q -x tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`；pre-push 只保留 focused local mirrors，不再指向旧 diagnostics mega-file
- **test**: `uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing`、`uv run python scripts/coverage_diff.py coverage.json --minimum 95 --changed-files .coverage-changed-files --changed-minimum 95`（total coverage 与 changed measured files 都是 blocking gate；只有显式提供 `--baseline` 才额外比较 total diff）、`uv run python scripts/refactor_tools.py --coverage-json coverage.json --minimum-coverage 95`；snapshot coverage 已包含在 `tests/` 主阻塞 lane 中，不再单独重复执行；本地可直接用 `./scripts/lint --full` 自动解析 `.coverage-changed-files`
- **security**: GitHub Actions 会在每个 PR 上运行 blocking runtime `pip-audit` 门禁；tag release 还会额外运行 tagged release security gate，并要求 tagged `CodeQL` analysis 已完成且 open alerts 为零。dev dependency audit 仅在 `schedule` / `workflow_dispatch` 作为 advisory、non-blocking 运行；GitHub artifact attestation / provenance 仍不是 signing，请不要把 attestation / pip-audit 混写成 artifact signing。
- **benchmark**: `uv run pytest tests/benchmarks/ -v --benchmark-only --benchmark-json=.benchmarks/benchmark.json`、`uv run python scripts/check_benchmark_baseline.py .benchmarks/benchmark.json --manifest tests/benchmarks/benchmark_baselines.json`；benchmark lane 只在 `schedule` / `workflow_dispatch` 运行，不进入 PR blocking lane；threshold warning 只发维护者信号，failure threshold 才作为该 lane 的 no-regression gate
- **preview**: `schedule` / `workflow_dispatch` 专用 compatibility preview lane 会升级 Home Assistant preview dependency set，并在 `DeprecationWarning` / `PendingDeprecationWarning` 提升为错误的条件下运行定向 smoke；它只提供 maintainer-facing advisory signal，不会改变 stable PR / release / support contract
- **shellcheck**: 若修改 `install.sh` / `scripts/*` shell 脚本，请运行 `shellcheck install.sh scripts/develop scripts/lint scripts/setup`（CI 的 `lint` job 也会执行）
- **validate**: GitHub Actions 会额外运行 `HACS` 与 `Hassfest` 校验；若仓库或 fork 为 private，CI 会跳过 HACS validation，因为 HACS 只支持公开 GitHub 仓库；本地通常不必手动复刻，但提交前应确保仓库元数据仍符合这些约束
- **release**: tag release 先复用 `.github/workflows/ci.yml`，再由 `.github/workflows/release.yml` 在 `refs/tags/${RELEASE_TAG}` 上运行 tagged release security gate 与 tagged `CodeQL` gate，发布 `SHA256SUMS` / `SBOM` / GitHub artifact attestation / provenance / keyless `cosign` signature bundles，并写出 release identity manifest。attestation / provenance 是 release identity 证据，`cosign` bundle 才是 artifact signing；维护者操作手册见 `docs/MAINTAINER_RELEASE_RUNBOOK.md`。若本次属于 maintainer-only `break-glass verify-only` 或 `non-publish rehearsal`，必须显式记录为不发布资产的验证演练，不能旁路门禁直接发版

### Minimal Validation by Change Type / 按变更类型最小验证

Choose the smallest lane that still matches the changed surface; do not invent a shadow CI story.
请选择仍能覆盖改动面的最小验证路径，不要再造一套影子 CI 故事线。

- **docs-only**: `uv run pytest -q tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`
- **governance-only**: `uv run pytest -q tests/meta/test_governance_release_*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`
- **release-only**: `uv run pytest -q tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py`
- **maintainer-only verify-only / non-publish rehearsal**: trigger `.github/workflows/release.yml` via `workflow_dispatch` with `tag=<existing-tag>` and `publish_assets=false`; this validates the release path without publishing public assets

### Type Hints / 类型提示

Please use type hints for function parameters and return values:
请为函数参数和返回值使用类型提示：

```python
async def async_turn_on(self, **kwargs: Any) -> None:
    """Turn on the light."""
```

## Submitting Changes / 提交更改

### Pull Request Process / Pull Request 流程

1. **Create a feature branch / 创建功能分支**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes / 进行更改**
   - Write clear, concise commit messages
   - 编写清晰简洁的提交信息
   - Add tests for new functionality
   - 为新功能添加测试
   - Update documentation if needed
   - 如有需要更新文档

3. **Run linting and tests / 运行代码检查和测试**
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run mypy
   uv run python scripts/check_translations.py
   uv run python scripts/check_architecture_policy.py --check
   uv run python scripts/check_file_matrix.py --check
   uv run pytest -q -x tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance*.py tests/meta/test_toolchain_truth.py tests/meta/test_version_sync.py
   uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing
   git diff --name-only --diff-filter=AMRT "$(git merge-base origin/main HEAD)...HEAD" > .coverage-changed-files
   uv run python scripts/coverage_diff.py coverage.json --minimum 95 --changed-files .coverage-changed-files --changed-minimum 95  # total + changed-surface coverage; add --baseline only for optional total diff
   uv run python scripts/refactor_tools.py --coverage-json coverage.json --minimum-coverage 95

   # If shell scripts changed / 若改到 shell 脚本
   shellcheck install.sh scripts/develop scripts/lint scripts/setup
   ```

   For protocol/auth/control public-surface changes, prefer adding the targeted regression above before the full run; only run benchmarks when performance is part of the change.
   对于 protocol/auth/control public-surface 变更，建议先运行上面的定向回归再做全量；只有性能相关改动才需要跑 benchmark。

4. **Submit Pull Request / 提交 Pull Request**
   - Provide a clear description of the changes
   - 提供更改的清晰描述
   - Reference any related issues
   - 引用任何相关问题

### Commit Message Format / 提交信息格式

We follow [Conventional Commits](https://www.conventionalcommits.org/):
我们遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature / 新功能
- `fix`: Bug fix / 错误修复
- `docs`: Documentation only / 仅文档
- `style`: Code style (formatting) / 代码样式（格式化）
- `refactor`: Code refactoring / 代码重构
- `test`: Adding tests / 添加测试
- `chore`: Maintenance / 维护

Example:
```
feat(light): add support for color temperature

Add support for adjusting color temperature on Lipro lights
that support this feature.

Closes #123
```

## Reporting Issues / 报告问题

### Bug Reports / 错误报告

When reporting bugs, please include:
报告错误时，请包括：

- Integration version / 集成版本
- Home Assistant version / Home Assistant 版本（最低支持 `2026.3.1`）
- Steps to reproduce / 复现步骤
- Expected vs actual behavior / 预期与实际行为
- Relevant logs (with debug logging enabled) / 相关日志（启用调试日志）

### Security Reports / 安全问题报告

Do not open a public issue for vulnerabilities.
安全漏洞不要走公开 Issue。

- Follow `SECURITY.md` and use the GitHub private vulnerability reporting path first.
  请先遵循 `SECURITY.md`；只有当你当前访问模式可见时，才优先使用 GitHub 私密漏洞披露流程。
- Only open a public issue after maintainers confirm the fix is ready to disclose.
  仅在维护者确认可以公开后，再开启公开问题。

### Feature Requests / 功能请求

When requesting features:
请求功能时：

- Describe the use case / 描述使用场景
- Explain why it would be useful / 解释为什么它有用
- Consider if it fits the project's scope / 考虑它是否符合项目范围

## Code of Conduct / 行为准则

Please follow `CODE_OF_CONDUCT.md` for community expectations.
请遵循 `CODE_OF_CONDUCT.md` 中的社区行为约定。

## Support / 支持渠道

See `docs/TROUBLESHOOTING.md` first, then `SUPPORT.md` for usage questions, bug triage expectations, support lifecycle, and security routing.
如需排障请先看 `docs/TROUBLESHOOTING.md`，再通过 `SUPPORT.md` 获取使用问题、缺陷分流与安全披露路径。

## Questions? / 有问题？

Start with `docs/README.md` and `SUPPORT.md`. If your current access mode exposes GitHub Discussions (or a future public mirror preserves that route), use Discussions for early design discussion; use Issues for confirmed, trackable work when that route is actually reachable.
请先从 `docs/README.md` 与 `SUPPORT.md` 开始。若你当前访问模式可见 GitHub Discussions（或未来 public mirror 保留该入口），可用它讨论早期设计；只有当 Issue 路径真实可达时，才用它承载已确认、可追踪的工作。

---

Thank you for contributing! 🎉
感谢您的贡献！🎉
