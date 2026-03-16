# Contributing to Lipro Smart Home Integration / 贡献给 Lipro 智能家居集成

Thank you for your interest in contributing to the Lipro Smart Home integration!
感谢您有兴趣为 Lipro 智能家居集成做出贡献！

## Development Setup / 开发环境设置

### Prerequisites / 前置条件

- Python 3.14.2+
- uv (Astral)
- Git

### Version Truth / 版本真源

- Canonical minimum supported Home Assistant version: `2026.3.1` from `pyproject.toml` (`homeassistant==2026.3.1`).
- Canonical Python toolchain truth: Python `3.14` (`requires-python`, `mypy`, `ruff`, `pre-commit`, devcontainer, and CI all align here).
- 唯一 Python 工具链真相：Python `3.14`（`requires-python`、`mypy`、`ruff`、`pre-commit`、devcontainer 与 CI 全部对齐到这里）。
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

## Documentation & Maintainer Entry Points / 文档与维护入口

- Public entry docs: `README.md`, `README_zh.md`, `CONTRIBUTING.md`
- User / contributor troubleshooting: `docs/TROUBLESHOOTING.md`
- Maintainer release flow: `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- Support routing and response expectations: `SUPPORT.md`
- Private vulnerability disclosure: `SECURITY.md`
- If you touch `README.md` / `README_zh.md` / `CONTRIBUTING.md` / `SUPPORT.md` / `SECURITY.md` / `.github/*` / release workflow, update these entry points together and do not leave silent defer behind.
- Public bug reports should start with diagnostics; developer report / one-click feedback is an escalation path only when diagnostics are insufficient or a maintainer explicitly asks for deeper debugging.

## Code Standards / 代码规范

### Linting and Formatting / 代码检查和格式化

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:
我们使用 [Ruff](https://docs.astral.sh/ruff/) 进行代码检查和格式化：

```bash
# Run linting / 运行代码检查
./scripts/lint

# Auto-fix issues / 自动修复问题
uv run ruff check . --fix

# Format code / 格式化代码
uv run ruff format .

# Type checking / 类型检查
uv run mypy
```

Notes:
说明：

- `./scripts/lint` runs `pip-audit` against exported runtime requirements by default.
  `./scripts/lint` 默认仅对导出的 runtime 依赖运行 `pip-audit`。
- `./scripts/lint` 是本地便捷包装；CI 的正式裁决仍以下面的显式 `uv run ...` 命令为准。
  `./scripts/lint` is a local convenience wrapper; the canonical CI contract remains the explicit `uv run ...` commands below.
- To also audit dev dependencies locally (may be noisy), set `PIP_AUDIT_INCLUDE_DEV=1`; the dev audit checks the installed environment so security overrides are honored.
  如需在本地额外审计 dev 依赖（可能较吵），可设置 `PIP_AUDIT_INCLUDE_DEV=1`；dev 审计会检查已安装环境，以便安全覆盖版本生效。

### Testing / 测试

Run tests with `uv` (same as CI):
使用 `uv` 运行测试（与 CI 一致）：

```bash
# Full test suite (same as CI)
uv run pytest tests/ -v --cov=custom_components/lipro --cov-fail-under=95 --cov-report=xml --cov-report=term-missing

# Quick local run (no coverage gate) / 本地快速跑（不含覆盖率门禁）
uv run pytest tests/

# Diagnostics focused tests (used by pre-push hook)
uv run pytest tests/core/test_diagnostics.py::TestAsyncGetConfigEntryDiagnostics::test_collects_and_redacts_diagnostics
uv run pytest tests/core/test_diagnostics.py::TestAsyncGetConfigEntryDiagnostics::test_handles_no_devices
uv run pytest tests/core/test_diagnostics.py::TestAsyncGetConfigEntryDiagnostics::test_diagnostics_snapshot

# Targeted protocol/auth/control public-surface regression / 定向 protocol/auth/control public-surface 回归
uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/test_auth.py tests/flows/test_config_flow.py tests/meta/test_public_surface_guards.py tests/test_coordinator_public.py
```

### CI Contract / CI 契约

Use the same command groups as GitHub Actions:
请与 GitHub Actions 使用同一组命令：

- **lint**: `uv run ruff check .`、`uv run ruff format --check .`、`uv run mypy`；若涉及用户可见文案，再跑 `uv run python scripts/check_translations.py`
- **governance**: `uv run python scripts/check_architecture_policy.py --check`、`uv run python scripts/check_file_matrix.py --check`、`uv run pytest -q -x tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py`
- **test**: `uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing`、`uv run pytest tests/snapshots/ -v`、`uv run python scripts/coverage_diff.py coverage.json --minimum 95`（coverage floor + optional baseline diff）、`uv run python scripts/refactor_tools.py --coverage-json coverage.json --minimum-coverage 95`
- **security**: GitHub Actions 会在每个 PR 上运行 runtime `pip-audit` 门禁；dev dependency audit 仅在 `schedule` / `workflow_dispatch` 作为 advisory、non-blocking 运行；若变更涉及依赖、认证、发布链路或安全边界，提交前至少复核 `./scripts/lint` 或手动执行 runtime `pip-audit` 流程
- **benchmark**: `uv run pytest tests/benchmarks/ -v --benchmark-only --benchmark-json=.benchmarks/benchmark.json`；当前是 advisory observability lane，仅在性能敏感改动或手动对齐 `schedule` / `workflow_dispatch` 时需要
- **shellcheck**: 若修改 `install.sh` / `scripts/*` shell 脚本，请运行 `shellcheck install.sh scripts/develop scripts/lint scripts/setup`（CI 的 `lint` job 也会执行）
- **validate**: GitHub Actions 会额外运行 `HACS` 与 `Hassfest` 校验；若仓库或 fork 为 private，CI 会跳过 HACS validation，因为 HACS 只支持公开 GitHub 仓库；本地通常不必手动复刻，但提交前应确保仓库元数据仍符合这些约束
- **release**: tag release 先复用 `.github/workflows/ci.yml`，再由 `.github/workflows/release.yml` 从 `refs/tags/${RELEASE_TAG}` 打包并发布资产；维护者操作手册见 `docs/MAINTAINER_RELEASE_RUNBOOK.md`，不要旁路门禁直接发版

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
   uv run python scripts/check_architecture_policy.py --check
   uv run python scripts/check_file_matrix.py --check
   uv run pytest -q -x tests/meta/test_dependency_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_governance_guards.py tests/meta/test_version_sync.py
   uv run pytest tests/ -v --ignore=tests/benchmarks --cov=custom_components/lipro --cov-fail-under=95 --cov-report=json --cov-report=xml --cov-report=term-missing
   uv run pytest tests/snapshots/ -v
   uv run python scripts/coverage_diff.py coverage.json --minimum 95  # coverage floor + optional baseline diff
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
  请先遵循 `SECURITY.md`，使用 GitHub 私密漏洞披露流程。
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

See `docs/TROUBLESHOOTING.md` first, then `SUPPORT.md` for usage questions, bug triage expectations, and security routing.
如需排障请先看 `docs/TROUBLESHOOTING.md`，再通过 `SUPPORT.md` 获取使用问题、缺陷分流与安全披露路径。

## Questions? / 有问题？

Feel free to open a GitHub Discussion for questions or early design discussion; use Issues for confirmed bugs and trackable work!
欢迎先通过 GitHub Discussions 提问或讨论设计；确认缺陷与可追踪工作再开 Issue！

---

Thank you for contributing! 🎉
感谢您的贡献！🎉
