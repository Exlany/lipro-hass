# Technology Stack

**Analysis Date:** 2026-03-27

> Snapshot: `2026-03-27`
> Freshness: 基于 `pyproject.toml`、`uv.lock`、`custom_components/lipro/manifest.json`、`hacs.json`、`.devcontainer.json`、`.pre-commit-config.yaml`、`scripts/{setup,develop,lint}`、`.github/workflows/{ci,release,codeql}.yml`、`custom_components/lipro/**`、`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`docs/developer_architecture.md`、`.planning/baseline/{DEPENDENCY_MATRIX.md,AUTHORITY_MATRIX.md,VERIFICATION_MATRIX.md}` 与 `.planning/reviews/{RESIDUAL_LEDGER.md,KILL_LIST.md}` 的当前截面。
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、审阅与后续实现对齐。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md}`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本文件不得反向充当当前治理真源。

## Languages

**Primary:**
- Python 3.14 / `>=3.14.2` - 生产代码位于 `custom_components/lipro/**/*.py`，测试位于 `tests/**/*.py`，治理与工具脚本位于 `scripts/*.py`。

**Secondary:**
- Bash - `install.sh`、`scripts/setup`、`scripts/develop`、`scripts/lint`。
- YAML - `.github/workflows/*.yml`、`custom_components/lipro/services.yaml`、`custom_components/lipro/quality_scale.yaml`、`blueprints/automation/lipro/*.yaml`、`.github/ISSUE_TEMPLATE/*.yml`。
- JSON - `custom_components/lipro/manifest.json`、`hacs.json`、`custom_components/lipro/translations/*.json`、`custom_components/lipro/icons.json`、`custom_components/lipro/firmware_support_manifest.json`、`tests/fixtures/**/*.json`。
- Markdown - `README.md`、`README_zh.md`、`CONTRIBUTING.md`、`SUPPORT.md`、`SECURITY.md`、`docs/**/*.md`、`.planning/**/*.md`。

**Not detected:**
- 根目录未检测到 `package.json`、`go.mod`、`Cargo.toml`、`requirements.txt`、`poetry.lock` 或 `Dockerfile`。

## Runtime

**Environment:**
- Home Assistant 自定义集成运行于 `custom_components/lipro/__init__.py`，平台适配分布在 `custom_components/lipro/{light,cover,switch,fan,climate,binary_sensor,sensor,select,update}.py`。
- 最低 Home Assistant 版本为 `2026.3.1`，由 `pyproject.toml`、`hacs.json`、`README.md`、`README_zh.md` 与 `tests/meta/test_version_sync.py` 同步约束。
- Python floor 为 `>=3.14.2`，声明于 `pyproject.toml`；开发与 CI 统一使用 Python `3.14`，见 `.devcontainer.json`、`.pre-commit-config.yaml`、`.github/workflows/{ci,release,codeql}.yml`。
- 所有网络 I/O 通过 Home Assistant 注入的 `aiohttp` session 完成，入口见 `custom_components/lipro/__init__.py`、`custom_components/lipro/config_flow.py`、`custom_components/lipro/firmware_manifest.py`。

**Package Manager:**
- `uv` - 本地安装由 `scripts/setup` 驱动，本地检查由 `scripts/lint` 驱动，本地开发启动由 `scripts/develop` 驱动，CI 依赖安装由 `.github/workflows/{ci,release,codeql}.yml` 驱动。
- Lockfile: present (`uv.lock`)。
- Build backend: `setuptools.build_meta`，定义于 `pyproject.toml`。

## Frameworks

**Core:**
- Home Assistant custom integration - 元数据位于 `custom_components/lipro/manifest.json`，服务声明位于 `custom_components/lipro/services.yaml`，质量分级位于 `custom_components/lipro/quality_scale.yaml`。
- 北极星分层架构 - 裁决文档位于 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 与 `docs/developer_architecture.md`；协议根位于 `custom_components/lipro/core/protocol/facade.py`，REST stable import home 位于 `custom_components/lipro/core/api/client.py`，REST child façade 位于 `custom_components/lipro/core/api/rest_facade.py`，MQTT child façade 位于 `custom_components/lipro/core/protocol/mqtt_facade.py`，运行根位于 `custom_components/lipro/core/coordinator/`，控制面位于 `custom_components/lipro/control/`。

**Testing:**
- `pytest==9.0.0`、`pytest-asyncio==1.3.0`、`pytest-cov==7.0.0`、`pytest-homeassistant-custom-component==0.13.317`、`pytest-benchmark==5.2.3`、`syrupy==5.0.0`，版本锁定于 `uv.lock`。
- 测试与守卫按职责分布在 `tests/core/`、`tests/integration/`、`tests/flows/`、`tests/platforms/`、`tests/services/`、`tests/meta/`、`tests/benchmarks/`。

**Build/Dev:**
- `ruff==0.15.4` 与 `mypy==1.19.1` 在 `pyproject.toml` 中配置，在 `.pre-commit-config.yaml` 中接入本地门禁。
- `pre-commit==4.5.1` 由 `scripts/setup` 安装本地 `pre-commit` / `pre-push` hooks。
- `pip-audit==2.10.0`、`CodeQL` 与 `shellcheck` 分别在 `.github/workflows/{ci,release,codeql}.yml` 中承担安全与脚本质量门禁。
- `.github/dependabot.yml` 每日更新 `devcontainers`、`github-actions` 与 `pip` 依赖。

## Key Dependencies

