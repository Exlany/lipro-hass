# Codebase Concerns

**Analysis Date:** 2026-03-28

> Snapshot: `2026-03-28`
> Freshness: 基于 `.planning/{ROADMAP.md,REQUIREMENTS.md,STATE.md}`、`.planning/reviews/{FILE_MATRIX.md,RESIDUAL_LEDGER.md,KILL_LIST.md}`、`custom_components/lipro/**`、`tests/**` 与当前 public-doc / governance truth 的截面。
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、审阅与后续实现对齐。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{PROJECT.md,ROADMAP.md,REQUIREMENTS.md,STATE.md}`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本文件不得反向充当当前治理真源。

## Risk Summary

- Overall posture: `Medium`. `.planning/reviews/RESIDUAL_LEDGER.md` 与 `.planning/reviews/KILL_LIST.md` 明确记录当前是 zero-active closeout posture，因此主要风险不是“未登记的大故障”，而是热点集中、治理连续性与验证盲区。
- Highest priority: `High` = 单维护者连续性 / private-access 治理约束、runtime/protocol 热点聚集、诊断与匿名分享脱敏漂移风险。
- Medium priority: 大型测试热点、`Any`/动态 payload 类型债、PR 路径缺少性能与 preview 兼容性阻塞门禁、平台基线过新。
- Low priority: 固件 advisory 远端新鲜度、`outlet_power` legacy side-car fallback。

## Phase 124 Concern Update

- `Phase 124` 没有新增 active residual family；本轮的主要成果是把 auth-flow-schedule carry-forward 收回正式 homes，而不是创造新的热点。
- 当前剩余高优先级 concern 继续集中在 runtime/control 反射边界、runtime snapshot 双真源拼装与 orchestrator assembly knot；这些不属于 Phase 124 新引入的问题。
- 若后续仍要继续重构，应优先处理 control → runtime contract-first port、root assembly provider injection 与 broader hotspot inward split，而不是再次回头修补 Phase 124 已冻结的 auth/flow/schedule formal homes。

## Tech Debt

**Runtime / protocol hotspot concentration:**
- Risk Level: `High`
- Issue: `Phase 101` 已把 `anonymous_share/manager.py` 收口成 435 行更诚实的 formal home，并把 aggregate outcome/accessor drift 压回 inward seams；`rest_decoder.py` / `rest_decoder_support.py` 也已统一 boundary truth 与 fallback-property semantics。但 runtime/protocol 复杂度仍集中在少数正式文件与 support collaborators：`custom_components/lipro/core/coordinator/runtime/command_runtime.py` (465 行)、`custom_components/lipro/core/anonymous_share/manager.py` (435 行)、`custom_components/lipro/core/protocol/boundary/rest_decoder.py` (425 行)、`custom_components/lipro/core/protocol/boundary/rest_decoder_support.py` (417 行)、`custom_components/lipro/core/api/status_fallback_support.py` (414 行)、`custom_components/lipro/core/api/rest_facade.py` (418 行)、`custom_components/lipro/entities/firmware_update.py` (418 行)。
- Evidence: `.planning/reviews/FILE_MATRIX.md` 仍将这些文件标为长期正式 home / local support collaborators；`.planning/REQUIREMENTS.md`、`.planning/ROADMAP.md` 与 `.planning/baseline/VERIFICATION_MATRIX.md` 已把 `Phase 98 -> 101` 退回 predecessor / previous-archived evidence，并把 archived-only current route 前推到 `Phase 102`。
- Phase 101 已把 `anonymous_share/manager.py` 收窄到 435 行 formal manager home，并让 `mqtt_api_service.py` 复用 boundary MQTT-config decode truth。
- Phase 102 没有重开 production formal homes；它只把 governance portability、verification stratification 与 docs/release continuity wording 压回同一条 archived-only baseline。
- Impact: 命令、状态、MQTT、入口 wiring、OTA 与匿名分享改动的回归半径大，review/triage 成本高，继续拖慢局部演进。
- Fix approach: 继续沿既有 formal seams inward decomposition，优先拆纯函数/纯策略层，不新增 public root，不让 helper 重新长成第二故事线。

**Test hotspot concentration:**
- Risk Level: `Medium`
- Issue: 仍有多份大测试文件承担过多主题：`tests/core/api/test_api_status_service.py` (594 行)、`tests/platforms/test_light_entity_behavior.py` (592 行)、`tests/services/test_services_diagnostics.py` (580 行)、`tests/core/api/test_api_command_surface_responses.py` (578 行)。
- Evidence: `.planning/reviews/RESIDUAL_LEDGER.md` 虽已记录 giant assurance carriers closeout，但当前仓内仍存在多份 >580 行的 topic-mixed suites。
- Impact: 失败定位慢，review diff 噪音大，后续 topicization 仍有成本。
- Fix approach: 继续按 capability / endpoint / platform behavior / exporter path 切成 concern-local suites，保留 thin anchor，复用 `tests/helpers/` 与 `tests/*/support.py`。

**Typed boundary debt under strict typing:**
- Risk Level: `Medium`
- Issue: `pyproject.toml` 开启 `mypy strict = true`，但 `custom_components` 仍扫描到约 359 个 `Any` 令牌，动态 payload 主要集中在 `custom_components/lipro/runtime_types.py`、`custom_components/lipro/core/coordinator/types.py`、`custom_components/lipro/core/protocol/boundary/rest_decoder_support.py`、`custom_components/lipro/core/protocol/boundary/schema_registry.py`、`custom_components/lipro/core/command/trace.py`。
- Evidence: `rg` 扫描显示 `Any` 仍大量存在；上述文件直接承载 `dict[str, Any]`、`JsonObject`、动态 trace/payload 映射。
- Impact: 边界漂移更多依赖测试而不是类型系统阻断，vendor payload 变化更容易深穿到 runtime。
- Fix approach: 从 protocol boundary 与 telemetry/trace family 开始，把 `Any` 缩成 `TypedDict`、`Protocol`、更窄 union；新增“禁止扩大 `Any` 面积”的 focused guard。

## Known Bugs

**Firmware advisory freshness lag:**
- Risk Level: `Low`
- Symptoms: OTA advisory 数据最长可缓存 30 分钟；远端获取失败时会继续返回旧缓存。
- Files: `custom_components/lipro/firmware_manifest.py`, `custom_components/lipro/entities/firmware_update.py`
- Trigger: `https://lipro-share.lany.me` 不可达、返回非 200、或 JSON 不合法时。
- Workaround: 当前 certified truth 仍以本地 `custom_components/lipro/firmware_support_manifest.json` 为准，远端 advisory 仅作补充信息。

## Security Considerations

**Diagnostics / anonymous-share redaction drift:**
- Risk Level: `High`
- Risk: 脱敏仍主要依赖枚举 key 与 regex 模式；若 vendor 新增敏感字段且未同步进入两套 sanitizer，诊断或分享载荷可能漏脱敏。
- Files: `custom_components/lipro/control/redaction.py`, `custom_components/lipro/core/anonymous_share/sanitize.py`, `custom_components/lipro/core/anonymous_share/manager.py`, `tests/core/anonymous_share/test_sanitize.py`, `tests/core/test_diagnostics_config_entry.py`, `tests/fixtures/external_boundaries/`
- Current mitigation: 已有 dedicated redaction helper、log safety 测试与 diagnostics/share 相关回归用例。
- Recommendations: 统一单一 redaction contract/registry；新增“看起来像 secret / token / identifier 的未知字段默认失败”测试；把 sanitizer miss 记为结构化指标。

**Single-maintainer security custody:**
- Risk Level: `High`
- Risk: 安全确认、修复发布与 release custody 依赖唯一 maintainer；无 documented delegate。
- Files: `.github/CODEOWNERS`, `SECURITY.md`, `SUPPORT.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`, `.planning/baseline/GOVERNANCE_REGISTRY.json`
- Current mitigation: 仓库已诚实记录 maintainer-unavailable drill，并要求 maintainer 不可用时冻结新 tag 与新 release promise。
- Recommendations: 增加至少一名 delegate；把 custody 恢复步骤写成 checklist；若仓库继续 private-access，补一个稳定可达的私密 intake / mirror 方案。

## Performance Bottlenecks

**PR path misses benchmark-governed hot paths:**
- Risk Level: `Medium`
- Problem: 阻塞测试路径显式 `--ignore=tests/benchmarks`；benchmark lane 只在 `schedule` / `workflow_dispatch` 运行，不进 PR blocking lane。
- Files: `.github/workflows/ci.yml`, `CONTRIBUTING.md`, `tests/benchmarks/benchmark_baselines.json`, `tests/benchmarks/test_command_benchmark.py`, `tests/benchmarks/test_mqtt_benchmark.py`, `tests/benchmarks/test_device_refresh_benchmark.py`, `tests/benchmarks/test_coordinator_performance.py`
- Cause: 当前性能回归被定义为 maintainer-facing signal，而不是每次 PR 的硬门禁。
- Improvement path: 对 `command_runtime`、`mqtt_runtime`、`device_runtime`、decoder hot path 增加 touched-path microbenchmark 或 label-gated PR benchmark 子集。

**Remote firmware advisory fetch is sequential and single-origin:**
- Risk Level: `Low`
- Problem: `custom_components/lipro/firmware_manifest.py` 顺序请求 `REMOTE_FIRMWARE_ADVISORY_URLS`，每个请求 5 秒 timeout，且两个 URL 都位于同一域名。
- Files: `custom_components/lipro/firmware_manifest.py`
- Cause: 远端 advisory 是补充数据源，当前主要优化的是简化实现与缓存，而不是多源韧性。
- Improvement path: 记录 last-success telemetry、并行尝试多个源、或把 advisory snapshot 随 release artifact 一起发布为 mirrorable asset。

## Fragile Areas

**HA root wiring / lazy factory adapter:**
- Risk Level: `High`
- Files: `custom_components/lipro/__init__.py`, `custom_components/lipro/control/entry_lifecycle_controller.py`, `custom_components/lipro/control/service_registry.py`, `custom_components/lipro/control/service_router_handlers.py`（已在 Phase 123 收敛 non-diagnostics family，但仍是 control-plane 关键热点）
- Why fragile: entry setup、auth、runtime bootstrap、service registration 与 lazy loader contract 在此收口；小改动就可能破坏启动路径或重新长出 second root。
- Safe modification: 让 `custom_components/lipro/__init__.py` 继续只做 thin adapter；新增逻辑优先下沉到 control/runtime formal home；触碰后至少重跑 `tests/core/test_init*.py`、`tests/core/test_control_plane.py`、`tests/services/test_services_registry.py`。
- Test coverage: 有力但仍偏广，尤其 init/control 改动常跨多套 suite 才能完全兜住。

**Anonymous-share submission flow:**
- Risk Level: `Medium`
- Files: `custom_components/lipro/core/anonymous_share/manager.py`, `custom_components/lipro/core/anonymous_share/manager_submission.py`, `custom_components/lipro/core/anonymous_share/share_client_submit.py`
- Why fragile: 聚合状态、token refresh、submit outcome、report redaction 与多 scope 语义跨模块耦合。
- Safe modification: 保持 outcome-native contract、primary-scope client 选择与 aggregate neutral semantics；不要回退成 accessor re-export 或 bool-only bridge，先补 focused fixture/test，再拆 orchestration。
- Test coverage: `tests/core/anonymous_share/*.py`, `tests/core/test_share_client_submit.py`, `tests/integration/test_telemetry_exporter_integration.py` 覆盖不错，但 topology 仍然复杂。

**Protocol decoding and schedule handling:**
- Risk Level: `Medium`
- Files: `custom_components/lipro/core/protocol/boundary/rest_decoder.py`, `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py`, `custom_components/lipro/services/schedule.py`, `custom_components/lipro/core/api/schedule_service.py`
- Why fragile: vendor payload normalization、schedule timing coercion、mesh/BLE edge case 与 service response 语义必须同步演进。
- Safe modification: 优先改 fixture 与 boundary decoder / decode-support truth，不要把 compat rescue 或 vendor metadata fallback 重新抬回 runtime/service 正式路径。
- Test coverage: `tests/core/api/test_protocol_contract_*.py`, `tests/services/test_services_schedule.py`, `tests/core/api/test_api_transport_and_schedule_*.py` 提供了强护栏。

## Scaling Limits

**Support / release throughput capped by one maintainer:**
- Risk Level: `High`
- Current capacity: 实际 triage / release owner 只有 `.github/CODEOWNERS` 中的 `@Exlany`。
- Limit: maintainer 不可用时，`SUPPORT.md`、`SECURITY.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md` 与 `.planning/baseline/GOVERNANCE_REGISTRY.json` 都要求冻结新 tag 与新 release promise。
- Scaling path: 补 delegate、拆分 triage 与 release custody、把 continuity 演练从“文档 truth”升级为“可执行流程”。

**Platform baseline is intentionally narrow:**
- Risk Level: `Medium`
- Current capacity: `pyproject.toml` 要求 `Python >=3.14.2`，`hacs.json` 与 dev 依赖要求 `Home Assistant 2026.3.1`。
- Limit: contributor / fork / 下游用户只要略低于当前生态基线就难以复现问题；兼容面扩大前没有更宽的支持矩阵。
- Scaling path: 要么继续保持 latest-only honesty，要么先扩 CI/test matrix 再扩大支持承诺。

## Dependencies at Risk

**GitHub-hosted release/security chain is mission-critical:**
- Risk Level: `Medium`
- Risk: release trust 依赖 `.github/workflows/release.yml`、`.github/workflows/codeql.yml`、GitHub dependency graph SBOM、artifact attestation、OIDC/cosign 验证与 GitHub Release 发布链。
- Impact: 平台故障、权限丢失或 repo admin 受限时，即使代码 ready 也可能无法按当前流程完成发布。
- Migration plan: 保留 `docs/MAINTAINER_RELEASE_RUNBOOK.md` 中的 non-publish verification path，并把关键验证输出设计成可镜像/可离线复核的资产。
- Files: `.github/workflows/release.yml`, `.github/workflows/codeql.yml`, `SECURITY.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`

**Cutting-edge platform pins:**
- Risk Level: `Medium`
- Risk: `requires-python = ">=3.14.2"` 与 `homeassistant==2026.3.1` 提高生态滞后风险，并缩窄 contributor parity。
- Impact: 外部协作者、复现环境与下游 fork 更容易在环境层先分叉，preview/deprecation 问题也更依赖定时巡检而非日常 PR 流。
- Migration plan: 若保持最新基线不变，就继续严格限制文档承诺；若要扩大 adoption，先补兼容矩阵与额外 CI lane。
- Files: `pyproject.toml`, `hacs.json`, `custom_components/lipro/manifest.json`, `.github/workflows/ci.yml`

## Missing Critical Features

**Public contributor intake remains access-mode constrained:**
- Risk Level: `Medium`
- Problem: 仓库明确是 private-access，`README.md`、`SUPPORT.md`、`SECURITY.md` 多次说明 HACS、Issues、Discussions、Security UI 只在当前 access mode 可见时成立，或等待 future public mirror。
- Blocks: 更广泛的开源协作、公共 issue intake、公开 HACS 安装路径与社区自助验证闭环。
- Files: `README.md`, `SUPPORT.md`, `SECURITY.md`, `.planning/baseline/GOVERNANCE_REGISTRY.json`, `hacs.json`

**Documented delegate is still missing:**
- Risk Level: `High`
- Problem: `.planning/baseline/GOVERNANCE_REGISTRY.json` 仍写明 `documented_delegate: false`，`.github/CODEOWNERS` 仍只有单 owner。
- Blocks: 可持续 release custody、并行 triage、以及 maintainer 不可用时的 bounded response。
- Files: `.planning/baseline/GOVERNANCE_REGISTRY.json`, `.github/CODEOWNERS`, `SUPPORT.md`, `docs/MAINTAINER_RELEASE_RUNBOOK.md`

## Test Coverage Gaps

**PR-blocking validation skips performance coverage:**
- What's not tested: 热路径 benchmark regression 不会在常规 PR 阻塞门禁中被发现。
- Files: `.github/workflows/ci.yml`, `tests/benchmarks/benchmark_baselines.json`, `tests/benchmarks/test_command_benchmark.py`, `tests/benchmarks/test_mqtt_benchmark.py`, `tests/benchmarks/test_device_refresh_benchmark.py`, `tests/benchmarks/test_coordinator_performance.py`
- Risk: 命令/MQTT/device refresh 等性能回归更可能先落到 `main`，再由 schedule/manual lane 发现。
- Priority: `Medium`

**Preview compatibility remains advisory-only:**
- What's not tested: Home Assistant preview / deprecation breakage 不会在每次 PR 上阻塞。
- Files: `.github/workflows/ci.yml`, `CONTRIBUTING.md`
- Risk: 生态弃用或 upcoming breakage 可能在 scheduled preview lane 之前悄悄积累。
- Priority: `Medium`

---

*Concerns audit: 2026-03-27*


## Phase 90 Concern Freeze

- The remaining hotspot risk is no longer “which files should die”, but how to split inward without changing outward ownership.
- Delete-gate language must stay localized and explicit; formal homes are not cleanup folklore.


## Phase 91 Concern Focus

- The dominant risk is no longer ownership ambiguity, but keeping typed boundary honesty frozen while Phase 92 narrows redaction/control shells.
- Canonicalization must happen once at the protocol root; any runtime-side re-normalization is now considered architectural drift.
