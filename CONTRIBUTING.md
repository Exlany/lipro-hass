# Contributing to Lipro Smart Home Integration / 贡献给 Lipro 智能家居集成

Thank you for your interest in contributing to the Lipro Smart Home integration!
感谢您有兴趣为 Lipro 智能家居集成做出贡献！

## Development Setup / 开发环境设置

### Prerequisites / 前置条件

- Python 3.13.2+
- Git

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

3. **Start Home Assistant for development / 启动 Home Assistant 进行开发**
   ```bash
   ./scripts/develop
   ```

   Access Home Assistant at http://localhost:8123
   在 http://localhost:8123 访问 Home Assistant

## Code Standards / 代码规范

### Linting and Formatting / 代码检查和格式化

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:
我们使用 [Ruff](https://docs.astral.sh/ruff/) 进行代码检查和格式化：

```bash
# Run linting / 运行代码检查
./scripts/lint

# Auto-fix issues / 自动修复问题
uv run ruff check custom_components/lipro tests --fix

# Format code / 格式化代码
uv run ruff format custom_components/lipro tests

# Type checking / 类型检查
uv run mypy custom_components/lipro
```

### Testing / 测试

Run tests with `uv` (same as CI):
使用 `uv` 运行测试（与 CI 一致）：

```bash
# Full test suite
uv run pytest tests/

# Diagnostics focused tests (used by pre-push hook)
uv run pytest tests/test_diagnostics.py::TestAsyncGetConfigEntryDiagnostics::test_collects_and_redacts_diagnostics
uv run pytest tests/test_diagnostics.py::TestAsyncGetConfigEntryDiagnostics::test_handles_no_devices
uv run pytest tests/test_diagnostics.py::TestAsyncGetConfigEntryDiagnostics::test_diagnostics_snapshot
```

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
   ./scripts/lint
   uv run mypy custom_components/lipro
   uv run pytest tests/
   ```

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
- Home Assistant version / Home Assistant 版本
- Steps to reproduce / 复现步骤
- Expected vs actual behavior / 预期与实际行为
- Relevant logs (with debug logging enabled) / 相关日志（启用调试日志）

### Feature Requests / 功能请求

When requesting features:
请求功能时：

- Describe the use case / 描述使用场景
- Explain why it would be useful / 解释为什么它有用
- Consider if it fits the project's scope / 考虑它是否符合项目范围

## Code of Conduct / 行为准则

- Be respectful and constructive / 保持尊重和建设性
- Focus on what's best for the community / 专注于对社区最有利的事情
- Accept constructive criticism gracefully / 优雅地接受建设性批评

## Questions? / 有问题？

Feel free to open an issue for discussion!
欢迎开启 Issue 进行讨论！

---

Thank you for contributing! 🎉
感谢您的贡献！🎉
