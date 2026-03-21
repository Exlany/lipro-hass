# Requirements: Lipro-HASS

> Archived milestone snapshots: `.planning/milestones/v1.1-REQUIREMENTS.md`, `.planning/milestones/v1.2-REQUIREMENTS.md`, `.planning/milestones/v1.4-REQUIREMENTS.md`, `.planning/milestones/v1.5-REQUIREMENTS.md`, `.planning/milestones/v1.6-REQUIREMENTS.md`

## Core Requirements

### Protocol Boundary

- [x] **BND-01**: REST/MQTT 边界必须通过正式 decoder family 输出 canonical contract，禁止 raw payload 穿透
- [x] **BND-02**: boundary family 必须拥有 authority inventory、fixture family、drift detection 与 canonical result contract
- [x] **BND-03**: 高漂移 boundary family 必须具备可版本化 schema/decoder 注册点、drift flags 与 authority source

### Architecture Enforcement

- [x] **ENF-01**: architecture guards 必须从 plane/root/surface/authority 规则派生，阻止双主链、compat 回流、raw payload 穿透
- [x] **ENF-02**: enforcement 必须同时支持本地快速校验与 CI fail-fast，不得只在合并末端发现偏航

### Telemetry Export

- [x] **OBS-01**: runtime/protocol 核心信号必须形成正式 exporter，覆盖 auth recovery、MQTT reconnect、command confirmation、refresh latency
- [x] **OBS-02**: diagnostics、system health、exporter 必须共享单一 telemetry truth，并遵循统一 redaction/cardinality policy

### Replay & Operability

- [x] **SIM-01**: protocol replay harness 必须复用正式 façade/decoder 路径，对 REST/MQTT 边界输入进行确定性回放
- [x] **SIM-02**: replay corpus 必须有 authority source、版本戳、drift detection，与现有 fixture/governance 体系对齐

### Governance

- [x] **GOV-06**: v1.1 新增组件、fixtures、guards、exporters 必须同步回写 `FILE_MATRIX / AUTHORITY_MATRIX / VERIFICATION_MATRIX / RESIDUAL_LEDGER`
- [x] **GOV-07**: 每个 v1.1 phase 必须显式给出 delete gate、验收命令与 phase closeout evidence

### AI Debug Evidence Pack

- [x] **AID-01**: 必须能从正式真源（exporter/replay/boundary inventory/governance pointers）pull 导出结构化 evidence pack，供 AI 调试与分析
- [x] **AID-02**: evidence pack 必须遵循统一脱敏策略：凭证等价物永不出现；允许报告内稳定、跨报告不可关联的伪匿名引用；允许真实时间戳

### Residual Surface Closure

- [x] **RSC-01**: `LiproProtocolFacade` 的正式 public surface 必须显式声明；child façade 不得再通过 `__getattr__` / `__dir__` 隐式定义 protocol root contract
- [x] **RSC-02**: concrete transport / compat shell 只能存在于显式 transitional seam；`raw_client` 与根模块 compat exports 不得继续作为正式 public surface 扩散
- [x] **RSC-03**: runtime 对设备集合的正式访问不得暴露 live mutable dict；平台/diagnostics/helpers 必须改走只读 view 或正式 service contract
- [x] **RSC-04**: outlet power 与类似补充状态必须通过正式 primitive 承载，禁止以 `extra_data` 旁写充当正式路径；相关 governance / guards / residual delete gate 必须同步收口

### API Drift Isolation & Core Boundary Prep

- [x] **ISO-01**: `login`、`device_list`、`query_device_status`、`query_mesh_group_status`、OTA/support-critical payload 等高漂移 REST/MQTT 输入必须在 protocol boundary 输出 canonical contract；runtime/domain/control/platform 不得再自行解析 vendor envelope、field alias 或分页形态。
- [x] **ISO-02**: host-neutral auth / session / query-result contracts 必须显式化；`config_flow`、`entry_auth` 与其他 control adapters 只能消费 formal use case / result contract，不得依赖 raw response dict shape。
- [x] **ISO-03**: `core` formal public surface 必须继续与 HA runtime root 解耦；`Coordinator` 保持通过 `coordinator_entry` 暴露，`core/__init__.py` 不得把 HA runtime 当作 host-neutral core truth 的一部分继续输出。
- [x] **ISO-04**: 与 API drift isolation 相关的 roadmap/context/research/validation/verification/governance docs、replay fixtures 与 meta guards 必须同轮更新；未来 CLI / 其他宿主只能建立在 formal boundary 之上，而不是反向长成 second root。


### Control Router Formalization & Wiring Residual Demotion

- [x] **CTRL-01**: `custom_components/lipro/control/service_router.py` 已成为 HA services callback、router wrapper 与 control-facing helper 的唯一正式 home；`custom_components/lipro/services/wiring.py` compat shell 已删除。
- [x] **CTRL-02**: service registrations、developer/public diagnostics handlers 与匿名分享提交路径已经正式 control router 组合；重复 wrapper / helper 逻辑已进一步合并，legacy seam 仅保留显式 compat re-export。
- [x] **CTRL-03**: 与 control router formalization 相关的 tests、ROADMAP/STATE/PROJECT/developer_architecture、FILE_MATRIX/RESIDUAL_LEDGER 等治理资产已同步更新，并关闭 `services/wiring.py` residual/delete gate。
- [x] **SURF-01**: `LiproRestFacade`、runtime refresh path 与 orchestrator wiring 中残留的 dynamic surface、ghost surface 与 compat fallback 必须收敛到显式 formal contract。
- [x] **CTRL-04**: control / services 中 runtime locator、debug-mode gating 与 diagnostics access 必须收敛到统一 formal runtime-access story。
- [x] **RUN-01**: runtime public typing 必须窄化为 public protocol；status executor 必须把 query 失败与单设备 apply 失败分层隔离。
- [x] **ENT-01**: supplemental entity 暴露规则必须收口到单一领域真源，并修复 `switch.py` 的 `hasattr()` 误建模与 unknown-enum 静默 fallback。
- [x] **ENT-02**: `entities/firmware_update.py` 必须拆薄为平台投影层，OTA policy/candidate/cache/arbitration 应进一步下沉到 formal helper cluster。
- [x] **GOV-08**: docs / phase assets / CI / release / issue / PR / security disclosure 必须形成一致的开源项目治理口径，governance guards 尽量结构化。

### Type Contract Alignment, Residual Cleanup & Governance Hygiene

