# Requirements: Lipro-HASS v1.1

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

- [ ] **GOV-14**: `AGENTS.md`、`PROJECT.md`、`ROADMAP.md`、`STATE.md`、baseline/review docs 与 `.planning/codebase/*` policy 必须重新对齐到 Phase 16 规划真相，不得继续把已关闭 seam 或过期 codebase map 当成活跃裁决来源；Phase 16 closeout 不允许留下无 owner / 无 delete gate / 无风险说明的高风险 carry-forward。
- [ ] **QLT-02**: Python / Ruff / pre-commit / devcontainer / pytest marker truth 必须一致：运行时、类型检查与 lint 目标版本不能漂移，名存实亡的 marker / tooling contract 必须落地或删除；本地 DX 与 closeout 质量门禁必须把这套真相可执行化。
- [ ] **HOT-04**: `core/api/client.py`、`core/protocol/facade.py`、`core/coordinator/coordinator.py`、`control/service_router.py`、`config_flow.py`、`entities/firmware_update.py` 及其 second-pass 发现的 secondary hotspots（如 entry-lifecycle / diagnostics / telemetry / request-policy / status-fallback / mqtt-runtime / rest-decoder 等）必须继续沿正式边界拆薄，避免 façade/root 与其紧邻协作者继续承载 strategy、shape normalization、exception mapping 与 glue 内核。
- [ ] **TYP-04**: `core/api`、`core/protocol`、`control` 与相邻 residual seams 中的 `Any` / `type: ignore` / `cast` / `getattr` / `import_module` 等宽口必须进一步收窄到 `Protocol`、typed alias、`TypedDict` 或明确 contract，不得仅靠技术性掩饰继续掩盖边界漂移。
- [ ] **ERR-01**: protocol/runtime/control/support 关键链路中的 catch-all 异常必须收窄或显式写成 documented arbitration，日志、重试与 reauth 语义必须可判定；entry-lifecycle、diagnostics/telemetry、mqtt-runtime、firmware-update 与相邻 glue seams 不得继续保留 undocumented broad-catch。
- [ ] **RES-02**: `_ClientBase` / `_Client*Mixin`、endpoint mixin exports、`LiproMqttClient` legacy naming、`get_auth_data()` fallback 与 helper-level compat envelope 必须继续本地化、减语义或退场，不得再制造旧 root / old client 仍合法的错觉。
- [ ] **CTRL-06**: `send_command`、share/developer-report、entry lifecycle、diagnostics/telemetry、maintenance/device-lookup、runtime access 与相关 response schema 必须统一到更清晰的 formal control/runtime contract：auth/error 主链一致、service payload shape 稳定、动态导入/反射式探测继续下降。
- [ ] **DOM-03**: `LiproDevice`、`CapabilitySnapshot`、entity descriptors 与平台能力消费协议必须进一步收口到单一领域真源；死接口、重复透传属性与双轨 capability 语义不得继续扩散。
- [ ] **OTA-01**: firmware update entity 必须回到 projection + action bridge 身份；manifest 读取、row arbitration、cache/hot-path I/O 与 install policy 应进一步下沉到更合适的 service/helper home。
- [ ] **TST-01**: platform/domain test layering 必须纠偏：平台测试优先验证真实 entity adapter，领域测试验证 device/capability semantics，OTA 策略测试不再长期停留在 platform test home。
- [ ] **DOC-02**: troubleshooting、contributor navigation、maintainer release runbook 与 `scripts/develop` 等本地 DX 入口必须与高治理仓库的真实维护路径对齐，降低新贡献者与单维护者的操作负担；Phase 16 closeout 还必须给出 second-pass re-audit 与 residual closeout story。

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

- **OBS-03**: 如需要外部监控对接，再评估 Prometheus / OpenTelemetry sink
- **BND-04**: 如 manual validators 成本继续升高，再裁决局部 `pydantic v2` backend
- **ENF-03**: 如 AST/meta guards 复杂度继续上升，再评估 `import-linter/grimp`
- **SIM-03**: 如需要更强双向仿真，再补 broker/cloud behavioral simulator
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
| GOV-14 | Phase 16 | Planned |
| QLT-02 | Phase 16 | Planned |
| HOT-04 | Phase 16 | Planned |
| TYP-04 | Phase 16 | Planned |
| ERR-01 | Phase 16 | Planned |
| RES-02 | Phase 16 | Planned |
| CTRL-06 | Phase 16 | Planned |
| DOM-03 | Phase 16 | Planned |
| OTA-01 | Phase 16 | Planned |
| TST-01 | Phase 16 | Planned |
| DOC-02 | Phase 16 | Planned |

**Coverage:**
- active milestone requirements: 65 total
- mapped to phases: 65
- unmapped: 0 ✓

*Last updated: 2026-03-15 after planning Phase 16 scope*
