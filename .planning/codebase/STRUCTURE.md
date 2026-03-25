# STRUCTURE
> Snapshot: `2026-03-19`
> Freshness: Phase 38 + 本次 arch/structure 终极审阅对齐刷新；仅按 `AGENTS.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md`、`docs/developer_architecture.md` 与当前 CI/release/public-doc truth 截面成立。上述真源变更后，本图谱必须同步刷新或标记过时。
> Repository: `/var/tmp/coolvibe/worktrees/edf26778937a-/lipro-hass`
> Focus: `arch`
> Derived collaboration map: 本文件是受约束的协作图谱 / 派生视图，仅用于导航、协作与局部审阅。
> Authority: 若与 `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`.planning/{ROADMAP,REQUIREMENTS,STATE}.md`、`.planning/baseline/*.md`、`.planning/reviews/*.md` 或 `docs/developer_architecture.md` 冲突，以后者为准；本图谱不得反向充当当前治理真源，且必须同步回写、标记为过时，或注明历史观察。

## 1. Scope And Reading Set
本结构图谱已纳入：
- `AGENTS.md`
- `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`
- `docs/developer_architecture.md`
- `.planning/PROJECT.md`
- `.planning/STATE.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/baseline/*.md`
- `.planning/reviews/*.md`
- `custom_components/lipro/**`
- `tests/**`

## 2. Structural Verdict
当前仓库的目录清晰度已经明显高于早期“client/coordinator/helper 散落式”状态，核心判断如下：
1. `custom_components/lipro/control/`、`custom_components/lipro/core/coordinator/`、`custom_components/lipro/core/protocol/`、`custom_components/lipro/core/capability/`、`custom_components/lipro/core/device/` 构成正式骨架。
2. `custom_components/lipro/services/` 已从历史 wiring carrier 收敛为 control-plane support cluster。
3. `custom_components/lipro/core/api/` 与 `custom_components/lipro/core/mqtt/` 的目录归属已经被压回 protocol slice，但命名与 helper spine 仍保留 residual 味道。
4. `tests/` 的组织方式与五平面基本镜像，对维护性是加分项；`tests/meta/` 则把目录边界写成可执行守卫。

## 2.1 Phase 35-38 结构增量
- `custom_components/lipro/core/api/client.py` 现在只保留 stable import home；`rest_facade.py` 不再同时吸附 request pipeline 与 endpoint forwarding 细节，这些复杂度已下沉到 `request_gateway.py`、`transport_executor.py` 与 `endpoint_surface.py`。
- `custom_components/lipro/core/protocol/facade.py` 现在通过 `rest_port.py` 与 `mqtt_facade.py` 组合 child façade，而不是把 `_rest_port` / MQTT glue 全堆在 root body。
- `custom_components/lipro/core/coordinator/services/polling_service.py` 已成为 runtime/service seam 的正式 helper home；`Coordinator` 中与 polling 相关的方法现为 thin wrapper。
- `tests/core/test_init_service_handlers*.py`、`tests/core/test_init_runtime*.py` 与 `tests/meta/test_governance_phase_history*.py` 形成稳定 topic suites；聚合根文件只保留共享 helper，不再承载跨故事线巨石测试。
- `Phase 38` 未新增新的 active residual 目录；当前结构问题主要表现为热点文件偏厚与历史命名仍留在 protocol slice 内部。

## 3. Top-Level Layout
| 路径 | 归属 | 结构作用 | 维护性判断 |
|---|---|---|---|
| `.planning/` | Governance / assurance | 项目状态、baseline、review、phase 证据 | 真源集中；适合仲裁，不适合承载实现细节 |
| `docs/` | Design / ADR / onboarding | 北极星、开发者架构、ADR | 与 `.planning/` 分工清楚；需持续保持同步 |
| `custom_components/lipro/` | Production code | HA integration 正式实现 | 结构已清晰，但仍有少量 legacy naming |
| `tests/` | Assurance implementation | 单元、集成、治理、fixture、replay、evidence | 目录镜像良好，是仓库可维护性的关键支撑 |

## 4. Production Tree Ownership
### 4.0 Entry Surface Matrix
代码、文档与配置入口已经形成比较稳定的入口矩阵：
- HA 运行入口：`custom_components/lipro/__init__.py`、`custom_components/lipro/coordinator_entry.py`、`custom_components/lipro/diagnostics.py`、`custom_components/lipro/system_health.py`
- 配置/接入入口：`custom_components/lipro/config_flow.py`、`custom_components/lipro/flow/options_flow.py`、`custom_components/lipro/headless/boot.py`（proof-only bootstrap seam）
- 平台投影入口：`custom_components/lipro/light.py`、`custom_components/lipro/switch.py`、`custom_components/lipro/sensor.py`、`custom_components/lipro/binary_sensor.py`、`custom_components/lipro/fan.py`、`custom_components/lipro/climate.py`、`custom_components/lipro/cover.py`、`custom_components/lipro/select.py`、`custom_components/lipro/update.py`
- 包与发布配置入口：`pyproject.toml`、`custom_components/lipro/manifest.json`、`custom_components/lipro/services.yaml`、`custom_components/lipro/quality_scale.yaml`
- 文档入口：`README.md`、`README_zh.md`、`docs/README.md`、`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`docs/developer_architecture.md`、`docs/TROUBLESHOOTING.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`docs/adr/README.md`
- 治理/校验脚本入口：`scripts/check_architecture_policy.py`、`scripts/check_file_matrix.py`、`scripts/export_ai_debug_evidence_pack.py`

### 4.1 `custom_components/lipro/` 根目录
根目录同时承载三类文件：
- HA adapter：`__init__.py`、`config_flow.py`、`diagnostics.py`、`system_health.py`、`coordinator_entry.py`
- platform entrypoints：`light.py`、`switch.py`、`sensor.py`、`binary_sensor.py`、`fan.py`、`climate.py`、`cover.py`、`select.py`、`update.py`
- manifest/config assets：`manifest.json`、`services.yaml`、`quality_scale.yaml`、`firmware_support_manifest.json`

判断：
- 根目录如今主要保留 HA-required entrypoints，方向正确。
- `coordinator_entry.py` 作为 runtime home 的单文件出口命名清楚，比把 `Coordinator` 混在 `core/__init__.py` 更可维护。
- platform 文件平铺在根目录是 Home Assistant 约定，不属于结构问题；真正的业务逻辑已下沉到 `entities/`、`helpers/platform.py`、`core/**`。

### 4.2 `custom_components/lipro/control/`
关键文件：
- `entry_lifecycle_controller.py`
- `service_registry.py`
- `service_router.py`
- `developer_router_support.py`
- `runtime_access.py`
- `diagnostics_surface.py`
- `system_health_surface.py`
- `telemetry_surface.py`

判断：
- 这是当前最清晰的目录之一：owner、adapter、locator、router、surface 各有单独文件。
- `service_router.py` 与 `developer_router_support.py` 的拆分提升了边界清晰度：public handler 留在 router，private glue 下沉到 helper home。
- `runtime_access.py` 把 `entry.runtime_data` 访问集中到一个位置，降低了 control/runtime 边界漂移风险。
- `telemetry_surface.py` 的术语收口已在 Phase 25.2 完成：bridge helper 现只承认 `Coordinator.protocol`，辅助层与正式 runtime/protocol 术语保持一致。
- `schedule.py`、`diagnostics/handlers.py` 与 `entities/firmware_update.py` 在 Phase 27 已统一改走 `coordinator.protocol_service`；这说明 runtime-owned protocol capability port 已真正成为正式消费面，而不是只停留在 coordinator 内部。

### 4.3 `custom_components/lipro/services/`
关键文件：
- `registry.py`
- `execution.py`
- `diagnostics/`
- `device_lookup.py`
- `share.py`
- `schedule.py`
- `command.py`

判断：
- 本目录现在更像 control-plane leaf collaborator cluster，而不是独立一层。
- `control/service_registry.py` + `services/registry.py` 负责 HA service declaration / register mechanics；仓库已不再保留额外的 `services/registrations.py` compat shell，真正 handler 统一路由到 `control/service_router.py`。
- `execution.py` 的名称仍偏宽泛，但其当前职责已收敛为正式 service execution facade；Phase 5 已关闭 coordinator 私有 auth seam，不应再把它写成 active residual。

### 4.4 `custom_components/lipro/core/`
这是正式骨干目录，但内部结构已经明显分层：
- `core/protocol/`：正式 protocol root、contracts、boundary、session、telemetry
- `core/api/`：REST child façade + helper spine + endpoint collaborators
- `core/mqtt/`：concrete MQTT transport slice
- `core/coordinator/`：runtime root、services、runtime helpers、mqtt lifecycle
- `core/capability/`：capability truth
- `core/device/`：device aggregate、snapshot、view、state、identity、extras
- `core/telemetry/`：observer-only assurance exporter
- `core/auth/`、`core/command/`、`core/ota/`、`core/anonymous_share/`、`core/utils/`：support clusters

判断：
- `core/` 不再是“所有业务都往里塞”的黑盒，子目录边界已经足够清楚。
- 其中 `core/coordinator/` 与 `core/protocol/` 是两条最稳定的正式主骨架；`core/api/`、`core/mqtt/` 则是协议面的物理切片，不再拥有 root 身份。

## 5. Module Boundary Quality
| 目录 | 边界清晰度 | 证据文件 | 备注 |
|---|---|---|---|
| `custom_components/lipro/control/` | 高 | `control/service_router.py`、`control/runtime_access.py`、`tests/core/test_control_plane.py` | 结构与职责一一对应 |
| `custom_components/lipro/core/coordinator/` | 高 | `core/coordinator/coordinator.py`、`orchestrator.py`、`services/protocol_service.py` | 运行面边界最成熟；Phase 27 已移除 external pure forwarders，但 `coordinator.py` 仍是后续 maintainability hotspot |
| `custom_components/lipro/core/protocol/` | 高 | `core/protocol/facade.py`、`contracts.py`、`boundary/*.py` | root / contract / boundary 三层分工清楚 |
| `custom_components/lipro/core/capability/` | 高 | `core/capability/registry.py` | 小而稳，authority 明确 |
| `custom_components/lipro/core/device/` | 中高 | `core/device/device.py`、`state.py`、`device_factory.py` | 动态委托已清理，但 façade leaf surface 仍偏宽 |
| `custom_components/lipro/core/api/` | 中 | `core/api/client.py`、`rest_facade.py`、`request_gateway.py`、`transport_executor.py`、`endpoint_surface.py`、`endpoints/*.py` | collaborator 命名已基本显式化；剩余主要成本集中在 `rest_facade.py` 作为 formal façade 组合根的体量 |
| `custom_components/lipro/core/mqtt/` | 中高 | `core/mqtt/transport.py` | `transport.py` + package no-export 让 concrete transport 的局部家园更直白 |
| `custom_components/lipro/services/` | 中 | `services/execution.py`、`services/registry.py` | 以 helper/support cluster 为主；service-registration formal owner 已收口到 `control/service_registry.py` |
| `custom_components/lipro/entities/` + platform 根文件 | 高 | `entities/base.py`、`helpers/platform.py`、各 platform `async_setup_entry()` | 领域投影关系清楚 |

## 6. Naming Assessment
### 6.1 命名一致且有利于维护的区域
- `coordinator_entry.py`：明确表达“HA runtime home”而不是通用 core export。
- `entry_lifecycle_controller.py`、`service_registry.py`、`runtime_access.py`：文件名与单一职责高度一致。
- `status_fallback.py`、`developer_router_support.py`：能看出 helper home / fallback kernel 身份，没有再伪装正式 surface。
- `core/protocol/boundary/rest_decoder.py`、`mqtt_decoder.py`、`schema_registry.py`：文件名直接对应 boundary 语义。

### 6.2 命名仍带 residual 气味的区域
- `core/api/rest_facade.py`：虽然已明显瘦身，但作为 formal REST façade 组合根仍承载不少 wiring / proxy 语义，单文件阅读成本依然偏高。
- `control/entry_lifecycle_controller.py`：formal home 正确，但 setup/unload/reload arbitration 仍集中在单文件里。
- `headless/boot.py`：命名已经诚实标注 proof-only，但被 `config_flow.py` 复用后，新读者仍需要额外分辨它不是正式 runtime/control 入口。
- `services/execution.py`：名字仍偏泛，但语义已稳定为 service execution facade；真实历史 seam 已在 Phase 5 关闭。

## 7. Maintainability Hotspots
主要维护热点不是目录失控，而是少数热点文件仍偏厚、偏热：
- 体量热点：`custom_components/lipro/core/api/rest_facade.py`、`custom_components/lipro/control/entry_lifecycle_controller.py`、`custom_components/lipro/core/protocol/facade.py`、`custom_components/lipro/core/coordinator/coordinator.py`、`custom_components/lipro/core/coordinator/runtime/device/snapshot.py` 与 `custom_components/lipro/config_flow.py` 仍是主要阅读成本来源。
- 变更热点：`custom_components/lipro/core/coordinator/coordinator.py`、`custom_components/lipro/__init__.py`、`custom_components/lipro/config_flow.py`、`custom_components/lipro/core/api/rest_facade.py`、`docs/developer_architecture.md` 在 git 历史中都是高频触达点，说明它们既重要也脆弱。
- 长函数热点：`Coordinator.__init__()`、`EntryLifecycleController.async_setup_entry()`、`SnapshotBuilder.build_full_snapshot()`、`MqttRuntime.__init__()`、`LiproConfigFlow.async_step_reauth_confirm()` 都已经进入“应持续拆薄”的区间。
- 控制面热点：`custom_components/lipro/control/entry_lifecycle_controller.py` 仍集中承载 setup/unload/reload arbitration；`service_router.py` 已下沉成 public shell + handlers/support。

相对健康、可维护的簇：
- `custom_components/lipro/core/coordinator/services/`
- `custom_components/lipro/core/protocol/boundary/`
- `custom_components/lipro/core/capability/`
- `custom_components/lipro/control/`

## 8. Test Tree As Structural Mirror
`tests/` 的结构是仓库维护性的核心优势：
- `tests/core/` 镜像 `core/**`，覆盖 protocol、runtime、domain、telemetry
- `tests/platforms/` 镜像 HA platform 根文件
- `tests/services/` 镜像 control/service story
- `tests/flows/` 镜像 config flow / options flow
- `tests/meta/` 把 `.planning/baseline/*.md` 与 `.planning/reviews/*.md` 转成可执行守卫
- `tests/fixtures/api_contracts/`、`tests/fixtures/external_boundaries/`、`tests/fixtures/protocol_boundary/`、`tests/fixtures/protocol_replay/` 为 boundary / replay / evidence 提供稳定资产
- `tests/harness/protocol/` 与 `tests/harness/evidence_pack/` 明确位于 assurance plane，不污染生产目录

结构性结论：测试树不是附属物，而是五平面中的 assurance implementation。它既证明目录归属，也防止目录回退。

## 9. Residual Structure Leftovers
从目录结构角度看，仍应视为 active residual 的对象（不含已关闭 seam）：
- `custom_components/lipro/core/api/rest_facade.py` 与 `custom_components/lipro/core/api/endpoints/*.py`：正式归属已经正确，但 façade 体量与 helper forwarding 仍是主要阅读负担
- `custom_components/lipro/control/entry_lifecycle_controller.py`：lifecycle arbitration 已 typed 化，但物理上仍是明显热点文件
- `custom_components/lipro/headless/boot.py`：proof-only bootstrap seam 虽已明确标注 local 身份，但物理上仍在 production tree，需要持续防止被升级成正式入口

这些对象的共同特征是：
- `custom_components/lipro/services/execution.py` 已关闭的 private auth seam 属于历史项：文件仍在，但 residual 已关闭而非 active residual。
- 已被 `.planning/reviews/RESIDUAL_LEDGER.md` 与 `.planning/reviews/KILL_LIST.md` 显式登记
- 仍在正式目录树内部，但不再享有正式 root 身份
- 后续应继续“物理收口”，而不是重新提升语义地位

## 10. Final Verdict
若只看目录：仓库已经具备清晰、稳定、可维护的正式骨架。
若看剩余技术债：问题已经从“结构混乱”转为“少量 legacy naming / hotspot 体量 / proof seam 认知成本尚未完全出清”。

一句话裁决：**`lipro-hass` 的目录结构已进入收尾优化期；真正要继续治理的是 residual 命名与热点文件体量，而不是重建新的层次或再造第二条主干。**
