# Technology Stack
> Snapshot: `2026-03-19`
> Freshness: 基于 `AGENTS.md`、`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{PROJECT,STATE,ROADMAP,REQUIREMENTS}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md`、`docs/developer_architecture.md`、`pyproject.toml`、`.github/workflows/*.yml`、`custom_components/lipro/**` 与 `tests/meta/*.py` 的当前截面成立。真源变更后，本图谱必须同步刷新或标记过时。
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、审阅与后续实现对齐。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本图谱不得反向充当当前治理真源，且必须同步回写、标记为过时，或注明历史观察。

**Analysis Date:** 2026-03-19

> Freshness: 基于 `AGENTS.md`、`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{PROJECT,STATE,ROADMAP,REQUIREMENTS}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md`、`docs/developer_architecture.md`、`pyproject.toml`、`.github/workflows/*.yml`、`custom_components/lipro/**` 与 `tests/meta/*.py` 的当前截面。
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、审阅与后续实现对齐。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准。

## Languages

**Primary:**
- Python 3.14 - 运行时代码位于 `custom_components/lipro/**/*.py`，测试位于 `tests/**/*.py`，治理与工具脚本位于 `scripts/*.py`。

**Secondary:**
- Bash - `install.sh`、`scripts/setup`、`scripts/develop`、`scripts/lint`。
- YAML - `.github/workflows/*.yml`、`custom_components/lipro/services.yaml`、`custom_components/lipro/quality_scale.yaml`、`blueprints/automation/lipro/*.yaml`、`.github/ISSUE_TEMPLATE/*.yml`。
- JSON - `custom_components/lipro/manifest.json`、`hacs.json`、`custom_components/lipro/translations/*.json`、`custom_components/lipro/icons.json`、`custom_components/lipro/firmware_support_manifest.json`、`tests/fixtures/**/*.json`。
- Markdown - `README.md`、`README_zh.md`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`docs/**/*.md`、`.planning/**/*.md`。

## Runtime

**Environment:**
- Home Assistant 自定义集成运行时，根入口在 `custom_components/lipro/__init__.py`，平台适配位于 `custom_components/lipro/{light,cover,switch,fan,climate,binary_sensor,sensor,select,update}.py`。
- 最低 Home Assistant 版本为 `2026.3.1`，在 `pyproject.toml`、`hacs.json`、`README.md`、`README_zh.md` 与 `tests/meta/test_toolchain_truth.py` 中保持同步。
- Python 要求为 `>=3.14.2`，声明于 `pyproject.toml`；本地开发与 CI 使用 Python 3.14，见 `.devcontainer.json`、`.github/workflows/ci.yml`、`.github/workflows/release.yml`、`.github/workflows/codeql.yml`。
- `aiohttp` session 通过 `homeassistant.helpers.aiohttp_client.async_get_clientsession` 注入，见 `custom_components/lipro/__init__.py`、`custom_components/lipro/config_flow.py`、`custom_components/lipro/firmware_manifest.py`。

**Package Manager:**
- `uv` - 由 `uv.lock`、`scripts/setup`、`scripts/lint`、`.github/workflows/ci.yml` 驱动。
- Lockfile: present (`uv.lock`)。

## Frameworks

**Core:**
- Home Assistant custom integration - 入口与元数据位于 `custom_components/lipro/manifest.json`、`custom_components/lipro/__init__.py`、`custom_components/lipro/config_flow.py`、`custom_components/lipro/diagnostics.py`、`custom_components/lipro/system_health.py`。
- 显式分层架构 - 北极星与开发者架构见 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`docs/developer_architecture.md`；协议根在 `custom_components/lipro/core/protocol/facade.py`，REST 子门面在 `custom_components/lipro/core/api/client.py`，MQTT 子门面在 `custom_components/lipro/core/protocol/mqtt_facade.py`，运行根在 `custom_components/lipro/core/coordinator/coordinator.py`。
- HA 生态元数据 - `integration_type: hub` 与 `iot_class: cloud_push` 在 `custom_components/lipro/manifest.json`；质量映射在 `custom_components/lipro/quality_scale.yaml`。

**Testing:**
- `pytest 9.0.0`、`pytest-asyncio 1.3.0`、`pytest-cov 7.0.0`、`pytest-homeassistant-custom-component 0.13.317`、`pytest-benchmark 5.2.3`、`syrupy 5.0.0` - 版本锁定见 `uv.lock`，声明见 `pyproject.toml`。
- 测试资产覆盖单元、集成、快照、协议回放、治理守卫，入口位于 `tests/core/`、`tests/integration/`、`tests/snapshots/`、`tests/meta/`。

**Build/Dev:**
- `setuptools.build_meta` - 构建后端在 `pyproject.toml`。
- `ruff 0.15.4` 与 `mypy 1.19.1` - 规则与严格类型检查在 `pyproject.toml` 与 `.pre-commit-config.yaml`。
- `pre-commit` - 本地提交前门禁在 `.pre-commit-config.yaml`。
- GitHub Actions - CI 与发布在 `.github/workflows/ci.yml`、`.github/workflows/release.yml`、`.github/workflows/codeql.yml`。
- HACS / Hassfest - 验证路径在 `.github/workflows/ci.yml` 与 `hacs.json`。

