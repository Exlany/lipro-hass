# lipro-hass AGENTS.md

本文件是 `lipro-hass` 仓库级执行约束，适用于整个仓库。

## 1. 先读这些

1. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
2. `docs/developer_architecture.md`
3. `README.md` / `README_zh.md`
4. `CONTRIBUTING.md`
5. `docs/CONTRIBUTOR_ARCHITECTURE_CHANGE_MAP.md`
6. `docs/adr/README.md`

若文档之间冲突，优先级按上面的顺序处理。

## 2. 项目定位

`lipro-hass` 是 Home Assistant 的 `Lipro` 集成。

核心目标只有三个：

- 保持单一正式架构主链
- 保持用户文档可直接使用
- 保持自动化校验可以解释并复现

## 3. 架构硬约束

- `LiproProtocolFacade` 是唯一正式 protocol root。
- `Coordinator` 是唯一正式 runtime orchestration root。
- `custom_components/lipro/control/` 是正式 control plane home。
- 根层 `__init__.py`、`config_flow.py`、`diagnostics.py`、`system_health.py` 只做 thin adapter。
- 不要恢复 `LiproClient`、`LiproMqttClient`、`raw_client` 等历史 compat 名称。
- 不要让 entity / platform / control 直接依赖 protocol internals 或 runtime 私有状态。

## 4. 已关闭残留

- `custom_components/lipro/services/execution.py` 仍是正式 service execution facade。
- `Phase 5 已关闭 coordinator 私有 auth seam`。
- 不要再把它描述为 active seam，也不要重新引入旁路 auth/runtime 访问路径。

## 5. 修改偏好

- 优先小范围改动，先修根因。
- 复用现有正式组件，不新增第二条故事线。
- 用户可见文档优先说清楚安装、配置、排障，不要把内部治理叙事塞进 README。
- 变更 README 时，保持 `README.md` 与 `README_zh.md` 信息等价。

## 6. 命令约束

- Python 命令统一使用 `uv run ...`
- 优先运行与改动面匹配的最小充分测试
- 常用校验：
  - `uv run ruff check .`
  - `uv run ruff format --check .`
  - `uv run pytest -q`
  - `uv run python scripts/check_markdown_links.py`
  - `uv run python scripts/check_translations.py`

## 7. 发布与 Tag 约束

- 每次创建或移动版本 tag 前，必须先更新 `CHANGELOG.md`，并确保目标 tag 对应提交包含该 changelog 变更。
- 打 tag 前必须确认项目版本文件与 tag 一致，至少检查 `pyproject.toml`、`custom_components/lipro/manifest.json` 与 `uv.lock`。
- 打 tag 前优先运行与发布改动匹配的最小充分校验；文档变更至少运行 `uv run python scripts/check_markdown_links.py`。

## 8. 禁止事项

- 不要提交敏感信息、调试垃圾或临时文件。
- 不要把本地 scratch / governance 目录重新纳入发布树。
- 不要用历史兼容层重新定义正式 public surface。