- [x] **TYP-01**: `LiproCoordinator` public protocol、`Coordinator` implementation、platform setup entrypoints 与 diagnostics/entity adapters 已重新对齐到正式 typed runtime surface。
- [x] **TYP-02**: `LiproRestFacade`、typed API service protocols 与 canonical result rows 已在返回类型上完全一致。
- [x] **CMP-01**: remaining explicit compat seams（`core.api.LiproClient`、`LiproProtocolFacade.get_device_list`、`LiproMqttFacade.raw_client`、`DeviceCapabilities`）已从生产 public surface 清退。
- [x] **CMP-02**: `core/api` historical skeleton 已进一步削薄；`_ClientBase` 仅保留 internal typing contract 角色，不再承担 public skeleton 语义。
- [x] **HOT-01**: `core/api/client.py`、`snapshot.py` 与相关 typed/runtime 热点已继续沿 formal boundary 收口，未引入第二 orchestration story。
- [x] **GOV-09**: developer-facing docs / config truth（architecture docs、quality scale、devcontainer、baseline/review truth）已对齐当前实现。
- [x] **GOV-10**: contributor-facing CI/open-source contract 已与真实仓库治理对齐；`security` job、`CODE_OF_CONDUCT.md`、`SUPPORT.md` 与 shell 脚本 lint 门禁均已纳入正式口径。

### Explicit Domain Surface, Governance Guard Hardening & Hotspot Boundary Decomposition

- [x] **DOM-01**: `LiproDevice` 与 `DeviceState` 的正式领域表面必须显式可枚举；设备域不得再依赖 `__getattr__` 动态扩面。
- [x] **DOM-02**: device/domain 内部消费者应优先走 `state` / `network_info` / `extras` / `capabilities` 组合根，避免新的隐式叶子 surface 继续反向定义领域真相。
- [x] **RUN-02**: `core/coordinator/orchestrator.py` 必须拆成更小的 runtime builder helpers，并把内部协议依赖的术语从模糊 `client` 收口到 `protocol`。
- [x] **RUN-03**: `core/api/status_service.py` 的 binary-split fallback 与 batch query 主链必须拆成可审计 helper / context / accumulator 边界，而不是继续堆在单个巨型函数里。
- [x] **GOV-11**: README / README_zh / CONTRIBUTING / SUPPORT / CODEOWNERS / quality-scale / devcontainer 与 meta guards 必须形成结构化、一致、可自动校验的开源治理入口。

### Legacy Stack Final Closure, API Spine Demolition & Governance Truth Consolidation

- [x] **RUN-04**: `Coordinator` 内部正式协议真源必须统一命名为 `protocol`，protocol-facing runtime ops 通过 `CoordinatorProtocolService` 收口，不再保留 `Coordinator.client` 合法故事线。
- [x] **HOT-02**: `core/api` 的 schedule residual 必须完成 closeout：`ScheduleApiService` 与 `LiproRestFacade` 尾部 schedule passthrough 退出正式故事线，schedule truth 固定为 `ScheduleEndpoints` + focused helpers。
- [x] **CTRL-05**: `control/service_router.py` 必须保留 public handler home 身份，但 developer report / optional capability / sensor-history 私有 glue 要下沉到 focused helper home。
- [x] **RUN-05**: `core/api/status_service.py` 的 binary-split fallback kernel 必须迁入可审计 helper module，public orchestration 行为保持不变。
- [x] **GOV-12**: subordinate docs、file/review ledgers、architecture policy 与 meta guards 必须同步到 Phase 14 真相，并显式锁定 `_ClientBase` / helper mixin family、`LiproMqttClient` residual ownership 与 assurance-only backflow ban。


### Support Feedback, Governance Truth & Maintainability Follow-Through

- [x] **SPT-01**: developer feedback 上传契约必须明确区分供应商诊断标识与用户自定义标签：`iotName` 等设备判型真源保持可用，`deviceName` / room labels / panel key labels / IR asset display names 等用户自定义名称必须匿名化或改写为非识别性表示，且 docs / fixtures / tests 同步锁定该裁决。
- [x] **GOV-13**: active governance docs 不得再引用不存在的 source path；phase/status/date/footer/authority wording 必须保持自洽，并由脚本或 meta guards fail-fast 校验。
- [x] **DOC-01**: README / README_zh / CONTRIBUTING / SUPPORT / CI / version metadata 必须对最低支持的 Home Assistant 版本与 HACS private-repo caveat 保持一致。
- [x] **HOT-03**: `control/service_router.py`、developer report 与 developer feedback upload 相关热点必须继续拆薄；public handler home、local debug view 与 upload payload shaping 必须明确分层。
- [x] **QLT-01**: 本轮审阅确认的 testing/tooling/security gap 必须转成明确结论：marker registry 要么真实落地要么删除，coverage diff 必须有 baseline 语义或更名澄清，benchmark/dev-audit policy 必须写成可执行 gate 或显式 documented arbitration。
- [x] **TYP-03**: `control/runtime_access.py` 与相邻 control seams 中可收窄的 `Any` / 宽口 host-side typing 必须继续向 formal runtime contracts 收口。
- [x] **RES-01**: `core/api/client_*` helper spine、`LiproMqttClient` legacy naming 与已登记 residuals 必须继续本地化、加固 guard 或缩窄 delete gate，不得重新回流为正式 surface。

### Post-Audit Truth Alignment, Hotspot Decomposition & Residual Endgame

- [x] **GOV-14**: `AGENTS.md`、`PROJECT.md`、`ROADMAP.md`、`STATE.md`、baseline/review docs 与 `.planning/codebase/*` policy 必须重新对齐到 Phase 16 规划真相，不得继续把已关闭 seam 或过期 codebase map 当成活跃裁决来源；Phase 16 closeout 不允许留下无 owner / 无 delete gate / 无风险说明的高风险 carry-forward。
- [x] **QLT-02**: Python / Ruff / pre-commit / devcontainer / pytest marker truth 必须一致：运行时、类型检查与 lint 目标版本不能漂移，名存实亡的 marker / tooling contract 必须落地或删除；本地 DX 与 closeout 质量门禁必须把这套真相可执行化。
- [x] **HOT-04**: `core/api/client.py`、`core/protocol/facade.py`、`core/coordinator/coordinator.py`、`control/service_router.py`、`config_flow.py`、`entities/firmware_update.py` 及其 second-pass 发现的 secondary hotspots（如 entry-lifecycle / diagnostics / telemetry / request-policy / status-fallback / mqtt-runtime / rest-decoder 等）必须继续沿正式边界拆薄，避免 façade/root 与其紧邻协作者继续承载 strategy、shape normalization、exception mapping 与 glue 内核。
- [x] **TYP-04**: `core/api`、`core/protocol`、`control` 与相邻 residual seams 中的 `Any` / `type: ignore` / `cast` / `getattr` / `import_module` 等宽口必须进一步收窄到 `Protocol`、typed alias、`TypedDict` 或明确 contract，不得仅靠技术性掩饰继续掩盖边界漂移。
- [x] **ERR-01**: protocol/runtime/control/support 关键链路中的 catch-all 异常必须收窄或显式写成 documented arbitration，日志、重试与 reauth 语义必须可判定；entry-lifecycle、diagnostics/telemetry、mqtt-runtime、firmware-update 与相邻 glue seams 不得继续保留 undocumented broad-catch。
- [x] **RES-02**: `_ClientBase` / `_Client*Mixin`、endpoint mixin exports、`LiproMqttClient` legacy naming、`get_auth_data()` fallback 与 helper-level compat envelope 已被缩窄到可审计范围，并在 Phase 17 完成最终 physical retirement / truthful disposition，不再制造旧 root / old client 仍合法的错觉。
- [x] **CTRL-06**: `send_command`、share/developer-report、entry lifecycle、diagnostics/telemetry、maintenance/device-lookup、runtime access 与相关 response schema 必须统一到更清晰的 formal control/runtime contract：auth/error 主链一致、service payload shape 稳定、动态导入/反射式探测继续下降。
- [x] **DOM-03**: `LiproDevice`、`CapabilitySnapshot`、entity descriptors 与平台能力消费协议必须进一步收口到单一领域真源；死接口、重复透传属性与双轨 capability 语义不得继续扩散。
- [x] **OTA-01**: firmware update entity 必须回到 projection + action bridge 身份；manifest 读取、row arbitration、cache/hot-path I/O 与 install policy 应进一步下沉到更合适的 service/helper home。
- [x] **TST-01**: platform/domain test layering 必须纠偏：平台测试优先验证真实 entity adapter，领域测试验证 device/capability semantics，OTA 策略测试不再长期停留在 platform test home。
- [x] **DOC-02**: troubleshooting、contributor navigation、maintainer release runbook 与 `scripts/develop` 等本地 DX 入口必须与高治理仓库的真实维护路径对齐，降低新贡献者与单维护者的操作负担；Phase 16 closeout 还必须给出 second-pass re-audit 与 residual closeout story。

