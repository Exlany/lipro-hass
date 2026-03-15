# Stack Map
> Snapshot: `2026-03-15`; governance truth says `v1.1` phases `7.1-15` complete and `Phase 16` is the active post-audit closeout line. This refresh follows `AGENTS.md`, `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `.planning/PROJECT.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/baseline/*.md`, `.planning/reviews/*.md`, `pyproject.toml`, `.github/workflows/*`, `custom_components/lipro/manifest.json`, plus related docs/scripts/assets.
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、协作与局部审阅。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本图谱必须同步回写或标记为过时。

## Product Shape
- Primary deliverable is a Home Assistant custom integration rooted at `custom_components/lipro/`.
- Python package metadata lives in `pyproject.toml`; HA runtime metadata lives in `custom_components/lipro/manifest.json`; HACS metadata lives in `hacs.json`.
- Release artifacts are versioned zips built from `custom_components/lipro/` by `.github/workflows/release.yml`.
- Architecture/governance truth is anchored by `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`, `.planning/baseline/*.md`, and `.planning/reviews/*.md`.

## Languages And Asset Types
| Kind | Paths | Current role |
| --- | --- | --- |
| Python `3.14` | `custom_components/lipro/**/*.py`, `tests/**/*.py`, `scripts/*.py` | HA runtime, protocol/MQTT/telemetry, QA and governance tooling |
| Bash | `install.sh`, `scripts/setup`, `scripts/develop`, `scripts/lint` | install/update, local DX, lint wrapper |
| YAML | `.github/workflows/*.yml`, `custom_components/lipro/services.yaml`, `custom_components/lipro/quality_scale.yaml`, `blueprints/automation/lipro/*.yaml`, `.github/ISSUE_TEMPLATE/*.yml` | CI/CD, HA services, quality-scale, blueprint, repo governance |
| JSON | `custom_components/lipro/manifest.json`, `hacs.json`, `custom_components/lipro/icons.json`, `custom_components/lipro/translations/*.json`, `custom_components/lipro/firmware_support_manifest.json`, `tests/fixtures/**/*.json` | HA/HACS metadata, UI translations, firmware trust root, boundary fixtures |
| Markdown | `README.md`, `README_zh.md`, `docs/*.md`, `docs/adr/*.md`, `.planning/**/*.md` | user docs, architecture, roadmap, baseline/review governance |

## Runtime And Framework Baseline
- Home Assistant custom-integration model: `custom_components/lipro/__init__.py`, `config_flow.py`, `diagnostics.py`, `system_health.py`, platform modules `light.py`, `cover.py`, `switch.py`, `fan.py`, `climate.py`, `binary_sensor.py`, `sensor.py`, `select.py`, `update.py`.
- Async runtime is HA-first and `aiohttp`-backed; session injection uses `homeassistant.helpers.aiohttp_client.async_get_clientsession` in `custom_components/lipro/__init__.py`, `config_flow.py`, and `firmware_manifest.py`.
- Typed runtime root stays in `ConfigEntry.runtime_data`; control-plane locator is `custom_components/lipro/control/runtime_access.py`; north-star runtime home remains `custom_components/lipro/coordinator_entry.py`.
- Protocol plane is split into explicit homes: `custom_components/lipro/core/protocol/`, `custom_components/lipro/core/api/`, `custom_components/lipro/core/mqtt/`, `custom_components/lipro/core/auth/`.
- Assurance-only telemetry/export lives in `custom_components/lipro/core/telemetry/` and is bridged into control-plane consumers by `custom_components/lipro/control/telemetry_surface.py`.

## First-Party Stack Layout
| Layer | Main paths | Notes |
| --- | --- | --- |
| Control plane | `custom_components/lipro/control/` | lifecycle, service registry/router, diagnostics/system-health surfaces, redaction, runtime access |
| Runtime plane | `custom_components/lipro/coordinator_entry.py`, `custom_components/lipro/core/coordinator/` | single orchestration root, runtime services, MQTT lifecycle, state/command/status runtimes |
| Domain plane | `custom_components/lipro/core/device/`, `custom_components/lipro/core/capability/`, `custom_components/lipro/entities/`, platform files | explicit device surface, capability truth, HA entity projections |
| Protocol plane | `custom_components/lipro/core/protocol/`, `custom_components/lipro/core/api/`, `custom_components/lipro/core/mqtt/`, `custom_components/lipro/core/auth/` | boundary decoders, REST/MQTT façades, auth/session, transport helpers |
| Assurance plane | `custom_components/lipro/core/telemetry/`, `tests/`, `.planning/baseline/`, `.planning/reviews/` | telemetry exporter, replay/evidence, meta guards, governance matrices |

## Runtime Dependencies
| Dependency | Declared in | Used by |
| --- | --- | --- |
| `aiohttp>=3.12.0` | `pyproject.toml` | REST transport, firmware advisory fetch, share worker client |
| `aiomqtt>=2.0.0` | `pyproject.toml`, `custom_components/lipro/manifest.json` | vendor MQTT runtime in `custom_components/lipro/core/mqtt/` |
| `pycryptodome>=3.19.0` | `pyproject.toml`, `custom_components/lipro/manifest.json` | MQTT credential AES decrypt in `custom_components/lipro/core/mqtt/credentials.py` |
| `voluptuous>=0.15.2` | `pyproject.toml` | config flow / service schema validation in `config_flow.py` and `services/contracts.py` |

## Dev, Lint, Type And Test Tooling
- Environment manager and command contract: `uv` via `uv.lock`, `scripts/setup`, `scripts/develop`, `scripts/lint`, `.pre-commit-config.yaml`, and GitHub Actions.
- Strict typing: `pyproject.toml` sets `mypy` strict mode for `custom_components/lipro` and `tests`; typed marker is `custom_components/lipro/py.typed`.
- Lint/format: `ruff` rules and project bans are configured in `pyproject.toml`; pre-commit runs `uv run --extra dev ruff format` and `uv run --extra dev ruff check`.
- Tests: `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-homeassistant-custom-component`, `pytest-benchmark`, `pytest-xdist`, `pytest-mypy-plugins`, and `syrupy` are declared in `pyproject.toml`.
- Security/static checks: `pip-audit` is wrapped by `scripts/lint` and `.github/workflows/ci.yml`; `shellcheck` covers `install.sh` and shell scripts.
- Local reproducibility: `.devcontainer.json` pins `mcr.microsoft.com/devcontainers/python:3.14`, forwards port `8123`, and runs `scripts/setup` post-create.

## CI/CD And Release Toolchain
| Surface | Paths | Current behavior |
| --- | --- | --- |
| CI | `.github/workflows/ci.yml` | `lint`, `governance`, `security`, `test`, `benchmark`, `validate` jobs; all use `uv sync --frozen --extra dev` |
| Governance gates | `.github/workflows/ci.yml`, `scripts/check_architecture_policy.py`, `scripts/check_file_matrix.py`, `tests/meta/test_*guards.py` | enforces north-star dependency/public-surface/version/governance rules |
| Coverage | `.github/workflows/ci.yml`, `scripts/coverage_diff.py`, Codecov upload | requires `--cov-fail-under=95` and uploads `coverage.xml` on push |
| Release | `.github/workflows/release.yml` | reuses `ci.yml`, checks tag vs `pyproject.toml`, zips `custom_components/lipro`, publishes `SHA256SUMS` |
| Dependency updates | `.github/dependabot.yml` | daily updates for `devcontainers`, `github-actions`, `pip`; ignores `homeassistant` |
| HACS / Hassfest | `.github/workflows/ci.yml`, `hacs.json`, `custom_components/lipro/quality_scale.yaml` | validates HA packaging semantics and HACS compatibility when repo is public |

## Config, UX, And Governance Assets
- Integration metadata/assets: `custom_components/lipro/manifest.json`, `custom_components/lipro/icons.json`, `custom_components/lipro/icon.png`, `custom_components/lipro/services.yaml`, `custom_components/lipro/translations/en.json`, `custom_components/lipro/translations/zh-Hans.json`, `custom_components/lipro/quality_scale.yaml`.
- Firmware/config trust assets: `custom_components/lipro/firmware_support_manifest.json` and `custom_components/lipro/firmware_manifest.py`.
- User docs and DX contracts: `README.md`, `README_zh.md`, `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, `docs/README.md`, `docs/developer_architecture.md`, `docs/adr/README.md`.
- Planning/governance truth: `.planning/PROJECT.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/baseline/*.md`, `.planning/reviews/*.md`.
- QA fixtures and evidence assets: `tests/fixtures/**`, `tests/harness/**`, `tests/meta/**`, `scripts/export_ai_debug_evidence_pack.py`.

## Packaging And Delivery Model
- Build backend is `setuptools.build_meta` in `pyproject.toml`; package discovery includes `custom_components*` namespace packages.
- Distribution targets HA users through HACS (`hacs.json`), GitHub Releases (`release.yml`), manual copy (`README*.md`), and shell installer (`install.sh`).
- `install.sh` downloads release archives/checksums from GitHub Releases, supports mirror override for archive metadata, and is guarded by `tests/meta/test_install_sh_guards.py`.
- There is no Docker image, no PyPI publish flow, and no server-side deployment manifest in this repo.

## Explicitly Absent Or Deferred
- No repo-owned database, cache, ORM, or migration stack.
- No OAuth/OIDC or third-party identity provider; auth is vendor phone/password plus token refresh.
- No inbound webhook server.
- No production Prometheus / OpenTelemetry sink today; `.planning/REQUIREMENTS.md` only records them as future evaluation items.
