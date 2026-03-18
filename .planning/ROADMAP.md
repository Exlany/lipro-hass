# Roadmap: Lipro-HASS North Star Evolution

## Milestones

- ✅ **v1.0 North Star Rebuild** - Phases 1-7 (+ 1.5 / 2.5 / 2.6), shipped 2026-03-13, archive: `.planning/milestones/v1.0-ROADMAP.md`
- ✅ **v1.1 Protocol Fidelity & Operability** - Phases 7.1-17 complete; final audit complete; milestone snapshots archived at `.planning/milestones/v1.1-ROADMAP.md` / `.planning/milestones/v1.1-REQUIREMENTS.md` (updated 2026-03-16)
- ✅ **v1.2 Host-Neutral Core & Replay Completion** - Phases 18-24 complete after Phase 24 reopen revalidation; 24 plans complete; milestone snapshots archived at `.planning/milestones/v1.2-ROADMAP.md` / `.planning/milestones/v1.2-REQUIREMENTS.md`; `v1.3` handoff-ready (revalidated 2026-03-17)

## Required Phase Outputs

每个 phase 完成时，除了代码与测试，还必须显式更新或确认以下输出：

- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/baseline/AUTHORITY_MATRIX.md`

## Phases

<details>
<summary>✅ v1.0 North Star Rebuild (Phases 1-7) — SHIPPED 2026-03-13</summary>

历史 v1.0 全量路线图已归档至 `.planning/milestones/v1.0-ROADMAP.md`。

</details>

### 🚧 v1.1 Protocol Fidelity & Operability

**Milestone Goal:** 在不破坏既有北极星单一主链的前提下，正式引入 boundary decoder family、architecture policy enforcement、runtime telemetry exporter、replay evidence，并把已登记 residual surfaces 收口到显式、可删除、可验证的最小集合。

**Current Status:** `Phase 7.1` 到 `Phase 17` 已全部完成（58/58 plans executed，2026-03-15）；`v1.1` 的 final closeout 与 repo audit 已落地，archive snapshots 已写入 `.planning/milestones/v1.1-ROADMAP.md` 与 `.planning/milestones/v1.1-REQUIREMENTS.md`。

### Phase 7.1: Protocol Boundary Schema/Decoder 收口
**Goal**: 把 REST/MQTT 的 decode authority 收口到 protocol boundary family，形成可版本化 schema/decoder registry，同时阻断 raw payload 穿透。
**Depends on**: Phase 7
**Requirements**: [BND-01, BND-02, BND-03]
**Success Criteria**:
  1. `protocol boundary family` 成为 decode authority 的正式归属。
  2. REST/MQTT 边界输入经统一 decoder family 输出 canonical contracts。
  3. authority / fixtures / drift assertions 与 boundary family 对齐，不再出现第二真源。
**Plans**: 3 plans

Plans:
- [x] 07.1-01: 建立 boundary inventory、decoder family 与 schema registry 设计
- [x] 07.1-02: 接入 REST/MQTT decoder pipeline 并阻断 raw payload leakage
- [x] 07.1-03: 补齐 boundary fixtures、contract/replay-ready assertions 与治理回写

### Phase 7.2: Architecture Enforcement 加固
**Goal**: 把 v1.1 新增 boundary/exporter/replay 组件纳入更强 architecture policy，阻止双主链、跨层直连、compat 回流复发。
**Depends on**: Phase 7.1
**Requirements**: [ENF-01, ENF-02]
**Success Criteria**:
  1. rules 不只守 import，还守 plane/root/surface/authority。
  2. 本地与 CI 都能快速发现结构偏航。
  3. 新增组件不会重新引入 backdoor 或第二主链。
**Plans**: 2 plans

Plans:
- [x] 07.2-01: 定义 architecture policy spec 与 rule categories
- [x] 07.2-02: 升级 meta guards、CI gates 与开发期快速校验链

### Phase 7.3: Runtime Telemetry Exporter 正式化
**Goal**: 把 runtime/protocol telemetry 收口到 exporter surface，使 diagnostics、system health、developer/CI sinks 共享同一真源。
**Depends on**: Phase 7.2
**Requirements**: [OBS-01, OBS-02]
**Success Criteria**:
  1. exporter 覆盖 auth recovery、MQTT reconnect、command confirmation、refresh latency。
  2. diagnostics / system health / exporter 共用统一 telemetry truth。
  3. redaction 与 cardinality budget 有明确规则并被测试验证。
**Plans**: 2 plans

Plans:
- [x] 07.3-01: 建立 telemetry exporter models/ports/sinks
- [x] 07.3-02: 接入 runtime/protocol telemetry sources 与 redaction validation

### Phase 7.4: Protocol Replay / Simulator Harness 建立
**Goal**: 让逆向协议样本能够经正式 façade/decoder 路径做确定性回放，生成 fidelity 与 operability 证据。
**Depends on**: Phase 7.3
**Requirements**: [SIM-01, SIM-02]
**Success Criteria**:
  1. replay harness 复用正式 protocol public path，不复制第二实现。
  2. REST/MQTT 回放可产出 canonical assertions、drift assertions 与 telemetry assertions。
  3. replay corpus 具有 authority source、版本戳与 deterministic controls。
**Plans**: 3 plans

Plans:
- [x] 07.4-01: 建立 replay assets authority、fixture layout 与 deterministic driver
- [x] 07.4-02: 为 REST/MQTT contract flows 接入 replay assertions
- [x] 07.4-03: 补 operability diagnostics 与 replay-based regression suite

### Phase 7.5: Integration / Governance / Verification 收尾
**Goal**: 对 v1.1 新增 boundary/exporter/replay/enforcement 组件做 file-level governance、verification matrix、closeout evidence 与 residual arbitration。
**Depends on**: Phase 7.4
**Requirements**: [GOV-06, GOV-07]
**Success Criteria**:
  1. file matrix / authority / verification / residual docs 全部同步。
  2. 每个新增组件都有 owner、delete gate、acceptance evidence。
  3. v1.1 交付物可以形成下一轮演进的稳定起点。
**Plans**: 2 plans

Plans:
- [x] 07.5-01: 回写 governance truth sources 与 file-level ownership
- [x] 07.5-02: 生成 v1.1 verification/closeout package 与 next-step recommendations

### Phase 8: AI Debug Evidence Pack

**Goal**: 把 telemetry/replay/boundary/governance 产物统一导出为“可给 AI 调试/分析”的脱敏证据包（Assurance/Tooling only）。
**Depends on**: Phase 7.5
**Requirements**: [AID-01, AID-02]
**Success Criteria**:
  1. evidence pack schema 版本化且稳定，默认 JSON 输出，附带 index。
  2. 证据包只 pull 正式真源（exporter/replay/boundary inventory/governance pointers），不生成第二套事实。
  3. 脱敏策略明确：凭证等价物永不出现；允许报告内稳定、跨报告不可关联的伪匿名引用；允许真实时间戳。
**Plans**: 2 plans

Plans:
- [x] 08-01: 定义 evidence pack schema、pseudo-id 与 redaction 策略
- [x] 08-02: 实现 evidence pack exporter + tests + governance handoff

### Phase 9: Residual Surface Closure

**Goal**: 收口审查报告中已登记的 protocol/runtime 残留：消除 child-defined protocol contract、收窄 compat exports、封住 live mutable runtime surface，并把 outlet power 旁写迁移到正式 primitive。
**Depends on**: Phase 8
**Requirements**: [RSC-01, RSC-02, RSC-03, RSC-04]
**Success Criteria**:
  1. `LiproProtocolFacade` 的正式 public surface 显式可裁决，child façade 不再通过 `__getattr__` / `__dir__` 隐式定义 protocol root；`raw_client` 仅允许存在于显式 compat/test seam 或被正式删除。
  2. runtime 对设备集合的对外访问不再暴露 live mutable dict；平台/diagnostics/helpers 改走只读 view 或正式 service contract。
  3. outlet power 不再通过 `device.extra_data["power_info"]` 旁写作为正式路径；实体/diagnostics/runtime 共用同一正式 primitive，并保留必要迁移兼容与回归证明。
  4. compat exports、governance matrices、residual/delete gate 与 meta/public-surface guards 全部同步，防止 residual surface 回流。
**Plans**: 5 plans

Plans:
- [x] 09-01: 收窄 protocol root surface 与 compat exports
- [x] 09-02: 正式化 runtime 只读设备视图与 outlet power primitive
- [x] 09-03: 回写 governance residual ledger、delete gate 与 regression guards
- [x] 09-04: 收敛 API/compat 旧测试夹具与 request patch 模式
- [x] 09-05: 收敛 runtime/platform/integration 旧测试到正式 surfaces

**Planning addendum (2026-03-14):** 已完成 legacy test convergence：API mega-test、runtime/platform/integration tests 已收敛到 formal surface、shared harness 与显式 compat seam，旧测试不再反向放大历史语义。

### Phase 10: API Drift Isolation & Core Boundary Prep

**Goal:** 在不引入第二条正式主链、也不提前物理抽离跨平台 SDK 的前提下，把逆向 API 的高漂移形态继续收口到 protocol boundary，提炼 host-neutral protocol/auth/device contracts，并收窄 HA adapter 对 protocol/runtime concrete shape 的依赖，让未来 CLI / 其他宿主只能建立在正式边界之上。
**Requirements**: [ISO-01, ISO-02, ISO-03, ISO-04]
**Depends on:** Phase 9
**Success Criteria**:
  1. `login`、`device_list`、`query_device_status`、`query_mesh_group_status`、OTA/support-critical payload 等高漂移输入在 protocol boundary 完成 canonicalization；runtime/domain/control 不再自行解析 vendor envelope、field alias 或分页形态。
  2. `config_flow` / `entry_auth` / control adapters 通过 formal auth/result contract 或显式 use case 协作，而不是直接依赖 raw response dict shape；底层 API 漂移不再直接打穿 HA adapter。
  3. `core` formal public surface 与 HA runtime root 的边界继续收窄：`Coordinator` 保持由 `coordinator_entry` 暴露，`core/__init__.py` 不再承担 host-neutral core truth 之外的 HA runtime 叙事。
  4. 与 drift isolation 相关的 roadmap/context/research/validation/verification/governance docs、replay fixtures 与 meta guards 同轮更新，确保未来 CLI / 其他宿主只能复用 formal boundary，而不是催生 second root。
**Plans**: 4 plans

Plans:
- [x] 10-01: 高漂移 protocol boundary canonicalization 收口
- [x] 10-02: formal auth/result contracts 与 HA control adapter 降耦
- [x] 10-03: `core` formal surface 与 HA runtime home 继续收窄
- [x] 10-04: docs / governance / replay / meta guard 同步闭环

## Cross-Phase Arbitration (7.3-14)

- `07.3` 只拥有 telemetry truth：exporter contracts、redaction、cardinality、timestamp / pseudo-id compatibility
- `07.4` 只拥有 replay truth：manifests、deterministic driver、replay assertions、run summary
- `07.5` 只拥有 governance closeout：matrices、evidence index、residual、delete gates
- `08` 只拥有 AI debug packaging：pull-only collector、pack schema、exporter entrypoint
- `09` 只拥有 residual surface closure：protocol/runtime 收口、compat seam 压缩、formal primitive / read-only view 收敛、governance delete gate 回写
- `10` 只拥有 API drift isolation / core-boundary prep：boundary contract closure、host-neutral auth/result contracts、HA adapter 降耦与治理同步；不得在本 phase 内把 shared core / cross-platform SDK 提升为正式 root
- `11` 只拥有 control router formalization、runtime-access hardening、entity/OTA truth convergence 与 open-source governance coherence；不得重新合法化 compat service carrier 或 dynamic protocol surface
- `12` 只拥有 type contract convergence、compat residual narrowing、hotspot slimming 与 contributor-facing governance hygiene；不得重新打开已在 Phase 11 关闭的 residual truth
- `13` 只拥有显式设备域表面、runtime/status 热点 helper 边界与公开治理资产结构化守卫；不得重新合法化动态 delegation
- `14` 只拥有 legacy stack final closure、API spine demolition 与 governance truth consolidation；不得把 `Coordinator.client` / `ScheduleApiService` / helper-home modules 回流为正式主链
- `15` 只拥有 developer feedback contract、governance truth repair、install/support truth sync、support hotspot follow-through 与 tooling/residual arbitration；不得因支持面修补重开第二条正式主链
- 执行顺序固定为 `7.3 -> 7.4 -> 7.5 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15`，避免真源反转与职责重叠

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-7 (+1.5/2.5/2.6) | v1.0 | 32/32 | Complete | 2026-03-13 |
| 7.1 Boundary Schema/Decoder | v1.1 | 3/3 | Complete | 2026-03-13 |
| 7.2 Enforcement | v1.1 | 2/2 | Complete | 2026-03-13 |
| 7.3 Telemetry Exporter | v1.1 | 2/2 | Complete | 2026-03-13 |
| 7.4 Replay Harness | v1.1 | 3/3 | Complete | 2026-03-13 |
| 7.5 Governance & Verification | v1.1 | 2/2 | Complete | 2026-03-13 |
| 8 AI Debug Evidence Pack | v1.1 | 2/2 | Complete | 2026-03-13 |
| 9 Residual Surface Closure | v1.1 | 5/5 | Complete | 2026-03-14 |
| 10 API Drift Isolation & Core Boundary Prep | v1.1 | 4/4 | Complete | 2026-03-14 |
| 11 Control Router Formalization & Wiring Residual Demotion | v1.1 | 8/8 | Complete | 2026-03-14 |
| 12 Type Contract Alignment, Residual Cleanup & Governance Hygiene | v1.1 | 5/5 | Complete | 2026-03-14 |
| 13 Explicit Domain Surface, Governance Guard Hardening & Hotspot Boundary Decomposition | v1.1 | 3/3 | Complete | 2026-03-14 |
| 14 Legacy Stack Final Closure, API Spine Demolition & Governance Truth Consolidation | v1.1 | 4/4 | Complete | 2026-03-15 |
| 15 Support Feedback Contract Hardening, Governance Truth Repair & Maintainability Follow-Through | v1.1 | 5/5 | Complete | 2026-03-15 |
| 16 Post-audit Truth Alignment, Hotspot Decomposition & Residual Endgame | v1.1 | 6/6 | Complete | 2026-03-15 |
| 17 Final Residual Retirement, Typed-Contract Tightening & Milestone Closeout | v1.1 | 4/4 | Complete | 2026-03-15 |

### Phase 11: Control Router Formalization & Wiring Residual Demotion

**Goal:** 在 control router formalization 已落地的基础上，继续收口本轮全仓复审暴露的 protocol/runtime residual surfaces、runtime access / diagnostics gaps、entity/platform modeling truth 与 governance/open-source maturity gaps。
**Requirements**: CTRL-01, CTRL-02, CTRL-03, SURF-01, CTRL-04, RUN-01, ENT-01, ENT-02, GOV-08
**Depends on:** Phase 10
**Plans:** 8/8 plans complete

Plans:
- [x] 11-01: formal router implementation inversion (completed 2026-03-14)
- [x] 11-02: legacy wiring demotion and test truth alignment (completed 2026-03-14)
- [x] 11-03: governance synchronization and verification closeout (completed 2026-03-14)
- [x] 11-04: protocol and runtime formal surface convergence (completed 2026-03-14)
- [x] 11-05: runtime access diagnostics and isolation hardening (completed 2026-03-14)
- [x] 11-06: entity and platform truth convergence (completed 2026-03-14)
- [x] 11-07: firmware update hotspot slimming (completed 2026-03-14)
- [x] 11-08: governance release and open-source coherence (completed 2026-03-14)

### Phase 12: Type Contract Alignment, Residual Cleanup & Governance Hygiene

**Goal:** 在不回退 Phase 11 已完成真相的前提下，清空当前 `mypy` 类型红灯，继续收窄显式 compat seams 与 `core/api` 历史骨架，顺着 formal boundary 切薄热点文件，并把 contributor-facing docs/config/open-source contract 同步到当前仓库真相。
**Requirements**: TYP-01, TYP-02, CMP-01, CMP-02, HOT-01, GOV-09, GOV-10
**Depends on:** Phase 11
**Plans:** 5/5 plans complete

Plans:
- [x] 12-01: runtime public type contract convergence (completed 2026-03-14)
- [x] 12-02: rest facade typed return alignment (completed 2026-03-14)
- [x] 12-03: compat surface narrowing and core api skeleton slimming (completed 2026-03-14)
- [x] 12-04: hotspot decomposition and exception boundary tightening (completed 2026-03-14)
- [x] 12-05: contributor contract and governance hygiene sync (completed 2026-03-14)

### Phase 13: Explicit Domain Surface, Governance Guard Hardening & Hotspot Boundary Decomposition

**Goal:** 把设备域的动态委托收口为显式 formal surface，继续拆薄 runtime/status 热点边界，并把 README / support / CODEOWNERS / quality-scale / devcontainer 等公开治理资产纳入结构化 guard。
**Requirements**: DOM-01, DOM-02, RUN-02, RUN-03, GOV-11
**Depends on:** Phase 12
**Plans:** 3/3 plans complete

Plans:
- [x] 13-01: explicit device and state surfaces (completed 2026-03-14)
- [x] 13-02: runtime hotspot decomposition and protocol terminology convergence (completed 2026-03-14)
- [x] 13-03: governance guard hardening and documentation sync (completed 2026-03-14)

### Phase 14: Legacy Stack Final Closure, API Spine Demolition & Governance Truth Consolidation

**Goal:** 彻底收口 `Coordinator` / `core/api` / `service_router` 周边最后一批旧 API spine 与 helper 回环：把 `Coordinator` 内部协议真源统一为 `protocol`，删除 `ScheduleApiService` 与 schedule passthrough，抽离 `status_service` fallback kernel 与 `service_router` developer glue，并把 subordinate governance truth / residual guards 完整回写到当前代码真相。
**Requirements**: RUN-04, HOT-02, CTRL-05, RUN-05, GOV-12
**Depends on:** Phase 13
**Success Criteria**:
  1. `Coordinator` 内部不再以 `client` 术语承载正式协议真源；protocol-facing runtime ops 经 `CoordinatorProtocolService` 收口。
  2. `ScheduleApiService` 与 `client.py` 尾部 schedule 私有 passthrough 已删除；schedule truth 固定为 `ScheduleEndpoints` + focused helpers。
  3. `status_service.py` 与 `service_router.py` 仅保留 public orchestration / handler 身份；fallback/glue 内核分别下沉到 `status_fallback.py` 与 `developer_router_support.py`。
  4. `PUBLIC_SURFACES / ARCHITECTURE_POLICY / VERIFICATION_MATRIX / FILE_MATRIX / RESIDUAL_LEDGER / KILL_LIST / PROJECT / STATE / ROADMAP / REQUIREMENTS` 与 meta guards 全部同步到 Phase 14 完成态。
**Plans:** 4/4 plans complete

Plans:
- [x] 14-01: coordinator protocol terminology convergence and api-spine slimming (completed 2026-03-15)
- [x] 14-02: api schedule residual closure and endpoint helper spine slimming (completed 2026-03-15)
- [x] 14-03: status fallback kernel and control-router glue extraction (completed 2026-03-15)
- [x] 14-04: governance truth refresh and residual guard hardening (completed 2026-03-15)

### Phase 15: Support feedback contract hardening, governance truth repair, and maintainability follow-through

**Goal:** 把终极审阅中确认仍然存在的问题收敛为单一正式修复线：明确 developer feedback 上传契约（保留 `iotName` 等供应商诊断标识、匿名化用户自定义名称）、修补治理真源死链与状态漂移、同步外部安装/支持文档、继续拆薄 support hotspots，并把测试/安全/工具链缺口收口为可执行门禁。
**Requirements**: [SPT-01, GOV-13, DOC-01, HOT-03, QLT-01, TYP-03, RES-01]
**Depends on:** Phase 14
**Success Criteria**:
  1. developer feedback contract、fixtures、docs 与 tests 对 `iotName` / user-defined labels 的处理完全一致。
  2. active governance docs 不再引用不存在 source，phase/status/date/footer consistency 受守卫保护。
  3. README / README_zh / SUPPORT / CI / version metadata 对最低 HA 版本与 HACS/private-repo caveat 保持一致。
  4. `service_router.py` 与 developer feedback / report hotspots 进一步拆薄，upload shaping 与 local debug view 明确分家。
  5. 审阅确认的 testing/tooling/security gaps 被转成明确 gate、baseline、fixture 或 documented arbitration；remaining residual naming/typing 继续收口而不回流。
**Plans:** 5/5 plans complete across 3 waves

Plans:
- [x] 15-01: developer feedback upload contract projector and support-copy truth (completed 2026-03-15)
- [x] 15-02: governance truth repair and phase-state guard hardening (completed 2026-03-15)
- [x] 15-03: install support and version truth sync (completed 2026-03-15)
- [x] 15-04: support hotspot decomposition and runtime-access typing narrowing (completed 2026-03-15)
- [x] 15-05: tooling security and residual policy arbitration (completed 2026-03-15)

### Phase 16: Post-audit truth alignment, hotspot decomposition, and residual endgame

**Goal:** 在不偏离北极星单一正式主链的前提下，把终极审阅确认仍然成立的剩余问题统一收口：校准治理/工具链真相，拆薄 `core/api` / `core/protocol` / `core/coordinator` / `control` / domain / OTA 热点及其 secondary glue hotspots，继续收紧类型与异常语义，削弱 residual/compat 认知债，并补齐测试分层、开源 DX 与 closeout audit 跟进。
**Requirements**: [GOV-14, QLT-02, HOT-04, TYP-04, ERR-01, RES-02, CTRL-06, DOM-03, OTA-01, TST-01, DOC-02]
**Depends on:** Phase 15
**Success Criteria**:
  1. `AGENTS.md`、`PROJECT.md`、`ROADMAP.md`、`STATE.md`、baseline/review truth 与 `.planning/codebase/*` policy 对活跃 phase / residual / authority / toolchain 讲同一条故事，不再出现已关闭 seam 被误记为 active residual 的冲突；`.planning/codebase/*` 明确只作为 derived collaboration maps。
  2. Python / Ruff / pre-commit / devcontainer / pytest marker truth 完全对齐，测试与 lint 规则集不再出现“运行时 3.14、规则仍按 3.13”这类认知漂移，`scripts/develop` 的非破坏性也有显式 smoke/manual gate。
  3. `LiproRestFacade`、`LiproProtocolFacade`、`Coordinator`、`service_router.py`、`config_flow.py`、`firmware_update.py` 及其 second-pass 暴露的 entry-lifecycle / diagnostics / telemetry / request-policy / status-fallback / mqtt-runtime / rest-decoder 等 secondary hotspots 都被纳入明确计划，不存在高风险热点游离于计划之外。
  4. `Any` / `type: ignore` / reflection / catch-all exception 的收口有真实 contract 与异常语义结果，热点文件需记录 before/after 指标，且关键 debt 不得净增。
  5. `core/api` helper spine、legacy MQTT naming、auth compat seam 与 outlet-power compat envelope 等当时 remaining residual 都已获得更窄、更诚实的本地语义，并通过 residual closeout 表写清 `item / disposition / owner / phase / delete gate / evidence`；其最终 physical retirement / truthful disposition 已在 Phase 17 完成。
  6. device / capability / entity / OTA / platform test layering 更接近单一领域真源：`LiproDevice` 不再继续膨胀成第二套 public surface，capability 消费协议与 OTA projection/service 边界更清晰。
  7. troubleshooting / contributor navigation / release runbook / local develop workflow 与 CI / docs / support truth 对齐，且 phase closeout 包含 second-pass repo audit，证明不存在未登记的高风险 carry-forward。
**Plans:** 6/6 complete across 3 waves

Plans:
- [x] 16-01: governance truth calibration and codebase-map policy arbitration (completed 2026-03-15)
- [x] 16-02: toolchain truth alignment and local DX contract cleanup (completed 2026-03-15)
- [x] 16-03: control/service contract unification and response-shape stabilization (completed 2026-03-15)
- [x] 16-04: protocol/runtime hotspot decomposition, typing narrowing, and exception semantics tightening (completed 2026-03-15)
- [x] 16-05: domain/entity/OTA surface rationalization (completed 2026-03-15)
- [x] 16-06: test-layer correction and open-source maintenance follow-through (completed 2026-03-15)

### Phase 17: Final residual retirement, typed-contract tightening and milestone closeout

**Goal:** 完成 v1.1 最后一轮 physical closeout：删除 API dead shells 与 legacy mixin spine，统一 auth / outlet-power typed contract，完成 MQTT canonical transport naming 与 no-export ban，并把所有 final closeout truth 回写到治理资产、里程碑审计与最终 repo audit 证据中。
**Requirements**: RES-03, TYP-05, MQT-01, GOV-15
**Depends on:** Phase 16
**Success Criteria**:
  1. `_ClientTransportMixin`、endpoint legacy mixin family、`_ClientPacingMixin`、`_ClientAuthRecoveryMixin` 与 `get_auth_data()` compat projection 已物理退场。
  2. `client_base.py` 只剩 `ClientSessionState`，`power_service.py` / protocol/runtime outlet-power path 只承认 explicit row/list contract，不再产生 synthetic wrapper。
  3. MQTT concrete transport 的 canonical 名称统一为 `MqttTransportClient`，且 root/core package no-export bans 与 locality guard 已同步到 baseline/tests。
  4. `ROADMAP / REQUIREMENTS / STATE / PROJECT / baseline / review ledgers / AGENTS / developer_architecture / milestone audit` 对 Phase 17 讲同一条完成态故事线。
**Plans:** 4/4 complete

Plans:
- [x] 17-01: api residual spine retirement and endpoint-port convergence (completed 2026-03-15)
- [x] 17-02: auth session and outlet-power contract convergence (completed 2026-03-15)
- [x] 17-03: mqtt transport naming demotion and locality guard hardening (completed 2026-03-15)
- [x] 17-04: phase 17 governance closeout and final repo audit (completed 2026-03-15)


## Current Milestone

### ✅ v1.2: Host-Neutral Core & Replay Completion

**Milestone Goal:** 在不破坏 `LiproProtocolFacade` / `Coordinator` 单一正式主链的前提下，把 future-host shared-core debt、remaining boundary/replay family debt 与关键 broad-catch / observability debt 提升为正式交付，让仓库从“HA 内部高治理集成”继续迈向“可复用、可回放、可宿主扩展、但不多根分裂”的下一阶段。

**Execution Scope:** `Phase 18 -> Phase 24`（7 phases / 24 plans；`24-04` / `24-05` 于 2026-03-17 完成 reopen revalidation）

**Current Status:** `Phase 18` 到 `Phase 24` 已全部完成（24/24 plans executed；Phase 24 于 2026-03-17 reopened 并重新验证）；`v1.2` 的 final repo audit、evidence index、milestone audit 与 `v1.3` handoff 已落地，archive snapshots 已写入 `.planning/milestones/v1.2-ROADMAP.md` 与 `.planning/milestones/v1.2-REQUIREMENTS.md`，当前维持 archive-ready、handoff-ready。

### Phase 18: Host-Neutral Boundary Nucleus Extraction
**Goal**: 把 boundary/auth/device 方向中已成熟的 host-neutral nucleus 从 HA adapter 语义中继续抽离，但不新建第二条 runtime story。
**Depends on**: Phase 17
**Requirements**: [CORE-01, CORE-03]
**Draft Success Criteria**:
  1. host-neutral nucleus 不再引用 HA entry/runtime adapter 类型。
  2. `LiproProtocolFacade` / `Coordinator` 仍保持正式根身份，提取只发生在 helper/service/nucleus 层。
  3. meta guards 能阻断 HA-specific imports 重新回流到 nucleus。
**Status**: Complete (`2026-03-16`)
**Plans**: 3/3 complete

Plans:
- [x] 18-01: 提炼 host-neutral contracts 与 adapter seams
- [x] 18-02: 抽离 auth/device/shared helpers 到 nucleus home
- [x] 18-03: 补齐 locality guards 与 focused regression

### Phase 19: Headless Consumer Proof & Adapter Demotion
**Goal**: 证明同一套 nucleus 能被 headless / CLI-style consumer 复用，而不是复制第二实现。
**Depends on**: Phase 18
**Requirements**: [CORE-02]
**Draft Success Criteria**:
  1. headless composition root 能走通 auth + device discovery + replay/evidence proof。
  2. HA adapter 继续只是 adapter，不再携带可复用业务根语义。
  3. 不出现 “CLI root / HA root” 双合法入口。
**Status**: Complete (`2026-03-16`)
**Plans**: 4/4 complete

Plans:
- [x] 19-01: 建立 headless composition root 与 boot contract
- [x] 19-02: 证明 auth/device/replay 使用同一 nucleus
- [x] 19-03: 继续 demote HA-only adapter assumptions
- [x] 19-04: sync long-term truth and second-root guards

### Phase 20: Remaining Boundary Family Completion
**Goal**: 把 `rest.list-envelope.v1`、`rest.schedule-json.v1`、`mqtt.topic.v1`、`mqtt.message-envelope.v1` 全部升级为 registry-backed boundary families。
**Depends on**: Phase 19
**Requirements**: [SIM-03, SIM-05]
**Draft Success Criteria**:
  1. 上述 families 全部具备 authority source、fixtures、decoder registry 与 drift assertions。
  2. inventory / authority / fixtures / manifests 不再把这些 families 记为 partial/de-scope。
  3. helper-level ad-hoc handling 进一步减少。
**Status**: Complete (`2026-03-16`)
**Plans**: 3/3 complete

Plans:
- [x] 20-01: formalize remaining REST families
- [x] 20-02: formalize remaining MQTT families
- [x] 20-03: sync inventory / fixtures / manifests / guards

### Phase 21: Replay Coverage & Exception Taxonomy Hardening
**Goal**: 把 `Phase 20` 新正式化的 families 全部纳入 replay/evidence 正式故事线，并继续把 protocol/runtime/control 关键 broad-catch 收敛为可判定的失败分类契约。
**Depends on**: Phase 20
**Requirements**: [SIM-04, ERR-02]
**Success Criteria**:
  1. replay harness、evidence pack 与 assertion families 覆盖 `rest.list-envelope`、`rest.schedule-json`、`mqtt.topic`、`mqtt.message-envelope`。
  2. 关键 `except Exception` 热点要么被收窄，要么具备统一的 documented arbitration / telemetry semantics。
  3. failure taxonomy 成为下游 observability surface 可复用的正式输入，而不是 helper-level 日志约定。
**Status**: Complete (`2026-03-16`)
**Plans**: 3/3 complete

Plans:
- [x] 21-01: expand replay and evidence across completed families
- [x] 21-02: tighten broad-catch exception arbitration
- [x] 21-03: formalize failure taxonomy contracts and guards

### Phase 22: Observability Surface Convergence & Signal Exposure
**Goal**: 把 `Phase 21` 产出的 failure taxonomy 显式暴露给 diagnostics / system health / support / developer-facing consumers，并消除消费者之间的失败语言漂移。
**Depends on**: Phase 21
**Requirements**: [OBS-03]
**Success Criteria**:
  1. diagnostics / system health / evidence export 对 auth/network/protocol/runtime failure 使用同一分类语言。
  2. support / developer / report-building surfaces 复用同一 structured signals，而不是各自拼装失败摘要。
  3. integration / meta guards 能阻断 observability consumer 再长出第二套 failure vocabulary。
**Status**: Complete (`2026-03-16`)
**Plans**: 3/3 complete

Plans:
- [x] 22-01: expose classified failure signals to diagnostics and system health
- [x] 22-02: converge support and developer evidence consumers
- [x] 22-03: harden observability contracts and integration guards

### Phase 23: Governance convergence, contributor docs and release evidence closure
**Goal**: 把 v1.2 期间新增的 replay-complete / host-neutral / observability-hardening 真相同步到 baseline / reviews / contributor docs / release evidence，并让开源协作面与 CI gate 讲同一条故事。
**Depends on**: Phase 22
**Requirements**: [GOV-16, GOV-17]
**Success Criteria**:
  1. roadmap / requirements / state / baseline / reviews / docs / templates 对 v1.2 讲同一条最终治理故事。
  2. contributor-facing docs、issue/PR templates、support/security/install/version surfaces 与当前正式架构保持一致。
  3. release evidence、CI gates 与 governance guards 共享同一 authority / verification chain。
**Status**: Complete (`2026-03-16`)
**Plans**: 3/3 complete

Plans:
- [x] 23-01: sync governance truth and authority ledgers
- [x] 23-02: align contributor docs templates and support surfaces
- [x] 23-03: close release evidence and workflow gate alignment

### Phase 24: Final milestone audit, archive readiness and v1.3 handoff prep
**Goal**: 完成 v1.2 的最终 repo audit、residual arbitration、archive-ready verification pack 与 v1.3 handoff，确保 closeout 后不残留 silent defer。
**Depends on**: Phase 23
**Requirements**: [GOV-18]
**Success Criteria**:
  1. final repo audit 能明确关闭、保留或递延全部剩余项，并写入 residual / kill / milestone closeout truth。
  2. milestone verification、evidence index、archive-ready assets 与 closeout decision bundle 完整可审计。
  3. v1.3 handoff 起点清晰，不继续携带未仲裁的 v1.2 debt。
**Status**: Complete (`2026-03-17`, revalidated after reopen)
**Plans**: 5/5 complete

Plans:
- [x] 24-01: run final repo audit and residual arbitration
- [x] 24-02: assemble milestone verification and archive bundle
- [x] 24-03: write v1.3 handoff and next-phase seed
- [x] 24-04: repair control-plane contract regressions and restore closeout gates
- [x] 24-05: resync reopened phase-24 closeout truth with fresh gate evidence

## Next Milestone Seed

### 🚧 v1.3: Quality-10 Remediation & Productization

**Milestone Goal:** 把终极复审与 `Phase 25 -> 31` 执行后的 retained cross-cutting gaps 一并转成最终可执行 closeout：先用 `Phase 25` 完成首轮路由，再由 `25.1 / 25.2 / 26 / 27 / 28 / 29 / 30 / 31` 分 tranche 落地 correctness、formal-surface、trust chain、typed/exception/hotspot 收口，最后用 `Phase 32` 统一处理 planning truth convergence、gate honesty、derived-map freshness 与 remaining quality-10 residue。

**Execution Scope:** `Phase 25 -> Phase 32`

**Seed Status:** `Phase 25 -> 32` 已于 `2026-03-18` 全部执行完成；v1.3 route 已从 final closeout tranche 收口到 execution-complete / audit-ready 状态，不再保留 `Phase 32 planned / execution-ready` 的 active story。

### Phase 25: Quality-10 remediation master plan and execution routing
**Goal**: 把终极复审中的全部关键问题制度化：逐项映射到 `25.1 / 25.2 / 26 / 27`，锁定边界、优先级、success gates 与显式排除项，确保没有任何 remaining item 继续停留在口头共识里。
**Depends on**: Phase 24
**Requirements**: [GOV-19]
**Draft Success Criteria**:
  1. 终极复审中的全部 P0 / P1 / P2 项，要么被路由到 `25.1 / 25.2 / 26 / 27`，要么被显式裁决为外部约束 / 非当前 debt，而不是 silent defer。
  2. `25.1 / 25.2 / 26 / 27` 的范围不互相踩踏：不把 trust chain、snapshot correctness、telemetry seam、hotspot slimming 混成一个黑洞 phase。
  3. reverse-engineered vendor `MD5` 登录哈希路径被记录为协议约束，而不是被误登记为仓库内部可独立消灭的密码学重构债。
**Status**: Complete
**Plans**: 4 complete

Plans:
- [x] 25-01: translate final review into routed requirement ledger and explicit exclusions
- [x] 25-02: define `25.1 / 25.2 / 26 / 27` boundaries, ordering and success gates
- [x] 25-03: sync roadmap, requirements, project, state and handoff truths
- [x] 25-04: freeze route-map validation, no-return rules and next-command handoff

### Phase 25.1: Snapshot atomicity and refresh arbitration
**Goal**: 消灭“部分失败覆盖全量状态”的设备快照风险，定义 refresh rejection / last-known-good / structured degraded 的正式仲裁语义。
**Depends on**: Phase 25
**Requirements**: [RUN-06, ERR-03]
**Draft Success Criteria**:
  1. page N 抓取失败时，partial snapshot 不会被当作新的全量 truth 发布到 coordinator state。
  2. refresh failure 的处理语义可判定、可测试，并沿正式 runtime 主链暴露，而不是靠 debug log 猜测。
  3. 与 snapshot 主链直接相关的 broad-catch / 灰区 side effects 得到收窄或结构化说明。
**Status**: Complete (`2026-03-17`)
**Plans**: 3/3 complete

Plans:
- [x] 25.1-01: enforce atomic snapshot rejection in builder and runtime
- [x] 25.1-02: wire coordinator arbitration onto the canonical refresh path
- [x] 25.1-03: close out phase truth and verification evidence

### Phase 25.2: Telemetry formal-surface closure and planning-truth sync
**Goal**: 干掉 `coordinator.client` ghost seam，让 telemetry / diagnostics / system health / planning truth 统一到正式 `protocol` surface 与诚实的 residual/derived-map 叙事。
**Depends on**: Phase 25.1
**Requirements**: [OBS-04, GOV-20]
**Draft Success Criteria**:
  1. control/exporter/diagnostics/system-health consumer 不再把 `Coordinator.client` 当合法 surface。
  2. touched authority docs、residual ledgers 与 `.planning/codebase/*` derived maps 对 closed seam 讲同一条故事。
  3. 过渡命名 / 历史 phase 叙事在 touched seam 上继续下降，不再让 formal surface 与旧术语并存。
**Status**: Complete (`2026-03-17`)
**Plans**: 3/3 complete

Plans:
- [x] 25.2-01: formalize telemetry source contracts and close the ghost seam
- [x] 25.2-02: sync baseline, residual and derived planning truth
- [x] 25.2-03: close out phase truth and verification evidence

### Phase 26: Release trust chain and open-source productization hardening
**Goal**: 把安装/发布 trust chain、support/version policy、双语与维护者冗余这些“国际成熟开源项目”要求收口成正式交付，而不再只停留在 runbook defer note。
**Depends on**: Phase 25.2
**Requirements**: [GOV-21, QLT-03]
**Draft Success Criteria**:
  1. 默认安装故事线从 `wget | bash` 转向“下载 release 资产 → 校验 → 安装”；release 具备更强的 provenance / signing / SBOM / attestation 路径或等价强身份保证。
  2. `README` / `README_zh` / `CONTRIBUTING` / `SUPPORT` / `SECURITY` / runbook / `CODEOWNERS` 对支持矩阵、维护者冗余、双语策略与产品化入口讲同一条故事。
  3. 依赖 / 兼容 / 支持策略更诚实：运行依赖、版本窗口、升级边界与支持政策被显式写明并可验证。
**Status**: Complete (`2026-03-17`)
**Plans**: 4/4 complete

Plans:
- [x] 26-01: harden installer and move supported shell installs to verified release assets
- [x] 26-02: publish installer, sbom and provenance from the existing release tail
- [x] 26-03: unify public support security contributor and productization truth
- [x] 26-04: close out phase truth and verification evidence

### Phase 27: Hotspot slimming, dependency strategy and maintainability follow-through
**Goal**: 在不引入第二 root 的前提下，继续切薄 giant roots 与纯转发层，清理过渡命名/phase residue，分裂测试巨石，并收口次级可靠性与可观测性 debt。
**Depends on**: Phase 26
**Requirements**: [HOT-05, RES-04, TST-02]
**Draft Success Criteria**:
  1. `Coordinator` / `LiproRestFacade` / forwarding layers 沿现有 `services/`、`boundary/`、child façade 继续切薄，而不是重建新 root。
  2. 过渡命名、历史 phase 注释、残留叙事噪声、次级 broad-catch 与 local persistence/observability follow-through 被继续收口。
  3. `tests/core/test_init.py`、`tests/meta/test_governance_guards.py` 一类巨石套件被拆成更稳定的专题回归面，同时维持治理门禁强度。
**Status**: Complete (`2026-03-17`)
**Plans**: 4/4 complete

Plans:
- [x] 27-01: formalize protocol-service capability port and migrate consumers
- [x] 27-02: retire coordinator forwarder cluster and clean phase residue
- [x] 27-03: sync baseline, dependency and residual truth to the new formal surface
- [x] 27-04: split test monoliths and refresh testing/toolchain truth

### Phase 28: Release trust gate completion and maintainer resilience
**Goal**: 把“诚实记录”继续推进为“制度化 hardening”：在不虚构第二维护者的前提下，补齐 maintainer continuity、release signing / scanning gate 与对外支持生命周期的机器化与可审计化。
**Depends on**: Phase 27
**Requirements**: [GOV-22, QLT-04]
**Draft Success Criteria**:
  1. release trust chain 继续从 attestation 走向更硬的 identity posture（如 signing、code-scanning gate 或等价 machine gate），并形成一致的本地/CI/runbook story。
  2. maintainer continuity、emergency access、support window / EOL / triage responsibility 被制度化到 docs/workflows，而不是只停留在“single-maintainer 现实说明”。
  3. public docs、release workflow、CODEOWNERS/runbook 与 support/security policy 对新的 continuity / trust posture 讲同一条故事。
**Status**: Complete (`2026-03-17`)
**Plans**: 3/3 complete

Plans:
- [x] 28-01: harden release identity posture and verifiable release evidence
- [x] 28-02: close code-scanning and security gate posture on the release path
- [x] 28-03: institutionalize maintainer continuity and support lifecycle truth

### Phase 29: REST child-façade slimming and test topicization
**Goal**: 沿北极星单一 protocol 主链继续切薄 `LiproRestFacade`，把 remaining hotspot 拆成更聚焦的 child collaborators / services，并把与这些热点耦合的 mega-tests 继续拆成稳定专题面。
**Depends on**: Phase 28
**Requirements**: [HOT-06, RES-05, TST-03]
**Draft Success Criteria**:
  1. `LiproRestFacade` 继续瘦身，但不会生成第二 protocol root、DI 容器或 bus story。
  2. high-churn REST families 被下沉到更清晰的 child homes，formal public surface 不因此膨胀。
  3. 与 REST hotspot 强耦合的 API mega-tests 继续按 `transport/auth`、`command/pacing`、`capability wrappers` 专题拆薄，且 touched baseline/review/test truth 对 child-façade decomposition 与 maintainability debt 讲实话。
**Status**: Complete (`2026-03-17`)
**Plans**: 3/3 complete

### Phase 30: Protocol/control typed contract tightening
**Goal**: 先在 protocol/control 这条高杠杆主链上继续收口 typed debt 与 broad-catch debt，把最靠近 boundary 与 child-façade 的宽口 contract 收回到正式 typed arbitration。
**Depends on**: Phase 29
**Requirements**: [TYP-06, ERR-04]
**Draft Success Criteria**:
  1. `core/api`、`core/protocol`、`control` touched hotspots 中的 `Any` / `type: ignore` / 宽口 contract 明显下降，并改用正式 typed ports、aliases 或 boundary contracts。
  2. 上述 touched hotspots 中 remaining broad-catch 改为 typed arbitration、documented failure contract 或显式 deferred truth，而不是继续吞掉错误语义。
  3. 这轮 tightening 不引入第二真源，也不把 helper/collaborator 回抬成 root。
**Status**: Complete (`2026-03-17`)
**Plans**: 3/3 complete

### Phase 31: Runtime/service typed budget and exception closure
**Goal**: 完成 repo-wide typed hardening 的第二半场，把 runtime/service/platform 剩余 typed backlog 与 broad-catch debt 收敛成可量化预算、明确语义与 no-growth guards。
**Depends on**: Phase 30
**Requirements**: [TYP-07, ERR-05, GOV-23]
**Draft Success Criteria**:
  1. 基于 handoff 基线 `Any=614`、`except Exception=36`、`type: ignore=12`，为 runtime/service/platform touched zones 建立预算并显著下降。
  2. remaining runtime/service broad-catch 只保留 documented fail-closed / degraded semantics；新增 catch-all regression 会被 meta guards 或 governance scripts 拦截。
  3. typed/exception budget、phase closeout truth 与 daily governance gates 形成同源 no-growth story，而不是继续依赖人工补漏。
**Status**: Complete (`2026-03-17`)
**Plans**: 4/4 complete

### Phase 32: Truth convergence, gate honesty, and quality-10 closeout
**Goal**: 把 `Phase 25 -> 31` 完成后仍残留的 planning truth 分叉、gate 口径漂移、derived-map freshness 与 hotspot/typed/exception/residual follow-through 统一收束成 final quality-10 closeout，不给下一轮再留 silent defer。
**Depends on**: Phase 31
**Requirements**: [GOV-24, QLT-05, GOV-25, GOV-26, HOT-07, TST-04, TYP-08, ERR-06, RES-06]
**Draft Success Criteria**:
  1. active planning truth（`PROJECT` / `ROADMAP` / `REQUIREMENTS` / `STATE`）与 retained handoff/audit pointers 对 `Phase 25 -> 31` complete + `Phase 32` pending 讲同一条故事，不再残留 stale continuation claim。
  2. repo-wide gate story 必须诚实：`ruff` / `mypy` / CI / contributor docs 的口径与实际执行范围一致；release identity / code-scanning / maintainer continuity surface 不再相互漂移。
  3. `.planning/codebase/*`、双语 public docs、giant roots/tests、typed/exception budgets 与 fallback/legacy residue 全部要么落到显式执行项，要么落到显式 defer truth，不再有口头约定。
  4. reverse-engineered vendor crypto constraints（如 `MD5` 登录路径）继续按协议约束诚实登记；在未证实上游可替换前，`Phase 32` 不制造伪仓库债。
**Status**: Complete (`2026-03-18`)
**Plans**: 5/5 complete

Plans:
- [x] 32-01: converge planning truth and repair requirement traceability
- [x] 32-02: align repo-wide gate honesty and toolchain reality
- [x] 32-03: converge release identity posture, maintainer continuity, and contributor templates
- [x] 32-04: refresh codebase-map freshness, authority disclaimers, and bilingual public-doc sync
- [x] 32-05: close hotspot slimming, mega-test topicization, typed/exception debt, and residual honesty

## Post-v1.3 Continuation Seed

### Phase 33: Contract-truth unification, hotspot slimming, and productization hardening
**Goal**: 把 `8.8/10` 终审仍残留的 runtime contract 双真源、control 去回路、giant roots / forwarding layers、broad-catch、CI/perf gate 漂移与深层开源产品化短板统一收束成下一轮 quality-10 hardening tranche，在不引入第二 root 的前提下把仓库从“高阶工程仓库”继续推进到“国际成熟开源产品”水位。
**Depends on**: Phase 32
**Requirements**: [ARC-03, CTRL-07, HOT-08, ERR-07, TST-05, QLT-06, GOV-27, GOV-28, QLT-07]
**Draft Success Criteria**:
  1. runtime public surface 真源统一到单一合同；control-plane locator / telemetry / read-model 变为 acyclic、port-based、snapshot-pure story。
  2. `LiproRestFacade` / `LiproProtocolFacade` / `Coordinator` / `Snapshot` / `CommandResult` 等 giant roots 或 giant helpers 继续沿现有 seams 切薄，而不是长出第二 orchestration root 或 helper folklore。
  3. broad-catch、local/CI/pre-push/perf gates、release evidence posture 与 dependency/compatibility story 收敛为 machine-checkable truth，不再残留重复测试、迟到反馈或文档强于现实的 drift。
  4. control exports、naming residue、empty compat shells、mega-tests、深层双语 docs、maintainer continuity 与 signing/code-scanning roadmap 全部被正式路由到可执行计划，不再停留在口头终审意见。
**Status**: Complete (`2026-03-18`)
**Plans**: 6/6 complete

Plans:
- [x] 33-01: unify runtime contract truth and purify control read models (completed 2026-03-18)
- [x] 33-02: remove control-plane reflection loops and shrink over-wide exports (completed 2026-03-18)
- [x] 33-03: slim giant roots and forwarding clusters along formal seams (completed 2026-03-18)
- [x] 33-04: converge exception policy, typed debt, and residual naming truth (completed 2026-03-18)
- [x] 33-05: harden CI/pre-push/benchmark/release-evidence gates and reproducibility posture (completed 2026-03-18)
- [x] 33-06: topicize remaining mega-tests and close deep-doc / continuity productization gaps (completed 2026-03-18)