### Final Residual Retirement, Typed-Contract Tightening & Milestone Closeout

- [x] **RES-03**: `_ClientTransportMixin`、`_ClientBase` skeleton、`_ClientEndpointPayloadsMixin` 与 endpoint legacy mixin family 已完成 physical retirement：formal REST path 现只通过 explicit collaborator composition + local typed ports 表达。
- [x] **TYP-05**: `persist_entry_tokens_if_changed()` 与 outlet-power helper contract 已收口到显式 typed truth：`AuthSessionSnapshot` 是 token persistence 的唯一正式契约，`power_service.py` 只返回 explicit row/list contract，不再输出 synthetic compat envelope。
- [x] **MQT-01**: MQTT concrete transport 的 legacy naming 与 locality 已完成 demote：production code 与非 transport-focused tests 已切到 canonical transport naming / `MqttTransportFacade` contract，并由 focused meta guard 与 no-export bans fail-fast 锁定 `ENF-IMP-MQTT-TRANSPORT-LOCALITY`。
- [x] **GOV-15**: `Phase 17` closeout 已把 `ROADMAP`、`REQUIREMENTS`、`STATE`、baseline/review ledgers、`v1.1` milestone audit 与最终 repo audit counts/evidence 完整回写；不存在新的 silent defer 或 authority drift。

## Cross-Phase Arbitration

- `07.3` 锁定 telemetry contracts / redaction / cardinality / timestamp-pseudo-id compatibility
- `07.4` 锁定 replay manifests / deterministic driver / replay assertions / run summary
- `07.5` 锁定 governance matrices / evidence index / residual / delete gates
- `08` 锁定 AI debug packaging / exporter entrypoint / pack schema
- `09` 锁定 residual surface closure / compat seam narrowing / read-only runtime access / formal outlet-power primitive
- `10` 锁定 API drift isolation / core-boundary prep / host-neutral contracts；不得把跨平台 SDK 抽离提升为本里程碑正式 root
- `12` 锁定 type contract convergence / compat narrowing / hotspot slimming / contributor-facing governance hygiene；不得重新打开已在 Phase 11 关闭的 residual truth
- `13` 锁定显式设备域表面、runtime/status 热点 helper 边界与公开治理资产结构化守卫；后续 closeout 不得重新引入 device/state 动态委托
- `14` 锁定 legacy stack final closure、API spine demolition、helper-home extraction 与 governance truth consolidation；后续 milestone audit 不得再把 `Coordinator.client`、`ScheduleApiService` 或 helper-home modules 回流成正式 surface
- `15` 锁定 developer feedback contract、governance truth repair、contributor/install docs sync、support hotspot follow-through 与 testing/tooling gate clarification；不得因修补支持面问题而重开第二条正式主链
- `16` 锁定 post-audit truth alignment、hotspot decomposition、type/exception tightening、residual endgame、domain/entity/OTA rationalization 与 contributor DX follow-through；不得因为收尾改进而重开第二条正式主链、第二套 protocol/runtime story 或无 gate rename campaign

## Future Requirements

- **OBS-05**: 如需要外部监控对接，再评估 Prometheus / OpenTelemetry sink
- **BND-04**: 如 manual validators 成本继续升高，再裁决局部 `pydantic v2` backend
- **ENF-03**: 如 AST/meta guards 复杂度继续上升，再评估 `import-linter/grimp`
- **SIM-06**: 如需要更强双向仿真，再补 broker/cloud behavioral simulator
- **AID-03**: 如 evidence pack 编码/校验成本成为瓶颈，再单独裁决 encoding backend，而不是提前绑定 `msgspec` / `pydantic v2`


## Out of Scope

| Feature | Reason |
|---------|--------|
| 全域 schema 框架替换 | 违背“边界局部增强”原则 |
| 第二套 protocol/runtime 实现 | 会破坏单一正式主链 |
| 外部监控平台接入 | 当前重点是 exporter formalization，不是 observability productization |
| 与北极星口径无关的大规模换栈 | 收益不直接指向当前里程碑目标 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BND-01 | Phase 7.1 | Complete |
| BND-02 | Phase 7.1 | Complete |
| BND-03 | Phase 7.1 | Complete |
| ENF-01 | Phase 7.2 | Complete |
| ENF-02 | Phase 7.2 | Complete |
| OBS-01 | Phase 7.3 | Complete |
| OBS-02 | Phase 7.3 | Complete |
| SIM-01 | Phase 7.4 | Complete |
| SIM-02 | Phase 7.4 | Complete |
| GOV-06 | Phase 7.5 | Complete |
| GOV-07 | Phase 7.5 | Complete |
| AID-01 | Phase 8 | Complete |
| AID-02 | Phase 8 | Complete |
| RSC-01 | Phase 9 | Complete |
| RSC-02 | Phase 9 | Complete |
| RSC-03 | Phase 9 | Complete |
| RSC-04 | Phase 9 | Complete |
| ISO-01 | Phase 10 | Complete |
| ISO-02 | Phase 10 | Complete |
| ISO-03 | Phase 10 | Complete |
| ISO-04 | Phase 10 | Complete |
| CTRL-01 | Phase 11 | Complete |
| CTRL-02 | Phase 11 | Complete |
| CTRL-03 | Phase 11 | Complete |
| SURF-01 | Phase 11 | Complete |
| CTRL-04 | Phase 11 | Complete |
| RUN-01 | Phase 11 | Complete |
| ENT-01 | Phase 11 | Complete |
| ENT-02 | Phase 11 | Complete |
| GOV-08 | Phase 11 | Complete |