## Key Dependencies

**Critical:**
- `aiohttp 3.13.3` - 运行时 REST 传输、固件 advisory 拉取、匿名分享上传；代码位于 `custom_components/lipro/core/api/`、`custom_components/lipro/firmware_manifest.py`、`custom_components/lipro/core/anonymous_share/share_client.py`。
- `aiomqtt 2.5.0` - 实时 MQTT 传输；代码位于 `custom_components/lipro/core/mqtt/*.py`，运行桥接位于 `custom_components/lipro/core/protocol/mqtt_facade.py`。
- `pycryptodome 3.23.0` - MQTT 密钥 AES 解密；代码位于 `custom_components/lipro/core/mqtt/credentials.py`。
- `voluptuous 0.15.2` - Config Flow 与服务 schema 校验；代码位于 `custom_components/lipro/config_flow.py`、`custom_components/lipro/flow/schemas.py`、`custom_components/lipro/services/contracts.py`。
- `homeassistant 2026.3.1` - 本地开发/测试兼容基线；声明位于 `pyproject.toml`，同步守卫位于 `tests/meta/test_toolchain_truth.py`。

**Infrastructure:**
- `pip-audit 2.10.0` - runtime 依赖安全门禁；入口见 `scripts/lint`、`.github/workflows/ci.yml`、`.github/workflows/release.yml`。
- `colorlog 6.10.1` - 开发环境日志美化；版本锁定见 `uv.lock`。
- `aiodns 4.0.0` 与 `pycares 5.0.1` - 开发/测试环境的异步 DNS 支持；声明位于 `pyproject.toml`。
- `orjson 3.11.6`、`pyjwt 2.12.0`、`pillow 12.1.1` - 通过 `tool.uv.override-dependencies` 固化的开发解析覆盖项，见 `pyproject.toml`。

## Configuration

**Environment:**
- 运行时凭证由 Home Assistant config entry 持有，入口位于 `custom_components/lipro/config_flow.py`、`custom_components/lipro/entry_auth.py`、`custom_components/lipro/const/config.py`；仓库根目录未检测到运行时 `.env` 文件。
- 用户选项位于 `custom_components/lipro/flow/options_flow.py` 与 `custom_components/lipro/const/config.py`，包括 `scan_interval`、`mqtt_enabled`、`debug_mode`、`request_timeout`、功率监控、命令确认、房间同步与设备过滤等。
- 服务契约位于 `custom_components/lipro/services.yaml`、`custom_components/lipro/services/contracts.py`、`custom_components/lipro/translations/en.json`、`custom_components/lipro/translations/zh-Hans.json`。
- 文档入口覆盖用户、开发者、支持与发布路径，位于 `README.md`、`README_zh.md`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`docs/TROUBLESHOOTING.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`docs/developer_architecture.md`、`docs/adr/*.md`。

**Build:**
- 打包与版本真源位于 `pyproject.toml`、`custom_components/lipro/manifest.json`、`hacs.json`。
- 本地 DX 入口位于 `scripts/setup`、`scripts/develop`、`scripts/lint`、`.devcontainer.json`。
- 质量门禁位于 `.pre-commit-config.yaml`、`.github/workflows/ci.yml`、`.github/workflows/release.yml`、`.github/workflows/codeql.yml`。
- 架构与治理守卫位于 `scripts/check_architecture_policy.py`、`scripts/check_file_matrix.py`、`tests/meta/test_dependency_guards.py`、`tests/meta/test_public_surface_guards.py`、`tests/meta/test_toolchain_truth.py`。

## Platform Requirements

**Development:**
- 使用 `uv sync --frozen --extra dev` 建立环境，入口位于 `scripts/setup` 与 `.github/workflows/ci.yml`。
- Python 3.14 开发环境来自 `.devcontainer.json` 与 GitHub Actions。
- Home Assistant 2026.3.1 开发依赖来自 `pyproject.toml`。
- 可选 shell 工具 `shellcheck` 在 `.github/workflows/ci.yml` 的 `lint` job 中执行，覆盖 `install.sh` 与 `scripts/*`。

**Production:**
- 目标宿主为用户自己的 Home Assistant，运行载荷位于 `custom_components/lipro/`。
- 支持的交付路径为 HACS（`hacs.json`）、GitHub Release 资产（`.github/workflows/release.yml` 与 `install.sh`）、以及 `README.md` / `README_zh.md` 描述的手工复制。
- HA 生态对齐体现在 `custom_components/lipro/config_flow.py`、`custom_components/lipro/diagnostics.py`、`custom_components/lipro/system_health.py`、`custom_components/lipro/quality_scale.yaml` 与 `.github/workflows/ci.yml` 的 HACS / Hassfest 校验。

---

*Stack analysis: 2026-03-19*
