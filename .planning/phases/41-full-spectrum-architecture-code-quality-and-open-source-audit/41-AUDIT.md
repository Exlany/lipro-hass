# Phase 41 Audit: Full-Spectrum Architecture, Code Quality, and Open-Source Verdict

**Date:** 2026-03-20
**Scope:** `custom_components/lipro/**`、`tests/**`、`docs/**`、`.github/**`、`scripts/**`、核心配置与 planning truth
**Method:** whole-repo read-only review + quantitative scans + parallel domain-specific subreviews

## Audit Method

- 以 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md:47`、`docs/NORTH_STAR_TARGET_ARCHITECTURE.md:64`、`docs/NORTH_STAR_TARGET_ARCHITECTURE.md:92`、`docs/developer_architecture.md:62`、`AGENTS.md:213` 为主裁决基线。
- 逐层审阅 protocol / runtime / domain / control / services / entities / tests / docs / release / governance / repo hygiene，而不是只看 Python 业务代码。
- 量化维度包含：tracked 文件占比、planning 噪音、热点文件、长函数、广义异常、命名残留、测试拓扑、发布信任链、文档分层与开源体验。
- 结论同时报告亮点与问题；所有高价值问题都给出严重度、根因与整改方向。

## Repository Inventory

| Metric | Value |
|---|---:|
| Tracked files | 1253 |
| `.planning/**` tracked files | 643 |
| `.planning/phases/**` tracked files | 602 |
| Repo-wide Python files | 515 |
| `custom_components/lipro` + `scripts` scanned files | 280 |
| `custom_components/lipro` + `scripts` scanned LOC | 42167 |
| `>=300` 行源码文件 | 42 |
| `>50` 行函数 | 44 |
| Broad `except Exception` in production | 0 |
| TODO/FIXME repo-wide | 0 |

## Truth Layers

- **Active truth**：`.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`、baseline/reviews、`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`docs/developer_architecture.md`。
- **Archived evidence**：`.planning/milestones/*.md`、`.planning/v1.5-MILESTONE-AUDIT.md`、`V1_5_EVIDENCE_INDEX.md` 等归档证据。
- **Execution trace**：`.planning/phases/**` 中的 `PLAN/CONTEXT/RESEARCH/SUMMARY/VERIFICATION/VALIDATION`，默认不应自动升格为长期真源，见 `AGENTS.md:213`、`AGENTS.md:218`、`docs/README.md:36`。
- **Repo hygiene noise**：`__pycache__`、coverage、egg-info、`.venv` 等；当前未被 Git 跟踪，但本地噪音仍偏大。

## Baseline Metrics

- 生产代码未发现 broad `except Exception`；说明异常治理克制且有纪律。
- `TODO/FIXME` 为 `0`，说明代码库没有把未完成事项静默塞进实现层。
- 热点主要集中在 protocol boundary、runtime access、OTA、匿名分享与治理脚本，而不是随处发散。
- 真实风险不在“明显烂代码”，而在**高成熟主链周围的边界发黏、执行资产过量入库、以及局部热点继续膨胀**。

## Expert Scorecard

| Dimension | Verdict | Notes |
|---|---|---|
| Architecture | A- | 单主链大体成形，但 control/services 仍发黏 |
| Code Health | B+ | 无 broad catch / TODO，热点与长函数仍明显 |
| Verification & Release | A- | 供应链门禁强，但 release/install E2E 偏弱 |
| Open-Source Readiness | B+ | 对外入口完整，但单维护者与双语一致性拖后腿 |
| Repo Hygiene | C+ | tracked caches 干净，但 `.planning/phases/**` 噪音过重 |
| Overall | **B+ / 8.1** | 已是高成熟仓库，但离“开源旗舰级整洁度”仍差一轮系统收口 |

## Architecture Strengths

- **Protocol plane 收敛成熟**：`LiproProtocolFacade` 作为唯一协议根，统一持有请求策略、诊断上下文、canonical contracts，并显式挂接 REST/MQTT 子门面，见 `custom_components/lipro/core/protocol/facade.py:39`、`custom_components/lipro/core/protocol/facade.py:65`、`custom_components/lipro/core/protocol/facade.py:70`。
- **Boundary normalization 先进**：REST/MQTT decoder family 与 authority/fixture/replay 是成体系的，能有效阻断 raw payload 泄漏，见 `custom_components/lipro/core/protocol/boundary/rest_decoder.py:25`、`custom_components/lipro/core/protocol/boundary/mqtt_decoder.py:22`、`custom_components/lipro/core/protocol/contracts.py:166`。
- **Runtime 单根明确**：`Coordinator` + `RuntimeOrchestrator` + `RuntimeContext` 的显式组合基本符合北极星目标，且设备集合以只读映射暴露，见 `custom_components/lipro/core/coordinator/coordinator.py:53`、`custom_components/lipro/core/coordinator/orchestrator.py:94`、`custom_components/lipro/core/coordinator/runtime_context.py:96`。
- **Domain 与平台投影关系健康**：`LiproDevice` 与 `CapabilityRegistry` 承担真源角色，实体层不直接摸协议内部，见 `custom_components/lipro/core/device/device.py:41`、`custom_components/lipro/core/capability/registry.py:19`、`custom_components/lipro/entities/base.py:87`。
- **根层 HA adapter 保持薄壳**：`custom_components/lipro/__init__.py:356`、`custom_components/lipro/__init__.py:370`、`custom_components/lipro/diagnostics.py:78`、`custom_components/lipro/system_health.py:16` 体现了工厂装配与 thin adapter 约束。
- **OTA 链路是高成熟样板**：本地 trust root + shared cache + arbitration + entity projection 的组合兼顾 authority、性能与用户体验，见 `custom_components/lipro/entities/firmware_update.py:114`、`custom_components/lipro/firmware_manifest.py:56`。

## Architecture Findings

- **High — control/services 边界仍发黏**：`services/* -> control/*` 与 `control/* -> services/*` 双向耦合仍明显，formal home 虽然名义上固定在 `control/`，但 helper surface 已开始反客为主，见 `custom_components/lipro/services/registrations.py:9`、`custom_components/lipro/services/device_lookup.py:14`、`custom_components/lipro/services/maintenance.py:21`、`custom_components/lipro/services/diagnostics/helpers.py:19`、`custom_components/lipro/control/service_router_handlers.py:58`。这会放大 ownership 模糊与后续切分成本。
- **Medium — `RuntimeAccess` 仍偏反射型读模型**：`custom_components/lipro/control/runtime_access.py:23`、`custom_components/lipro/control/runtime_access.py:24`、`custom_components/lipro/control/runtime_access.py:70` 直接围绕显式成员探测与 `MagicMock` 语义写生产逻辑，说明 runtime public read API 仍不够正式。
- **Medium — `services/maintenance.py` 职责混杂**：同文件既处理 `refresh_devices`，又承担 device-registry listener / entry reload 基础设施，并被 `custom_components/lipro/runtime_infra.py:14` 反向调用；这更像 runtime/control infra，而不是 service helper。
- **Medium — schedule service 直接依赖 protocol codec/type**：`custom_components/lipro/services/schedule.py:12`、`custom_components/lipro/services/schedule.py:13`、`custom_components/lipro/services/schedule.py:14` 说明 control/service 层仍借用 `core/api` 内部 contract，边界略有穿透。
- **Low — 支撑层又套支撑层**：`services/diagnostics/helpers.py`、`control/developer_router_support.py`、`control/service_router_support.py` 形成双层 wrapper，虽未形成第二主链，但已经出现“支持层套支持层”的壳味。

## Naming and Residual Findings

- **Medium — ADR 仍在回灌旧术语**：`docs/adr/README.md:47`、`docs/adr/0004-explicit-lightweight-boundaries.md:17`、`docs/adr/0004-explicit-lightweight-boundaries.md:47` 仍使用 `API Client` / `mixin` 叙事，与 façade 时代的正式术语存在漂移。
- **Medium — 生产代码还有少量误导性文案**：`custom_components/lipro/core/api/endpoints/devices.py:13` 与 `custom_components/lipro/core/api/endpoints/misc.py:32` 仍写 `Legacy ... mixin`；`custom_components/lipro/core/auth/manager.py:28`、`custom_components/lipro/core/auth/manager.py:79` 仍保留 “Legacy storage payload” / “API client” 话术。
- **Low — residual shell 仍可见**：`custom_components/lipro/coordinator_entry.py:1` 只是 `Coordinator` export，`custom_components/lipro/__init__.py:141`、`custom_components/lipro/__init__.py:160` 又专门 lazy-load 它；这不是功能 bug，但会增加命名与入口理解成本。
- **Medium — 同名对象跨层重影**：`custom_components/lipro/core/anonymous_share/manager.py:64` 与 `custom_components/lipro/services/share.py:42` 同名 `AnonymousShareManager`；`custom_components/lipro/core/mqtt/connection_manager.py:25` 与 runtime mqtt 子树中的同类命名也接近，增加跳读成本。

## Directory and Ownership Findings

- **优点**：目录大体能映射到 north-star planes；`custom_components/lipro/core/protocol/**`、`custom_components/lipro/core/coordinator/**`、`custom_components/lipro/control/**`、`custom_components/lipro/entities/**` 的语义总体清晰。
- **Medium — `services/maintenance.py` 的目录归属偏弱**：infra 行为混入 service 目录，破坏了“formal home + helper surface”的可解释性。
- **Low — `models.py` / `types.py` / `registry.py` 这类泛名文件重复较多**：`custom_components/lipro/control/models.py:1`、`custom_components/lipro/core/telemetry/models.py:1`、`custom_components/lipro/core/capability/models.py:1` 等会提高导航成本。
- **Medium — 跨层同名转发过多**：`query_device_status`、`send_command`、`refresh_access_token` 等在 5~7 个文件里出现同名中继，虽符合分层，却降低问题追踪效率，典型链路见 `custom_components/lipro/core/api/endpoint_surface.py:38`、`custom_components/lipro/core/api/rest_facade_endpoint_methods.py:32`、`custom_components/lipro/core/protocol/facade.py:223`、`custom_components/lipro/core/protocol/rest_port.py:49`。

## Quality Gates and Testing

- **亮点**：治理型测试和发布信任链很强。`tests/meta/test_dependency_guards.py:44`、`tests/meta/test_public_surface_guards.py:1`、`tests/meta/test_governance_guards.py:218`、`tests/meta/test_external_boundary_fixtures.py:27` 构成了罕见完整的治理护栏；`.github/workflows/release.yml:177`、`.github/workflows/release.yml:212`、`.github/workflows/release.yml:257` 则把 SBOM / attestation / CodeQL / cosign 纳入正式 release 路径。
- **High — release/install 缺少真实 E2E smoke**：当前更像结构契约验证，而不是“产物真的能装、能回滚、能落位”的执行态验证，见 `tests/meta/test_governance_release_contract.py:40`、`tests/meta/test_install_sh_guards.py:10`。
- **High — 覆盖率门禁偏总量，缺少变更面约束**：CI 强制 `95%` 总覆盖，但 `scripts/coverage_diff.py:34`、`scripts/coverage_diff.py:43` 无 baseline 时直接跳过 diff，新增低覆盖代码可能被高历史覆盖稀释。
- **Medium — 本地门禁与 CI 非完全同构**：`scripts/lint:12`、`scripts/lint:51` 默认不跑 governance/pytest；`scripts/lint:74` 对缺失 `shellcheck` 仍可跳过；`.pre-commit-config.yaml:55`、`.pre-commit-config.yaml:67` 也只覆盖部分门禁。
- **Low — 局部异步测试仍依赖真实时间**：`tests/core/test_debounce.py:24`、`tests/core/test_boundary_conditions.py:338` 等存在慢测与偶发抖动风险。

## Release and Install Posture

- **强项**：`install.sh:154`、`install.sh:205`、`install.sh:301`、`install.sh:444`、`install.sh:523` 显示安装器已考虑 zip 预检、路径穿越、checksum、rollback；release pipeline 也体现了较强的供应链意识。
- **Medium — `security_gate` 的 Python 选择不够显式**：项目要求 `pyproject.toml:11` 为 `>=3.14.2`，但 `.github/workflows/release.yml:33` 的 `security_gate` 仅 `setup-uv`，没有像其他 job 一样显式 `setup-python`。
- **Low — benchmark 仍偏留证据而非防回退**：`.github/workflows/ci.yml:231`、`.github/workflows/ci.yml:240` 主要上传结果，没有阈值或历史基线对比。

## Open-Source Experience

- **亮点**：`README.md:72`、`SUPPORT.md:5`、`docs/TROUBLESHOOTING.md:12` 已形成安装→排障→支持分流链；`CONTRIBUTING.md:23`、`CONTRIBUTING.md:117`、`.devcontainer.json:2` 也让贡献环境具备可执行性。
- **High — 单维护者连续性是最大治理风险**：`SUPPORT.md:32`、`SECURITY.md:33`、`.github/CODEOWNERS:1`、`docs/MAINTAINER_RELEASE_RUNBOOK.md:105` 明示缺少 delegate / backup maintainer；这直接拉低 bus factor。
- **Medium — 贡献入口被治理术语压重**：`CONTRIBUTING.md:73`、`CONTRIBUTING.md:76`、`docs/README.md:24`、`.github/pull_request_template.md:8` 让外部贡献者过早接触 `.planning/*` / governance registry / evidence index 等维护者语汇。
- **Medium — 安全披露只有 GitHub 私密 advisory 单一路径**：`SECURITY.md:58`、`SECURITY.md:64`、`SECURITY.md:75` 缺少邮箱或备用联系人，在单维护者模型下放大失联风险。
- **Medium — 双语策略不一致**：`README.md:19` 承诺双语，但 `CHANGELOG.md:1` 为纯中文，`SUPPORT.md:1` 与 `docs/TROUBLESHOOTING.md:1` 偏英文，`docs/README.md:1` 与 `docs/developer_architecture.md:1` 又偏中文/混合。
- **Low — 文档重复与易过时字面量**：`README.md:94`、`README_zh.md:94` 的版本示例硬编码，且 `docs/developer_architecture.md:3`、`CHANGELOG.md:33` 暴露内部阶段时态，长期易漂移。

## Repo Hygiene Findings

- **High — `.planning/phases/**` tracked 过量**：全仓 `1253` 个 tracked 文件里，`.planning` 占 `643`，其中 `.planning/phases/**` 就有 `602`；细分还有 `189` 个 `*-PLAN.md`、`185` 个 `*-SUMMARY.md`、`50` 个 `*-CONTEXT.md`、`43` 个 `*-RESEARCH.md`。这与 `AGENTS.md:213`、`AGENTS.md:218`、`docs/README.md:36` 的“phase 默认是 execution trace”口径相冲突。
- **优点 — tracked caches 干净**：`.gitignore:1` 到 `.gitignore:37` 已覆盖 `__pycache__`、coverage、egg-info、pytest/ruff/mypy cache；当前未发现这些噪音被 Git 跟踪。
- **Low — 本地 ignored 噪音仍高**：本地约 `73` 个 ignored 项，其中 `59` 个 `__pycache__`，会放大搜索和审阅噪音，但不构成仓库污染。
- **High — 热点文件集中度偏高**：`scripts/check_file_matrix.py:1`、`custom_components/lipro/core/protocol/boundary/rest_decoder_support.py:1`、`custom_components/lipro/core/anonymous_share/manager.py:1`、`custom_components/lipro/control/runtime_access.py:1`、`custom_components/lipro/core/ota/manifest.py:1` 是最值得优先拆薄的高杠杆目标。
- **Medium — 语义压扁而非 broad catch**：`custom_components/lipro/core/api/diagnostics_api_service.py:139`、`custom_components/lipro/core/anonymous_share/share_client.py:153` 不使用 broad `Exception`，但仍把多种失败折叠成弱语义返回，削弱了诊断颗粒度。

## Final Verdict

`lipro-hass` 已经不是“民间脚本式”仓库，而是**高度治理化、架构意识强、供应链信任链完整**的成熟项目；其真正短板不再是粗糙实现，而是：

1. **control / services 的边界还不够干净**；
2. **少数热点模块复杂度继续攀升**；
3. **release/install 与新增覆盖的执行型验证不够强**；
4. **开源项目外部体验仍被单维护者模型与治理噪音拉低**；
5. **phase 执行资产过量入库，正在侵蚀正式真源的清晰度**。

若以国际优秀开源集成项目为参照，本仓库已经具备 **强架构、强治理、强守卫** 的骨架；下一轮最该做的，不是重写主链，而是**收边界、拆热点、降噪音、补真实执行验证、提升外部协作体验**。