| TYP-01 | Phase 12 | Complete |
| TYP-02 | Phase 12 | Complete |
| CMP-01 | Phase 12 | Complete |
| CMP-02 | Phase 12 | Complete |
| HOT-01 | Phase 12 | Complete |
| GOV-09 | Phase 12 | Complete |
| GOV-10 | Phase 12 | Complete |
| DOM-01 | Phase 13 | Complete |
| DOM-02 | Phase 13 | Complete |
| RUN-02 | Phase 13 | Complete |
| RUN-03 | Phase 13 | Complete |
| GOV-11 | Phase 13 | Complete |
| RUN-04 | Phase 14 | Complete |
| HOT-02 | Phase 14 | Complete |
| CTRL-05 | Phase 14 | Complete |
| RUN-05 | Phase 14 | Complete |
| GOV-12 | Phase 14 | Complete |

| SPT-01 | Phase 15 | Complete |
| GOV-13 | Phase 15 | Complete |
| DOC-01 | Phase 15 | Complete |
| HOT-03 | Phase 15 | Complete |
| QLT-01 | Phase 15 | Complete |
| TYP-03 | Phase 15 | Complete |
| RES-01 | Phase 15 | Complete |
| GOV-14 | Phase 16 | Complete |
| RES-03 | Phase 17 | Complete |
| TYP-05 | Phase 17 | Complete |
| MQT-01 | Phase 17 | Complete |
| GOV-15 | Phase 17 | Complete |
| QLT-02 | Phase 16 | Complete |
| HOT-04 | Phase 16 | Complete |
| TYP-04 | Phase 16 | Complete |
| ERR-01 | Phase 16 | Complete |
| RES-02 | Phase 16 | Complete |
| CTRL-06 | Phase 16 | Complete |
| DOM-03 | Phase 16 | Complete |
| OTA-01 | Phase 16 | Complete |
| TST-01 | Phase 16 | Complete |
| DOC-02 | Phase 16 | Complete |

**Coverage:**
- active milestone requirements: 65 total
- mapped to phases: 65
- unmapped: 0 ✓

*Last updated: 2026-03-21 after completing Phase 52 protocol-root/request-policy closeout and promoting the current v1.8 truth*


## Archived Milestone (v1.2)

> `v1.2` 已完成全部执行与 closeout；以下 requirement / traceability 反映 `Phase 18-24` 全部完成，且 `Phase 24` 已在 2026-03-17 reopen revalidation 后继续保持 archive-ready / handoff-ready。归档快照已写入 `.planning/milestones/v1.2-REQUIREMENTS.md`。

### Core Reuse / Host-Neutral Nucleus

- [x] **CORE-01**: boundary/auth/device 的共享 nucleus 可在不依赖 HA entry/runtime adapter 类型的前提下独立组合。
- [x] **CORE-02**: 同一套 nucleus 必须能被 headless / CLI-style consumer 复用，完成认证、设备发现与 replay/evidence proof。
- [x] **CORE-03**: HA adapter 只能保留 adapter 身份，不得继续把 host-specific wiring 泄露回共享 nucleus。

### Replay / Boundary Completion