**Critical:**
- `aiohttp==3.13.3` - REST 传输、固件 advisory 拉取与匿名分享上传，代码位于 `custom_components/lipro/core/api/transport_*.py`、`custom_components/lipro/firmware_manifest.py`、`custom_components/lipro/core/anonymous_share/*.py`。
- `aiomqtt==2.5.0` - MQTT push 传输，代码位于 `custom_components/lipro/core/mqtt/transport.py` 与 `custom_components/lipro/core/protocol/mqtt_facade.py`。
- `pycryptodome==3.23.0` - 供应商 AES/HMAC/MD5 相关逻辑，代码位于 `custom_components/lipro/core/mqtt/credentials.py` 与 `custom_components/lipro/core/utils/vendor_crypto.py`。
- `voluptuous==0.15.2` - config flow 与服务参数校验，代码位于 `custom_components/lipro/flow/*.py` 与 `custom_components/lipro/services/contracts.py`。

**Infrastructure:**
- `homeassistant==2026.3.1` - 仅作为开发/测试宿主依赖，声明于 `pyproject.toml` 与 `uv.lock`。
- `colorlog==6.10.1`、`aiodns==4.0.0`、`pycares==5.0.1` - 由 `uv.lock` 锁定的运行/开发支持依赖。
- `manifest.json` 仅声明 `aiomqtt` 与 `pycryptodome`；`aiohttp` 与 `voluptuous` 由 Home Assistant 运行时提供，这一分工由 `tests/meta/test_version_sync.py` 守卫。

## Configuration

**Environment:**
- 仓库中未检测到 `.env*` 文件。
- 运行时凭证不是 env 驱动，而是通过 `custom_components/lipro/config_flow.py` 与 `custom_components/lipro/entry_auth.py` 写入 Home Assistant config entry。
- 本地开发环境变量为 `LIPRO_DEVELOP_CONFIG_DIR` 与 `LIPRO_DEVELOP_SMOKE_ONLY`，定义于 `scripts/develop`。
- 本地安全审计环境变量为 `PIP_AUDIT_INCLUDE_DEV`，定义于 `scripts/lint`。
- 安装脚本环境变量为 `ARCHIVE_TAG`、`ARCHIVE_FILE`、`LIPRO_ALLOW_MIRROR`、`LIPRO_ALLOW_BRANCH_FALLBACK`、`LIPRO_INSTALL_MAX_FILES`、`LIPRO_INSTALL_MAX_UNCOMPRESSED_BYTES`、`LIPRO_INSTALL_MAX_SINGLE_FILE_BYTES`，定义于 `install.sh`。

**Build:**
- 打包与工具链真源位于 `pyproject.toml`、`custom_components/lipro/manifest.json`、`hacs.json`、`.devcontainer.json` 与 `.pre-commit-config.yaml`。
- 本地入口脚本为 `scripts/setup`、`scripts/develop`、`scripts/lint`。
- CI / release / security 入口位于 `.github/workflows/{ci,release,codeql}.yml` 与 `.github/dependabot.yml`。

## Platform Requirements

**Development:**
- 需要 Python 3.14 与 `uv`；约束分别见 `.devcontainer.json`、`pyproject.toml`、`scripts/setup` 与 `.github/workflows/*.yml`。
- `shellcheck` 不是运行时必需，但在 `.github/workflows/ci.yml` 与 `scripts/lint` 的完整检查路径中会被调用。
- 本地 Home Assistant 烟测通过 `scripts/develop` 中的 `uv run hass -c .` 启动。

**Production:**
- 部署目标是用户的 Home Assistant 配置目录中的 `custom_components/lipro/`。
- 稳定安装路径是经校验的 GitHub release 资产或本地归档配合 `install.sh --archive-file`；`install.sh`、`README.md` 与 `README_zh.md` 都明确将 `ARCHIVE_TAG=main`、branch fallback 与 mirror 安装标记为 preview / unsupported 路径。

## Risks & Recommendations

**Version Floor:**
- 风险：`pyproject.toml` 要求 Python `>=3.14.2`，`hacs.json` 要求 Home Assistant `2026.3.1`，版本门槛较高，任何升级都需要多处同步。
- 建议：以 `tests/meta/test_version_sync.py` 作为合并前必跑门禁，避免 `pyproject.toml`、`hacs.json`、`README*` 与 workflow 配置失配。

**Toolchain Reproducibility:**
- 风险：依赖图由 `uv.lock` 固定，但仓库内没有显式固定 `uv` CLI 版本；一旦本地与 CI 的 `uv` 行为漂移，可能影响锁文件解析与导出结果。
- 建议：若出现漂移，优先在 `CONTRIBUTING.md` 或 workflow 中补充期望的 `uv` 最低版本说明，而不是引入第二套安装方式。

**Packaging Split:**
- 风险：`pyproject.toml` 与 `custom_components/lipro/manifest.json` 对运行时依赖的分工是刻意设计，但新增依赖时容易误放位置。
- 建议：新增依赖前先判断它是 Home Assistant 提供还是集成自带，并同步更新 `tests/meta/test_version_sync.py` 或相邻元测试。

**Preview Install Surface:**
- 风险：`install.sh` 保留 branch / mirror 预览路径，便于调试，但也容易被误用为生产安装路径。
- 建议：继续把 `.github/workflows/release.yml` 生成的校验资产作为唯一稳定分发故事线，不再增加旁路安装器或未签名下载路径。

---

*Stack analysis: 2026-03-27*