- [x] **SIM-03**: `rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 已成为 registry-backed boundary families。
- [x] **SIM-04**: replay harness 与 evidence pack 已覆盖新增 formalized families，并复用同一正式 public path。
- [x] **SIM-05**: 当前 authority/inventory 中对 remaining replay families 的 de-scope / partial 标记，已随 coverage 落地被移除或缩窄为真实剩余项。

### Error / Observability Hardening

- [x] **ERR-02**: protocol/runtime/control 关键 broad-catch 已被收窄或改成 documented arbitration，catch-all 不再作为默认策略。
- [x] **OBS-03**: diagnostics / system health / evidence export 已对 auth/network/protocol/runtime failure 使用统一分类语言。

### Governance

- [x] **GOV-16**: v1.2 的 host-neutral / replay-complete / observability-hardening 真相已同步到 roadmap / state / baseline / reviews / docs / meta guards。
- [x] **GOV-17**: contributor-facing docs、issue/PR templates、support/security/install/version surfaces 与 release evidence 已对齐最终 v1.2 架构与治理门禁。
- [x] **GOV-18**: milestone closeout 已留下 final repo audit、residual arbitration、archive-ready verification assets 与 v1.3 handoff，且在 2026-03-17 reopened gates 后重新验证，无 silent defer。

## Traceability for v1.2

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| CORE-01 | Phase 18 | Complete |
| CORE-02 | Phase 19 | Complete |
| CORE-03 | Phase 18 | Complete |
| SIM-03 | Phase 20 | Complete |
| SIM-04 | Phase 21 | Complete |
| SIM-05 | Phase 20 | Complete |
| ERR-02 | Phase 21 | Complete |
| OBS-03 | Phase 22 | Complete |
| GOV-16 | Phase 23 | Complete |
| GOV-17 | Phase 23 | Complete |
| GOV-18 | Phase 24 | Complete |

**Current Coverage:**
- v1.2 requirements: 11 total
- Current mapped: 11
- Current complete: 101 ✓
- Current unmapped: 0 ✓

## Next Milestone Seed (v1.3)

> `Phase 25` 已被提升为 v1.3 的总计划母相：它先冻结 `25.1 / 25.2 / 26 / 27` 首轮路由，再由 `28 / 29 / 30 / 31` 完成第二梯队 closeout；`Phase 32 / 33` 已于 `2026-03-18` 完成 final truth-convergence + hardening closeout。当前 `.planning/v1.3-MILESTONE-AUDIT.md` 已刷新为 `tech_debt / closeout-eligible`；若继续追求 10 分质量，下一步优先 `$gsd-plan-milestone-gaps`，否则可 `$gsd-complete-milestone v1.3`。

### Governance / Route Ownership

- [x] **GOV-19**: 终极复审中的全部 P0 / P1 / P2 问题必须被显式路由到 `25.1 / 25.2 / 26 / 27` 或被裁决为外部协议约束 / 非当前 debt；禁止 silent defer。
- [x] **GOV-20**: telemetry seam closure 触及的 authority docs、residual ledgers、handoff truth 与 touched `.planning/codebase/*` derived maps 必须同步，明确 formal surface 迁移且 derived maps 继续只是协作图谱。
- [x] **GOV-21**: release/install trust chain、support matrix、双语策略、维护者冗余与 contributor-facing productization surfaces 必须达到更成熟的开源治理标准。

### Runtime / Observability Correctness

- [x] **RUN-06**: 全量设备快照刷新必须满足原子性；分页失败、拓扑 enrich 失败或 parse failure 不得静默发布 partial truth 覆盖既有运行态。
- [x] **ERR-03**: refresh failure 必须具备可判定 arbitration；`拒绝提交 / 保留 last-known-good / 结构化 degraded` 三者必须显式、可测且语义稳定。
- [x] **OBS-04**: telemetry / diagnostics / system health consumer 只能通过正式 protocol telemetry surface 或显式 port 拉取协议信号，不得继续依赖 `Coordinator.client`、隐式属性或 ghost seam。

### Productization / Maintainability Follow-Through

- [x] **QLT-03**: 依赖、兼容、支持窗口与升级策略必须更诚实、更可复现，并与 release / support surfaces 保持一致。
- [x] **HOT-05**: `Coordinator`、`LiproRestFacade` 与纯转发层必须继续沿正式边界切薄，不得再用“只是转发”合理化巨型根对象。
- [x] **RES-04**: 过渡命名、历史 phase 叙事、残留噪声与协议受限实现说明必须更诚实；reverse-engineered vendor `MD5` 登录哈希路径被记录为协议约束，而不是仓库弱密码学债。
- [x] **TST-02**: 巨型测试文件与贡献者高认知负担测试面必须继续拆分成稳定、可局部执行的专题套件，同时保留现有治理门禁强度。
- [x] **GOV-22**: maintainer continuity、emergency access、support window / EOL / triage ownership 必须从“诚实说明”升级为制度化、可审计的运维/治理资产，且不虚构额外维护者。
- [x] **QLT-04**: release identity posture 必须进一步硬化；signing、code-scanning gate 或等价 machine-enforced release security controls 必须形成一致 story。
- [x] **HOT-06**: `LiproRestFacade` remaining hotspot 必须继续拆成更聚焦的 child collaborators / services，不得保留巨型 child façade 作为长期合法形态。
- [x] **RES-05**: 与 `LiproRestFacade` / protocol child-collaborator decomposition 相关的命名、职责与 residual truth 必须继续收口并诚实同步。
- [x] **TST-03**: remaining mega-test suites 必须继续专题化拆分，并保持局部可执行与治理门禁强度。
- [x] **TYP-06**: 高价值 `core/api` / `core/protocol` / `control` hotspots 的 `Any` / `type: ignore` 必须继续沿正式 contract 收窄，不得长期停留在 boundary-adjacent distributed backlog。
- [x] **ERR-04**: remaining broad-catch paths in touched protocol/control hotspots 必须改成 typed arbitration、documented failure contract 或显式 deferred truth。
- [x] **TYP-07**: runtime/service/platform touched zones 的 `Any` / `type: ignore` backlog 必须建立预算、继续下降，并形成 no-growth typed hardening story。
- [x] **ERR-05**: remaining runtime/service broad-catch paths 必须收敛为 documented fail-closed / degraded semantics 或被移除；新增 catch-all regression 必须被 guard 阻断。
- [x] **GOV-23**: typed/exception budget、phase closeout assets 与 daily governance gates 必须机器化守护 `30/31` 的 no-growth contract，而不是依赖人工补漏。
- [x] **GOV-24**: `.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md` 与 retained handoff/audit pointers 已对 `Phase 25 -> 32` complete 讲同一条 current story，不再分叉。
- [x] **QLT-05**: repo-wide `ruff` / `mypy` / CI / contributor docs gate story 已诚实且 machine-checkable；工具范围、blocking truth 与 release posture 均已被文档和 guards 显式固定。
- [x] **GOV-25**: release identity posture、code-scanning / signing defer truth、maintainer continuity、support/security process 与 contributor-facing templates 已收敛成单一、诚实、可审计的治理故事。
- [x] **GOV-26**: `.planning/codebase/*.md` 与双语 public docs 现已带 freshness / disclaimer / authority-boundary truth，并与 baseline/review docs 同步。
- [x] **HOT-07**: touched runtime/platform/governance hotspots 已继续沿现有正式 seams 收口，helper/platform/runtime typing 不再并行生长第二 coordinator 故事。
- [x] **TST-04**: touched replay/runtime/governance suites 已继续按契约与守卫专题化收口，并保持局部可执行性与守卫强度。
- [x] **TYP-08**: 高价值 touched hotspots 的 typed debt 已进一步 burn-down，并通过 repo-wide `mypy` / Phase 31 budget guard 区分 sanctioned truth 与 backlog truth。
- [x] **ERR-06**: touched hotspots 的 broad-catch / catch-all truth 已继续收敛为 named arbitration、documented semantics 或 explicit defer truth，并由 guard 固化。
- [x] **RES-06**: fallback / legacy / phase residue 与 protocol-constrained crypto wording 已被继续清理或显式文档化，不再依赖口头约定。

## Traceability for v1.3 route map

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-19 | Phase 25 | Complete |
| RUN-06 | Phase 25.1 | Complete |
| ERR-03 | Phase 25.1 | Complete |
| OBS-04 | Phase 25.2 | Complete |
| GOV-20 | Phase 25.2 | Complete |
| GOV-21 | Phase 26 | Complete |
| QLT-03 | Phase 26 | Complete |
| HOT-05 | Phase 27 | Complete |
| RES-04 | Phase 27 | Complete |
| TST-02 | Phase 27 | Complete |
| GOV-22 | Phase 28 | Complete |
| QLT-04 | Phase 28 | Complete |
| HOT-06 | Phase 29 | Complete |
| RES-05 | Phase 29 | Complete |
| TST-03 | Phase 29 | Complete |
| TYP-06 | Phase 30 | Complete |
| ERR-04 | Phase 30 | Complete |
| TYP-07 | Phase 31 | Complete |
| ERR-05 | Phase 31 | Complete |
| GOV-23 | Phase 31 | Complete |
| GOV-24 | Phase 32 | Complete |
| QLT-05 | Phase 32 | Complete |
| GOV-25 | Phase 32 | Complete |
| GOV-26 | Phase 32 | Complete |
| HOT-07 | Phase 32 | Complete |
| TST-04 | Phase 32 | Complete |
| TYP-08 | Phase 32 | Complete |
| ERR-06 | Phase 32 | Complete |
| RES-06 | Phase 32 | Complete |

**Seed Coverage:**
- v1.3 routed requirements: 29 total
- Current mapped: 29
- Current complete: 29
- Current pending: 0
- Current unmapped: 0 ✓

## Audit-Driven Continuation Seed (Phase 33)

> `Phase 25 -> 32` 已把 correctness、telemetry seam、truth convergence 与 release honesty 推到高位；`2026-03-18` 的全仓终审仍确认存在一簇剩余 P1/P2 debt。`Phase 33` 把这些问题全部正式路由成下一轮可执行 tranche，而不是继续停留在终审备忘里。

### Architecture / Control Truth

- [x] **ARC-03**: runtime public surface 必须只有一份正式类型真源；HA 顶层 adapter 可以 import / alias，但不得继续自定义第二份 `LiproRuntimeCoordinator` 契约。
- [x] **CTRL-07**: control-plane telemetry / runtime-access / support read-model 必须改成 acyclic、port-based 边界；`RuntimeCoordinatorSnapshot` 必须变成纯 DTO，不再携带活体 runtime root。

### Hotspots / Quality Gates

- [x] **HOT-08**: giant runtime/protocol/helper hotspots 必须继续沿现有正式 seams 切薄；`LiproRestFacade`、`LiproProtocolFacade`、`Coordinator`、`SnapshotBuilder`、`CommandResult` family 不得被长期合法化为 forwarding roots。
- [x] **ERR-07**: remaining broad-catch paths 必须收敛到 named arbitration、documented degraded semantics 或 fail-closed contract；新增 catch-all regression 必须被 no-growth guards 拦截。
- [x] **QLT-06**: local / CI / release / benchmark gates 必须收敛到 machine-checkable truth；snapshot duplicate execution、local late feedback 与 performance advisory-only posture 必须被修正。
- [x] **QLT-07**: dependency / compatibility posture 必须更可复现、更显式；runtime dependency bounds、Python floor、support window 与 release posture 必须讲同一条故事。

### Governance / Productization / Testing

- [x] **GOV-27**: control public exports、empty compat shells、legacy/mixin naming residue 与 internal helper exposure 必须缩面或重分类，不能继续暗示第二条 public story。
- [x] **GOV-28**: 深层 public docs 必须朝 bilingual parity、support/security continuity 与 maintainer custody honesty 再推进一轮；`signing` / `code scanning` / release custody 仍须显式、非虚构。
- [x] **TST-05**: remaining giant test suites 必须继续 topicize 成更稳定、可局部执行的专题面，同时保持治理门禁强度与回归信号。

## Traceability for Phase 33 continuation

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| ARC-03 | Phase 33 | Complete |
| CTRL-07 | Phase 33 | Complete |
| HOT-08 | Phase 33 | Complete |
| ERR-07 | Phase 33 | Complete |
| TST-05 | Phase 33 | Complete |
| QLT-06 | Phase 33 | Complete |
| GOV-27 | Phase 33 | Complete |
| GOV-28 | Phase 33 | Complete |
| QLT-07 | Phase 33 | Complete |

**Seed Coverage:**
- Phase 33 routed requirements: 9 total
- Current mapped: 9
- Current complete: 9
- Current pending: 0
- Current unmapped: 0 ✓



## Planned Milestone (v1.8)

> `v1.8` 以 `v1.6` archive truth 为 shipped baseline，以 `v1.7` promoted audit/closeout evidence 为 immediate route seed；当前重点是 continuity automation、formal-root sustainment 与 hotspot round 2，而不是重开 `v1.7`。

### Operational Continuity Automation, Formal-Root Sustainment & Hotspot Round 2

- [x] **GOV-38**: maintainer-unavailable / delegate / custody / freeze / restoration drill 已从 prose agreement 升级为可执行、低摩擦、可重复演练的 continuity contract。
- [x] **GOV-39**: `.planning/baseline/GOVERNANCE_REGISTRY.json` 已进一步承担下游 maintainer/public metadata projection truth，降低 docs / templates / contributor guidance 的手工同步漂移。
- [x] **QLT-18**: release chain 已支持 verify-only / non-publish rehearsal，并为 docs-only / governance-only / release-only 等 change type 提供最小充分验证矩阵。
- [x] **ARC-08**: `LiproProtocolFacade` 已继续 inward decomposition，并保持其作为唯一 protocol-plane root 的正式身份不变。
- [x] **HOT-12**: `Coordinator`、`__init__.py` 与 `EntryLifecycleController` 必须继续沿现有 seams 限流，降低 orchestration density。
- [x] **HOT-13**: `AnonymousShareManager`、diagnostics API helper family 与 request-policy companions 必须继续切薄，而不新增 public wrapper / helper-owned truth。
- [x] **TST-10**: second-wave mega-tests 必须继续按 concern topicize，让 API/MQTT/platform 大套件失败直接命中局部语义。
- [x] **TYP-13**: repo-wide typing truth 必须区分 production debt 与 test/guard literal debt，并继续压缩非 REST 区域的 `Any` 集中区。

## Traceability for completed v1.8 route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-38 | Phase 51 | Complete |
| GOV-39 | Phase 51 | Complete |
| QLT-18 | Phase 51 | Complete |
| ARC-08 | Phase 52 | Complete |
| HOT-12 | Phase 53 | Complete |
| HOT-13 | Phase 54 | Complete |
| TST-10 | Phase 55 | Complete |
| TYP-13 | Phase 55 | Complete |

**Coverage:**
- v1.8 routed requirements: 8 total
- Current mapped: 8
- Current complete: 8
- Current pending: 0
- Current unmapped: 0 ✓

## Completed Milestone (v1.7)

> `v1.7` 以 `v1.6` archive truth 为 shipped baseline；`Phase 46` 完成了 repo-wide 审阅，`Phase 47 -> 50` 则把 high-value follow-up route 全部正式落地并收束为 promoted closeout evidence。

### Full-Spectrum Repository Audit, Open-Source Maturity & Remediation Routing

- [x] **GOV-36**: 所有 Python 代码、测试、文档、配置、工作流与 `.planning` 治理真源都必须进入可追溯的 file-level 审阅范围，不能留下未被定性的盲区。
- [x] **ARC-05**: formal roots、public surfaces、dependency direction、control/runtime/protocol/service ownership 与 hotspot seams 必须按北极星架构与优秀开源案例完成系统审阅，并给出 keep / split / forbid / defer 裁决。
- [x] **DOC-05**: 开源项目入口、README/README_zh、CONTRIBUTING、SUPPORT、SECURITY、runbook、issue/PR templates 与 bilingual boundary 必须完成国际化可维护性审阅，明确 strengths、gaps 与改进优先级。
- [x] **RES-12**: 重构后的代码与老旧术语/旧残留风险必须被重新盘点，明确哪些是历史遗留、哪些是 future sustainment debt、哪些必须在后续 phase 物理清退。
- [x] **TST-08**: 巨石测试、验证拓扑、回归半径与失败定位体验必须完成 repo-wide 审阅，并输出下一轮 topicization / contract-hardening 路线。
- [x] **TYP-11**: `Any`、`type: ignore`、broad exception、typed budget 守卫覆盖范围与异常语义一致性必须完成量化盘点，并形成后续 no-growth / reduction 策略。
- [x] **QLT-16**: 必须形成机器可审计的终极审阅报告、评分矩阵、优先级排序与 `Phase 47+` remediation roadmap，使质量改进可以被持续执行与验证。

## Traceability for completed v1.7 audit route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-36 | Phase 46 | Complete |
| ARC-05 | Phase 46 | Complete |
| DOC-05 | Phase 46 | Complete |
| RES-12 | Phase 46 | Complete |
| TST-08 | Phase 46 | Complete |
| TYP-11 | Phase 46 | Complete |
| QLT-16 | Phase 46 | Complete |

**Coverage:**
- v1.7 routed requirements: 7 total
- Current mapped: 7
- Current complete: 7
- Current pending: 0
- Current unmapped: 0 ✓

## Formalized follow-up route from Phase 46

- [x] **GOV-37**: `SUPPORT.md`、`SECURITY.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.github/CODEOWNERS`、issue/PR templates 与 `.planning/baseline/GOVERNANCE_REGISTRY.json` 必须对 continuity / custody / delegate / freeze / restoration 讲同一条单维护者合同故事线。
- [x] **DOC-06**: `docs/README.md` 与 package metadata 必须把 documentation index 暴露成对外正式入口；public fast path、maintainer appendix 与双语边界不得继续视觉混层。
- [x] **RUN-08**: `RuntimeAccess` 必须继续按 projection / telemetry / system-health concern 拆薄；control consumers 不得恢复对 `entry.runtime_data` 或 coordinator internals 的散点读取。
- [x] **ARC-06**: `Coordinator`、`__init__.py` 与 `EntryLifecycleController` 必须继续 inward decomposition，降低 hotspot density，同时保持 lazy wiring 与单一正式主链。
- [x] **TST-09**: 治理 megaguards、runtime-root megatests 与 platform megatests 必须按 concern topicize，减少 giant-file failure triage 成本。
- [x] **QLT-17**: 测试与治理守卫的 failure localization 必须直接标出 phase / doc / token / runtime facet，避免“一个断言管全仓”的模糊失败面。
- [x] **TYP-12**: REST child façade family 的 `Any` / typed helper budget 必须继续收紧，并把 sanctioned-vs-backlog debt 分类压缩到更小、更诚实的边界。
- [x] **ARC-07**: command/result policy 与 diagnostics auth-error duplication 必须收敛到单一 formal home，不得让 ownership drift 继续散落在 helper / service / API family 之间。

## Traceability for formalized v1.7 follow-up route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-37 | Phase 47 | Complete |
| DOC-06 | Phase 47 | Complete |
| RUN-08 | Phase 48 | Complete |
| ARC-06 | Phase 48 | Complete |
| TST-09 | Phase 49 | Complete |
| QLT-17 | Phase 49 | Complete |
| TYP-12 | Phase 50 | Complete |
| ARC-07 | Phase 50 | Complete |

**Follow-up coverage:**
- formalized requirements: 8 total
- Current mapped: 8
- Current complete: 8
- Current pending: 0
- Current unmapped: 0 ✓

## Archived Milestone (v1.6)

> `v1.6` 已于 `2026-03-20` 完成归档；以下 requirements / traceability 保留 `Phase 42 -> 45` 的最终 fulfilled contract，归档快照见 `.planning/milestones/v1.6-REQUIREMENTS.md`，审计裁决见 `.planning/v1.6-MILESTONE-AUDIT.md`，证据入口见 `.planning/reviews/V1_6_EVIDENCE_INDEX.md`。

### Delivery Trust, Boundary Decoupling & Maintainability Closure

- [x] **GOV-34**: maintainer delegate、security fallback、`.github/CODEOWNERS`、issue/PR templates 与 maintainer runbook 必须形成单一 continuity truth，不能继续依赖单点隐性记忆。
- [x] **QLT-12**: release workflow 必须对发布产物运行 install / uninstall smoke，验证 release asset 在临时 HA 目录中的真实可用性。
- [x] **QLT-13**: 质量门禁必须同时约束 total coverage 与 changed-surface diff coverage，并保持 local/CI 命令语义一致。
- [x] **QLT-14**: 必须引入 scheduled compatibility / deprecation preview lane，提前暴露 Home Assistant 或依赖漂移。
- [x] **ARC-04**: `control/` 与 `services/` 必须收敛为单向依赖合同，禁止 helper / runtime / locator 双向缠绕回流。
- [x] **CTRL-10**: runtime infra 与 service helper 的 formal home 必须明确；`services/maintenance.py` 不得继续承载 runtime truth。
- [x] **RUN-07**: `RuntimeAccess` 必须提供 typed public read-model API；生产消费者不得依赖反射、`MagicMock` 形状或私有字段。
- [x] **GOV-35**: `.planning/phases/**` 默认仅是 execution trace；只有 promoted allowlist 资产可进入长期治理 / CI truth。
- [x] **RES-11**: `client / mixin / forwarding` 等旧术语必须退出 current docs、ADR 与注释，只允许留在历史资产或 residual ledger。
- [x] **DOC-04**: contributor fast-path、maintainer appendix 与双语边界策略必须显式化、可链接、可守卫。
- [x] **HOT-11**: 高复杂度热点文件与长函数必须沿现有正式 seams 切薄，且不得扩张 public surface。
- [x] **ERR-11**: 布尔失败返回必须升级为 typed result / reason code，并可被 diagnostics / share / message 路径消费。
- [x] **TYP-10**: runtime / diagnostics / share / message touched-zone 的 typed budget 必须继续收紧，并设 no-growth guard。
- [x] **QLT-15**: benchmark 必须从“留证据”升级为“防回退”门禁，具备基线比较与阈值告警。

## Traceability for archived v1.6 route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-34 | Phase 42 | Completed |
| QLT-12 | Phase 42 | Completed |
| QLT-13 | Phase 42 | Completed |
| QLT-14 | Phase 42 | Completed |
| ARC-04 | Phase 43 | Completed |
| CTRL-10 | Phase 43 | Completed |
| RUN-07 | Phase 43 | Completed |
| GOV-35 | Phase 44 | Completed |
| RES-11 | Phase 44 | Completed |
| DOC-04 | Phase 44 | Completed |
| HOT-11 | Phase 45 | Completed |
| ERR-11 | Phase 45 | Completed |
| TYP-10 | Phase 45 | Completed |
| QLT-15 | Phase 45 | Completed |

**Coverage:**
- v1.6 routed requirements: 14 total
- Current mapped: 14
- Current complete: 14
- Current pending: 0
- Current unmapped: 0 ✓

## Archived Milestone (v1.5)

> `v1.5` 已于 `2026-03-19` 完成归档；以下 requirements / traceability 保留 `Phase 40` 的最终 fulfilled contract，归档快照见 `.planning/milestones/v1.5-REQUIREMENTS.md`，审计裁决见 `.planning/v1.5-MILESTONE-AUDIT.md`，证据入口见 `.planning/reviews/V1_5_EVIDENCE_INDEX.md`。

### Governance Truth & Control-Surface Finalization

- [x] **GOV-33**: authority precedence、active truth、archive snapshots、promoted phase assets 与 derived collaboration maps 的身份必须在 `AGENTS.md`、baseline 三件套、`docs/README.md` 与 current-story docs 中讲同一条故事，并吸收 `V1_4_EVIDENCE_INDEX.md` / `v1.4-MILESTONE-AUDIT.md` / `Phase 38-39` closeout 证据。
- [x] **QLT-11**: continuity / release-trust / install-path / support-routing 事实必须收口到 machine-readable governance registry，并以 meta guards 强制 README、README_zh、CONTRIBUTING、SUPPORT、SECURITY、TROUBLESHOOTING、runbook、issue/PR templates 同步；同时补齐 break-glass verify-only 与 non-publish rehearsal 语义。
- [x] **CTRL-09**: control/services 对 runtime 的枚举、device read-model、snapshot/telemetry projection 与 diagnostics lookup 必须统一经 `runtime_access` formal home 暴露，不得继续在 `diagnostics_surface.py`、`device_lookup.py`、`maintenance.py` 各自复制 locator/read logic。
- [x] **ERR-10**: service-layer auth/error execution contract 必须统一到正式 shared executor；`schedule.py` 不得继续复制 coordinator auth chain、旁路 reauth 语义或独立 broad arbitration story。
- [x] **RES-10**: touched protocol/runtime/service hotspots 中的 `client` / `forwarding` / `mixin` stale terminology 必须继续收口到 `protocol` / `port` / `facade` / `operations` 语义；compat-leaning wording 只允许留在历史文档或显式 residual 账本中。

## Traceability for archived v1.5 route

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-33 | Phase 40 | Complete |
| QLT-11 | Phase 40 | Complete |
| CTRL-09 | Phase 40 | Complete |
| ERR-10 | Phase 40 | Complete |
| RES-10 | Phase 40 | Complete |

**Coverage:**
- v1.5 routed requirements: 5 total
- Current mapped: 5
- Current complete: 5
- Current pending: 0
- Current unmapped: 0 ✓

## Archived Milestone (v1.4)

> `v1.4` 已于 `2026-03-19` 完成归档；以下 requirements / traceability 保留 `Phase 34 -> 39` 的最终 fulfilled contract，归档快照见 `.planning/milestones/v1.4-REQUIREMENTS.md`，审计裁决见 `.planning/v1.4-MILESTONE-AUDIT.md`，证据入口见 `.planning/reviews/V1_4_EVIDENCE_INDEX.md`。

### Continuity & Release Trust

- [x] **GOV-29**: maintainer continuity 已从“单维护者现实的诚实记录”升级为“delegate / custody transfer / freeze escalation”的正式合同；support / security / release 不再依赖隐性人治。
- [x] **QLT-08**: release identity 已补齐 machine-verifiable artifact signing，并把 hard release-trust gate 与现有 `SHA256SUMS` / `SBOM` / attestation / provenance story 统一成单一 blocking contract。

### Protocol Hotspots

- [x] **HOT-09**: `LiproRestFacade` 与 `LiproProtocolFacade` 必须继续沿现有 seams 切薄，root 层 forwarding glue 不得长期合法化为协议主链的一部分。
- [x] **RES-07**: protocol/control touched hotspots 的 compat / forwarding residue、反射/私有实现细节依赖（如 `__dict__` / `_waiters` 类模式）与命名残留必须继续删除、下沉或显式登记 delete gate；public surface 不能借重构反向扩张。

### Runtime Root & Exception Policy

- [x] **HOT-10**: `Coordinator` 运行根必须继续瘦身，并把 runtime/service 协作者 home 固化到更小、更清晰的边界。
- [x] **ERR-08**: 生产宽异常必须继续 burn-down 到可守护阈值；核心热点只能保留 named arbitration、documented degraded semantics 或 fail-closed path。
- [x] **TYP-09**: runtime/service/platform touched-zone 的 typed budget 必须继续收紧，并以 no-growth guards 固化到 daily governance gates。

### Test Topology & Derived Truth

- [x] **TST-06**: 剩余巨石测试必须继续 topicize 成稳定、可局部执行的专题面，避免单文件持续吸附多条故事线。
- [x] **GOV-30**: `.planning/codebase/*`、测试策略文档、verification / authority truth 与 public docs entry topology 必须和真实测试命令、目录结构、support/security/docs routing 及守卫语义保持一致，并有 drift guard 约束。
- [x] **QLT-09**: benchmark / test-topology / closeout evidence / governance guards 必须从“可执行”提升到“可解释、可对齐、可审计”的质量故事：形成预算或基线语义、降低 prose-coupled 高噪音断言，并避免派生真相漂移于实际门禁之外。

### Fresh-Audit Residual & Quality-Signal Hardening

- [x] **RES-08**: external-boundary firmware naming 必须退役最后一条 active residual family，统一到 bundled local trust-root asset + remote advisory payload 的诚实术语，同时保留历史资产文件名与 authority contract。
- [x] **QLT-10**: coverage floor / explicit-baseline diff / advisory benchmark artifact posture 必须在脚本、CI、贡献文档与 derived testing map 中讲同一条 machine-checkable 质量故事，dead marker semantics 不得回流。
- [x] **GOV-31**: governance closeout / phase-history guards 必须优先依赖 `ROADMAP` / `REQUIREMENTS` / recommended command anchors，而不是 sentence-level `PROJECT` / `STATE` prose 复述，同时保持审计强度。

### Governance Current-Story & Test Topology Closeout

- [x] **GOV-32**: `ROADMAP / REQUIREMENTS / STATE / PROJECT` 必须共同承认 `v1.4 / Phase 39 complete / closeout-ready` 当前故事，coverage / traceability 算术可被守卫验证。
- [x] **DOC-03**: `docs/NORTH_STAR_TARGET_ARCHITECTURE.md` 与 `docs/developer_architecture.md` 必须刷新到 current topology，并显式说明 `custom_components/lipro/control/` 是 formal control-plane home。
- [x] **CTRL-08**: control-plane formal home / thin-adapter boundary / `services/` helper identity 必须同步到治理真源、review ledgers 与守卫断言。
- [x] **RES-09**: dead protocol shell、误导性 fixture/replay authority 命名与相关 residual folklore 必须退场或历史化，不得继续暗示第二 public truth。
- [x] **TST-07**: remaining mega-tests 与治理巨石守卫必须继续 topicize / structure 化，Phase 39 closeout evidence 必须显式 promoted。

## Traceability for v1.4 route + fresh-audit continuation

| Requirement | Planned Phase | Status |
|-------------|---------------|--------|
| GOV-29 | Phase 34 | Complete |
| QLT-08 | Phase 34 | Complete |
| HOT-09 | Phase 35 | Complete |
| RES-07 | Phase 35 | Complete |
| HOT-10 | Phase 36 | Complete |
| ERR-08 | Phase 36 | Complete |
| TYP-09 | Phase 36 | Complete |
| TST-06 | Phase 37 | Complete |
| GOV-30 | Phase 37 | Complete |
| QLT-09 | Phase 37 | Complete |
| RES-08 | Phase 38 | Complete |
| QLT-10 | Phase 38 | Complete |
| GOV-31 | Phase 38 | Complete |
| GOV-32 | Phase 39 | Complete |
| DOC-03 | Phase 39 | Complete |
| CTRL-08 | Phase 39 | Complete |
| RES-09 | Phase 39 | Complete |
| TST-07 | Phase 39 | Complete |

**Coverage:**
- v1.4 requirements + fresh-audit continuation: 18 total
- Current mapped: 18
- Current complete: 18
- Current pending: 0
- Current unmapped: 0 ✓
