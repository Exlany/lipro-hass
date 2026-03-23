# Roadmap: Lipro-HASS North Star Evolution

## Milestones

- ✅ **v1.0 North Star Rebuild** - Phases 1-7 (+ 1.5 / 2.5 / 2.6), shipped 2026-03-13, archive: `.planning/milestones/v1.0-ROADMAP.md`
- ✅ **v1.1 Protocol Fidelity & Operability** - Phases 7.1-17 complete; final audit complete; milestone snapshots archived at `.planning/milestones/v1.1-ROADMAP.md` / `.planning/milestones/v1.1-REQUIREMENTS.md` (updated 2026-03-16)
- ✅ **v1.2 Host-Neutral Core & Replay Completion** - Phases 18-24 complete after Phase 24 reopen revalidation; 24 plans complete; milestone snapshots archived at `.planning/milestones/v1.2-ROADMAP.md` / `.planning/milestones/v1.2-REQUIREMENTS.md`; `v1.3` handoff-ready (revalidated 2026-03-17)
- ✅ **v1.4 Sustainment, Trust Gates & Final Hotspot Burn-down** - Phases 34-39 shipped 2026-03-19; milestone audit: `.planning/v1.4-MILESTONE-AUDIT.md`; evidence index: `.planning/reviews/V1_4_EVIDENCE_INDEX.md`; snapshots archived at `.planning/milestones/v1.4-ROADMAP.md` / `.planning/milestones/v1.4-REQUIREMENTS.md`; local tag: `v1.4`
- ✅ **v1.5 Governance Truth Consolidation & Control-Surface Finalization** - Phase 40 shipped 2026-03-19; milestone audit: `.planning/v1.5-MILESTONE-AUDIT.md`; evidence index: `.planning/reviews/V1_5_EVIDENCE_INDEX.md`; snapshots archived at `.planning/milestones/v1.5-ROADMAP.md` / `.planning/milestones/v1.5-REQUIREMENTS.md`; local tag: `v1.5`
- ✅ **v1.6 Delivery Trust Hardening, Runtime Boundary Decoupling & Maintainability Closure** - Phases 42-45 closed out on 2026-03-20 from the formal `41-REMEDIATION-ROADMAP.md` route; milestone audit: `.planning/v1.6-MILESTONE-AUDIT.md`; evidence index: `.planning/reviews/V1_6_EVIDENCE_INDEX.md`; snapshots archived at `.planning/milestones/v1.6-ROADMAP.md` / `.planning/milestones/v1.6-REQUIREMENTS.md`
- ✅ **v1.7 Full-Spectrum Repository Audit, Open-Source Maturity & Remediation Routing** - Phase 46 audit executed on 2026-03-20; Phase 47 -> 50 completed on 2026-03-21 with promoted closeout evidence; formalized follow-up route complete
- ✅ **v1.8 Operational Continuity Automation, Formal-Root Sustainment & Hotspot Round 2** - formal milestone opened on 2026-03-21 from post-Phase-50 audit arbitration; Phases 51 -> 55 completed on 2026-03-21 with promoted closeout evidence and ready for archive / next-milestone arbitration
- ✅ **v1.9 Shared Backoff Neutralization & Cross-Plane Retry Hygiene** - formal milestone opened on 2026-03-22 from the explicit Phase 56+ residual carry-forward; Phase 56 completed on 2026-03-22 with promoted closeout evidence and now serves as the closeout-ready seed baseline for v1.10
- ✅ **v1.13 Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence** - `Phase 60 -> 62` archived on 2026-03-22; milestone audit: `.planning/v1.13-MILESTONE-AUDIT.md`; evidence index: `.planning/reviews/V1_13_EVIDENCE_INDEX.md`; snapshots archived at `.planning/milestones/v1.13-ROADMAP.md` / `.planning/milestones/v1.13-REQUIREMENTS.md`
- ✅ **v1.12 Verification Localization & Governance Guard Topicization** - `Phase 59` archived on 2026-03-22; milestone audit: `.planning/v1.12-MILESTONE-AUDIT.md`; evidence index: `.planning/reviews/V1_12_EVIDENCE_INDEX.md`; snapshots archived at `.planning/milestones/v1.12-ROADMAP.md` / `.planning/milestones/v1.12-REQUIREMENTS.md`
- ✅ **v1.11 Repository Audit Refresh & Next-Wave Remediation Routing** - formal milestone opened on 2026-03-22 from the renewed full-repository audit request; Phase 58 completed on 2026-03-22 with refreshed repo-wide audit evidence and now serves as the closeout-ready seed baseline for v1.12
- ✅ **v1.10 Command-Result Typed Outcome & Reason-Code Hardening** - formal milestone opened on 2026-03-22 from the Phase 56 deferred follow-up route; Phase 57 completed on 2026-03-22 with promoted closeout evidence and now serves as the closeout-ready seed baseline for v1.11

- 🚧 **v1.14 Governance Truth Realignment, Typed Runtime Access & Final Hidden-Root Closure** - formal milestone opened on 2026-03-23 from `v1.13` archived evidence; `Phase 63 -> 66` completed on 2026-03-23 and returned the milestone to closeout-ready status after governance latest-pointer / release-target fidelity alignment, adapter-root cleanup, runtime-access de-reflection, runtime alias projection, anonymous-share outcome-contract closure, and focused protocol seam hardening

## Required Phase Outputs

每个 phase 完成时，除了代码与测试，还必须显式更新或确认以下输出：

- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/reviews/PROMOTED_PHASE_ASSETS.md`（`.planning/phases/**` 只有这里显式登记的资产才算长期治理 / CI 证据；未登记 phase 文件继续按执行痕迹处理）
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
  2. `session_state.py` 只剩 `RestSessionState`，`power_service.py` / protocol/runtime outlet-power path 只承认 explicit row/list contract，不再产生 synthetic wrapper。
  3. MQTT concrete transport 的 canonical 名称统一为 `MqttTransport`，且 root/core package no-export bans 与 locality guard 已同步到 baseline/tests。
  4. `ROADMAP / REQUIREMENTS / STATE / PROJECT / baseline / review ledgers / AGENTS / developer_architecture / milestone audit` 对 Phase 17 讲同一条完成态故事线。
**Plans:** 4/4 complete

Plans:
- [x] 17-01: api residual spine retirement and endpoint-port convergence (completed 2026-03-15)
- [x] 17-02: auth session and outlet-power contract convergence (completed 2026-03-15)
- [x] 17-03: mqtt transport naming demotion and locality guard hardening (completed 2026-03-15)
- [x] 17-04: phase 17 governance closeout and final repo audit (completed 2026-03-15)


## Current Milestone

### 🟢 v1.9: Shared Backoff Neutralization & Cross-Plane Retry Hygiene

**Milestone Goal:** 在不重开第二条 root / retry-policy story 的前提下，把 generic exponential backoff primitive 从 `request_policy.py` 的跨平面 utility 泄漏中抽离，迁入 neutral shared helper home，并将 residual closeout 固化为 machine-checkable current truth。

**Execution Scope:** `Phase 56`（1 phase / 3 plans）

**Current Status:** `Phase 56` 已于 `2026-03-22` 完成执行与验证；`custom_components/lipro/core/utils/backoff.py` 现成为 neutral shared exponential-backoff primitive home，`RequestPolicy` 只再承担 API-local `429` / busy / pacing truth，而 `command` / `runtime` / `mqtt` callers 已切断对 `request_policy.py` 的 generic helper 依赖。默认下一步是执行 `$gsd-complete-milestone v1.9`。

**Milestone Outcomes:**
1. `Generic backoff helper leak` 已从 active residual family 转为 closed residual，且关闭理由已写回 baseline / review truth。
2. `RequestPolicy` 的 ownership 更诚实：API policy truth 留在 API plane，neutral primitive 则进入 `core/utils/backoff.py`。
3. `v1.9` 当前故事、promoted phase assets 与 focused meta guards 已同步收口到 `Phase 56` closeout。


### Phase 18: Host-Neutral Boundary Nucleus Extraction
**Goal**: 把 boundary/auth/device 方向中已成熟的 host-neutral nucleus 从 HA adapter 语义中继续抽离，但不新建第二条 runtime story。
**Depends on**: Phase 17
**Requirements**: [CORE-01, CORE-03]
**Success Criteria**:
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
**Success Criteria**:
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
**Success Criteria**:
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
**Success Criteria**:
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
**Success Criteria**:
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
**Success Criteria**:
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
**Success Criteria**:
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
**Success Criteria**:
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
**Success Criteria**:
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
**Success Criteria**:
  1. `LiproRestFacade` 继续瘦身，但不会生成第二 protocol root、DI 容器或 bus story。
  2. high-churn REST families 被下沉到更清晰的 child homes，formal public surface 不因此膨胀。
  3. 与 REST hotspot 强耦合的 API mega-tests 继续按 `transport/auth`、`command/pacing`、`capability wrappers` 专题拆薄，且 touched baseline/review/test truth 对 child-façade decomposition 与 maintainability debt 讲实话。
**Status**: Complete (`2026-03-17`)
**Plans**: 3/3 complete

### Phase 30: Protocol/control typed contract tightening
**Goal**: 先在 protocol/control 这条高杠杆主链上继续收口 typed debt 与 broad-catch debt，把最靠近 boundary 与 child-façade 的宽口 contract 收回到正式 typed arbitration。
**Depends on**: Phase 29
**Requirements**: [TYP-06, ERR-04]
**Success Criteria**:
  1. `core/api`、`core/protocol`、`control` touched hotspots 中的 `Any` / `type: ignore` / 宽口 contract 明显下降，并改用正式 typed ports、aliases 或 boundary contracts。
  2. 上述 touched hotspots 中 remaining broad-catch 改为 typed arbitration、documented failure contract 或显式 deferred truth，而不是继续吞掉错误语义。
  3. 这轮 tightening 不引入第二真源，也不把 helper/collaborator 回抬成 root。
**Status**: Complete (`2026-03-17`)
**Plans**: 3/3 complete

### Phase 31: Runtime/service typed budget and exception closure
**Goal**: 完成 repo-wide typed hardening 的第二半场，把 runtime/service/platform 剩余 typed backlog 与 broad-catch debt 收敛成可量化预算、明确语义与 no-growth guards。
**Depends on**: Phase 30
**Requirements**: [TYP-07, ERR-05, GOV-23]
**Success Criteria**:
  1. 基于 handoff 基线 `Any=614`、`except Exception=36`、`type: ignore=12`，为 runtime/service/platform touched zones 建立预算并显著下降。
  2. remaining runtime/service broad-catch 只保留 documented fail-closed / degraded semantics；新增 catch-all regression 会被 meta guards 或 governance scripts 拦截。
  3. typed/exception budget、phase closeout truth 与 daily governance gates 形成同源 no-growth story，而不是继续依赖人工补漏。
**Status**: Complete (`2026-03-17`)
**Plans**: 4/4 complete

### Phase 32: Truth convergence, gate honesty, and quality-10 closeout
**Goal**: 把 `Phase 25 -> 31` 完成后仍残留的 planning truth 分叉、gate 口径漂移、derived-map freshness 与 hotspot/typed/exception/residual follow-through 统一收束成 final quality-10 closeout，不给下一轮再留 silent defer。
**Depends on**: Phase 31
**Requirements**: [GOV-24, QLT-05, GOV-25, GOV-26, HOT-07, TST-04, TYP-08, ERR-06, RES-06]
**Success Criteria**:
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
**Success Criteria**:
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

## v1.4: Sustainment, Trust Gates & Final Hotspot Burn-down

> `v1.3` milestone audit 已确认 `no critical gaps` 但保留显式 retained tech debt；`Phase 34 -> 39` 已将这批问题按单一北极星主链完成收口，并在 `2026-03-19` 通过 `v1.4` milestone audit 后正式进入 archived / evidence-ready 状态。

### Phase 34: Continuity and hard release gates
**Goal**: 把单维护者连续性与 release trust 从“诚实说明”推进到“可演练、可阻断、可审计”：建立真实的 continuity / custody / freeze contract，并为 artifact signing 与 hard code-scanning gate 做最终路由。
**Depends on**: Phase 33
**Requirements**: [GOV-29, QLT-08]
**Success Criteria**:
  1. 未签名或未通过新增 hard gate 的 release asset 不能被包装成稳定 release；release workflow、README / README_zh、SUPPORT、SECURITY 与 runbook 对 trust posture 口径完全一致。
  2. maintainer continuity 不再只有“单维护者现实”的诚实记录，而是具备 delegate / custody / freeze escalation 的正式合同与证据。
  3. continuity / release truth 至少形成一轮可追溯的 drill、checklist 或 guard 证据，而不是只存在于叙述性文档。
**Status**: Complete (`2026-03-18`)
**Plans**: 3/3 complete

Plans:
- [x] 34-01: formalize continuity, custody, and freeze-escalation contracts (completed 2026-03-18)
- [x] 34-02: add artifact signing and hard release-trust gates (completed 2026-03-18)
- [x] 34-03: converge public docs, runbook, CODEOWNERS, and guards on continuity/release truth (completed 2026-03-18)

### Phase 35: Protocol hotspot final slimming
**Goal**: 继续拆薄 `LiproRestFacade` 与 `LiproProtocolFacade` 两个协议热点，但严格沿现有 protocol seams 下沉职责，不长出第二 root，不把 forwarding glue 合法化成永久结构。
**Depends on**: Phase 34
**Requirements**: [HOT-09, RES-07]
**Success Criteria**:
  1. `custom_components/lipro/core/api/client.py` 与 `custom_components/lipro/core/protocol/facade.py` 继续显著瘦身，职责按 transport / auth / command / capability 等协作者切开。
  2. public surface 只减不增；protocol / API 定向回归与 surface guards 继续全绿。
  3. compat / forwarding residue、反射/私有实现细节依赖与命名残留被进一步删除、隔离或显式下沉，不再在 root façade 层漂浮。
**Status**: Complete (`2026-03-18`)
**Plans**: 3/3 complete

Plans:
- [x] 35-01: split REST child-façade collaborators along formal seams (completed 2026-03-18)
- [x] 35-02: slim protocol-facade forwarding clusters and sync public-surface truth (completed 2026-03-18)
- [x] 35-03: add hotspot guardrails and targeted protocol regressions (completed 2026-03-18)

### Phase 36: Runtime root and exception burn-down
**Goal**: 收薄 `Coordinator` 运行根，并把生产宽异常从当前存量压到可守护阈值；所有新增失败语义都必须落到 typed arbitration、documented degraded contract 或 fail-closed path。
**Depends on**: Phase 35
**Requirements**: [HOT-10, ERR-08, TYP-09]
**Success Criteria**:
  1. `custom_components/lipro/core/coordinator/coordinator.py` 显著瘦身，runtime/service clusters 的 home 更明确，但正式 runtime root 仍只有一条。
  2. 生产 `except Exception` 存量明显下降，核心热点清零或收敛到 machine-guarded no-growth budget。
  3. runtime/service/platform touched-zone 的 typed budget 与 exception policy 继续统一到单一治理故事。
**Status**: Complete (`2026-03-18`)
**Plans**: 3/3 complete

Plans:
- [x] 36-01: extract coordinator runtime/service clusters along existing seams (completed 2026-03-18)
- [x] 36-02: burn down broad exceptions into typed arbitration and guarded degraded contracts (completed 2026-03-18)
- [x] 36-03: refresh runtime typed-budget and no-growth evidence (completed 2026-03-18)

### Phase 37: Test topology and derived-truth convergence
**Goal**: 完成巨石测试第三波 topicization，并把 `.planning/codebase/*`、测试策略、verification truth 与实际套件布局重新拉回单一故事，避免 derived-map 再漂移。
**Depends on**: Phase 36
**Requirements**: [TST-06, GOV-30, QLT-09]
**Success Criteria**:
  1. 剩余巨石测试被拆成更稳定、可局部执行的专题套件，失败定位速度明显提升。
  2. `.planning/codebase/*`、测试策略文档、verification matrix、public docs entry topology 与实际命令/目录结构保持一致，并有 drift guard 约束。
  3. benchmark 形成预算或基线语义，governance tests 降低 prose-coupled 高噪音断言，最终 closeout 证据完整，为后续 fresh audit 奠定稳定基线。
**Status**: Complete (`2026-03-18`)
**Plans**: 3/3 complete

Plans:
- [x] 37-01: topicize remaining mega-tests into stable topical suites (completed 2026-03-18)
- [x] 37-02: converge derived maps, testing strategy, and verification truth (completed 2026-03-18)
- [x] 37-03: add drift guards and closeout evidence for test-topology changes (completed 2026-03-18)

### Phase 38: External-boundary residual retirement and quality-signal hardening
**Goal**: 关闭最后一条 external-boundary naming residual，并把 quality-signal / governance closeout truth 收紧到更诚实、可机审的单一故事线。
**Depends on**: Phase 37
**Requirements**: [RES-08, QLT-10, GOV-31]
**Success Criteria**:
  1. firmware external-boundary 语义统一为 bundled local trust-root asset + remote advisory payload，保留历史文件名但不再误导 authority truth。
  2. `coverage_diff.py` / CI / `CONTRIBUTING.md` / `.planning/codebase/TESTING.md` 讲同一条质量故事：coverage floor 始终 blocking、diff 仅在显式 baseline 下执行、benchmark 继续 advisory 但以 artifact 形式可审计。
  3. governance closeout / phase-history guards 进一步偏向 `ROADMAP` / `REQUIREMENTS` / command anchors，减少对 `PROJECT` / `STATE` 句型复述的耦合，并形成 fresh-audit baseline。
**Status**: Complete (`2026-03-18`)
**Plans**: 3/3 complete

Plans:
- [x] 38-01: retire external-boundary advisory naming residual with honest trust-root terminology (completed 2026-03-18)
- [x] 38-02: convert quality-signal wording into machine-checkable contracts (completed 2026-03-18)
- [x] 38-03: reduce governance prose-coupling and lock fresh-audit closeout evidence (completed 2026-03-18)

### Phase 39: Governance current-story convergence, control-home clarification, and mega-test decomposition

**Goal:** 把 current-story canonical docs、control/services formal role、dead protocol shell、authority asset naming、governance closeout evidence 与剩余 mega-test topology 全部收口到一条诚实、可验证、可归档的 `v1.4` 故事。
**Requirements**: [GOV-32, DOC-03, CTRL-08, RES-09, TST-07]
**Depends on:** Phase 38
**Success Criteria**:
  1. `ROADMAP / REQUIREMENTS / STATE / PROJECT` 对 `v1.4 / Phase 39 complete / next command` 讲同一条 current story，coverage / traceability 算术无误。
  2. `docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`docs/developer_architecture.md`、review ledgers 与 promoted assets 清楚承认 `custom_components/lipro/control/` 是 formal control-plane home，`services/` 只承担 declarations / adapters / helpers。
  3. `custom_components/lipro/core/protocol/compat.py` 退场，authority fixtures / replay manifests / guards / readmes 完成单命名收口；remaining mega-tests topicize 成低噪声专题面并通过完整 hard gates。
**Status**: Complete (`2026-03-19`)
**Plans**: 6/6 complete

Plans:
- [x] 39-01: converge roadmap requirements state and project onto one current story (completed 2026-03-19)
- [x] 39-02: refresh authority docs and clarify control-home topology (completed 2026-03-19)
- [x] 39-03: retire protocol dead shell and converge device-list authority assets (completed 2026-03-19)
- [x] 39-04: topicize device mqtt config-flow and anonymous-share mega-tests (completed 2026-03-19)
- [x] 39-05: topicize governance mega-tests and promote phase 39 closeout evidence (completed 2026-03-19)
- [x] 39-06: run phase-39 full validation gates and finalize closeout evidence (completed 2026-03-19)


## v1.5: Governance Truth Consolidation & Control-Surface Finalization

> `v1.5` 已于 2026-03-19 完成 milestone audit、archive promotion 与 local tag；以下保留 `Phase 40` 的最终路线快照，archive snapshots 见 `.planning/milestones/v1.5-ROADMAP.md` / `.planning/milestones/v1.5-REQUIREMENTS.md`，审计裁决见 `.planning/v1.5-MILESTONE-AUDIT.md`。

**Archive status:** `shipped / archived (2026-03-19)`
**Archive assets:** `.planning/v1.5-MILESTONE-AUDIT.md`, `.planning/milestones/v1.5-ROADMAP.md`, `.planning/milestones/v1.5-REQUIREMENTS.md`, `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-SUMMARY.md`, `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-VERIFICATION.md`, `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-VALIDATION.md`, local tag `v1.5`

### Phase 40: Governance truth consolidation, runtime-access convergence, and service execution unification

**Goal:** 把 active truth / archive snapshot / derived map / compatibility note 的资产分层重新收口到单一 current story；把 control/services 对 runtime 的读取统一回 `runtime_access`；把 schedule/service auth-error 执行链收敛到正式 shared executor，并顺手清理 touched naming residue 与 stale terminology。
**Requirements**: [GOV-33, CTRL-09, ERR-10, RES-10, QLT-11]
**Depends on:** Phase 39
**Success Criteria**:
  1. `PROJECT / ROADMAP / REQUIREMENTS / STATE`、`docs/README.md` 与 baseline 三件套对 authority precedence、active truth、archive snapshot 与 promoted phase assets 讲同一条 current story，并吸收 `V1_4_EVIDENCE_INDEX.md` / `v1.4-MILESTONE-AUDIT.md` / `Phase 38-39` closeout contract。
  2. continuity / release-trust / install-path / support-routing 事实收口到 machine-readable governance registry；README、README_zh、CONTRIBUTING、SUPPORT、SECURITY、TROUBLESHOOTING、runbook 与 issue/PR templates 由守卫强制同步，且补齐 break-glass verify-only / non-publish rehearsal 语义。
  3. `runtime_access` 成为 control/services 的单一 runtime read-model：diagnostics/device lookup/maintenance 不再各自复制 coordinator 枚举或设备读取逻辑；`schedule.py` 复用 shared service execution auth/error chain；touched `client` / `forwarding` / `mixin` terminology 收口到 `protocol` / `port` / `facade` / `operations` 语义。
**Status**: Complete (`2026-03-19`)
**Plans**: 7/7 complete

- [x] **Phase 40:** Governance truth consolidation, runtime-access convergence, and service execution unification (completed 2026-03-19)

Plans:
- [x] 40-01: align current-story docs with active truth and archive identity (completed 2026-03-19)
- [x] 40-02: sync baseline authority and governance guards with v1.5 truth (completed 2026-03-19)
- [x] 40-03: add governance registry and release/support/runbook truth (completed 2026-03-19)
- [x] 40-04: sync contributor templates and drift guards to registry-backed truth (completed 2026-03-19)
- [x] 40-05: converge runtime-access read model and harden runtime-only guards (completed 2026-03-19)
- [x] 40-06: unify shared service execution contract for schedule flows (completed 2026-03-19)
- [x] 40-07: retire touched naming residue and finalize review-guard sync (completed 2026-03-19)


**Milestone status:** `Archived / evidence-ready`
**Closeout assets:** `.planning/v1.5-MILESTONE-AUDIT.md`, `.planning/reviews/V1_5_EVIDENCE_INDEX.md`, `.planning/milestones/v1.5-ROADMAP.md`, `.planning/milestones/v1.5-REQUIREMENTS.md`, `.planning/phases/40-governance-truth-consolidation-runtime-access-convergence-and-service-execution-unification/40-VALIDATION.md`, local tag `v1.5`

## v1.6: Delivery Trust Hardening, Runtime Boundary Decoupling & Maintainability Closure

> `v1.6` 已于 `2026-03-20` 完成 milestone audit 与 archive promotion；以下保留 `Phase 42 -> 45` 的最终路线快照，archive snapshots 见 `.planning/milestones/v1.6-ROADMAP.md` / `.planning/milestones/v1.6-REQUIREMENTS.md`，审计裁决见 `.planning/v1.6-MILESTONE-AUDIT.md`，证据入口见 `.planning/reviews/V1_6_EVIDENCE_INDEX.md`。

**Archive status:** `archived / evidence-ready (2026-03-20)`
**Route source:** `.planning/phases/41-full-spectrum-architecture-code-quality-and-open-source-audit/41-REMEDIATION-ROADMAP.md`
**Default next command:** `$gsd-new-milestone`
**Closeout assets:** `.planning/v1.6-MILESTONE-AUDIT.md`, `.planning/reviews/V1_6_EVIDENCE_INDEX.md`, `.planning/milestones/v1.6-ROADMAP.md`, `.planning/milestones/v1.6-REQUIREMENTS.md`, `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-SUMMARY.md`, `.planning/phases/45-hotspot-decomposition-and-typed-failure-semantics/45-VERIFICATION.md`

### Phase 42: Delivery trust gates and validation hardening

**Goal:** 补齐 maintainer delegate / security fallback、release artifact install smoke、total + changed-surface coverage 双门禁、local-vs-CI parity 与 compatibility / deprecation preview lane，让“仓库能发布”升级为“产物可验证、流程可接班、漂移可前探”。
**Requirements**: [GOV-34, QLT-12, QLT-13, QLT-14]
**Depends on:** Phase 40
**Success Criteria**:
  1. `SUPPORT.md`、`SECURITY.md`、`.github/CODEOWNERS`、runbook 与 issue/PR templates 对 maintainer delegate / fallback / freeze escalation 讲同一条故事。
  2. release workflow 对 release zip 运行 install/uninstall smoke；coverage gate 同时约束 total coverage 与 changed-surface coverage；本地与 CI 命令矩阵语义一致。
  3. scheduled preview lane 能提前暴露 HA / dependency deprecation drift，并形成 machine-readable warning signal。
**Status**: Complete (`2026-03-20`)
**Plans**: 4/4 complete
- [x] 42-01: align continuity ownership and fallback disclosure truth (completed 2026-03-20)
- [x] 42-02: add release artifact install smoke and tagged-Python parity (completed 2026-03-20)
- [x] 42-03: enforce total-plus-diff coverage and local/CI parity (completed 2026-03-20)
- [x] 42-04: add compatibility preview lane and deprecation signal truth (completed 2026-03-20)

### Phase 43: Control-services boundary decoupling and typed runtime access

**Goal:** 解开 `control/` ↔ `services/` 双向缠绕，把 `RuntimeAccess` 升级为 typed read-model contract，并把 `services/maintenance.py` 承载的 runtime infra 迁回正确 formal home。
**Requirements**: [ARC-04, CTRL-10, RUN-07]
**Depends on:** Phase 42
**Success Criteria**:
  1. `control/` 与 `services/` 收敛为单向依赖合同；helper surface 不再反客为主或反向定义 runtime truth。
  2. `RuntimeAccess` 暴露 typed public read-model API；diagnostics / system health / maintenance / lookup 消费者不再依赖反射、`MagicMock` 形状或私有字段。
  3. runtime infra 与 service helper 各回 formal home；`maintenance.py` 不再承担 entry reload / listener / coordinator-traversal 等跨层职责。
**Status**: Complete (`2026-03-20`)
**Plans**: 4/4 complete
- [x] 43-01: tighten RuntimeAccess into a typed public read-model (completed 2026-03-20)
- [x] 43-02: relocate maintenance-owned runtime infra to formal control homes (completed 2026-03-20)
- [x] 43-03: converge control-services collaboration onto a one-way dependency contract (completed 2026-03-20)
- [x] 43-04: codify the new control-runtime-service boundary in docs and guards (completed 2026-03-20)

### Phase 44: Governance asset pruning and terminology convergence

**Goal:** 收紧 `.planning/phases/**` 的 execution-trace / promoted-asset 边界，统一 façade 时代官方术语，拆 contributor fast-path 与 maintainer appendix，并把双语边界策略明文化。
**Requirements**: [GOV-35, RES-11, DOC-04]
**Depends on:** Phase 43
**Success Criteria**:
  1. `.planning/phases/**` 默认仅是 execution trace，只有 allowlist 资产进入长期治理 / CI truth；文档、review ledgers 与守卫不再把 trace 误写成 authority。
  2. current docs / ADR / comments 完成 `client / mixin / forwarding` → `protocol / facade / operations` 术语收口，旧术语只留在历史资产或 residual ledger。
  3. contributor fast-path、maintainer appendix 与 bilingual policy 可链接、可守卫、低噪声，减少外部贡献者过早接触维护者治理术语。
**Status**: Complete (`2026-03-20`)
**Plans**: 4/4 complete
- [x] 44-01: tighten phase-asset promotion and authority boundaries (completed 2026-03-20)
- [x] 44-02: converge current repository terminology onto protocol-facade-operations language (completed 2026-03-20)
- [x] 44-03: split contributor fast-path from maintainer appendices and codify bilingual boundaries (completed 2026-03-20)
- [x] 44-04: close the governance story across ledgers indexes and guards (completed 2026-03-20)

### Phase 45: Hotspot decomposition and typed failure semantics

**Goal:** 拆 `rest_decoder_support.py`、`diagnostics_api_service.py`、`share_client.py`、`message_processor.py` 等高复杂度热点，压缩 forwarding 链，并把 bool-fail 升级为 typed result / reason code，同时把 benchmark 从“留证据”升级为“防回退”。
**Requirements**: [HOT-11, ERR-11, TYP-10, QLT-15]
**Depends on:** Phase 44
**Success Criteria**:
  1. 高复杂度热点沿现有正式 seams 切薄；长函数、弱语义 fallback 与多层 forwarding 链明显下降，且 public surface 不扩张。
  2. diagnostics / share / message / protocol touched-zone 改用 typed result / reason code；失败语义可被日志、diagnostics 与测试稳定消费。
  3. benchmark 具备 baseline compare / threshold warning / no-regression gate 语义，不再只是上传产物。
**Status**: Complete (`2026-03-20`)
**Plans**: 4/4 complete
- [x] 45-01: decompose the protocol decoder hotspot without expanding public surface (completed 2026-03-20)
- [x] 45-02: slim diagnostics-share hotspots and replace weak bool-fail paths with typed outcomes (completed 2026-03-20)
- [x] 45-03: give MQTT message handling typed outcomes and a no-growth typed-budget guard (completed 2026-03-20)
- [x] 45-04: upgrade benchmark evidence into governed baseline threshold and no-regression truth (completed 2026-03-20)

## v1.7: Full-Spectrum Repository Audit, Open-Source Maturity & Remediation Routing

> `v1.7` 以 `.planning/v1.6-MILESTONE-AUDIT.md`、`.planning/reviews/V1_6_EVIDENCE_INDEX.md` 与 archived snapshots 为 shipped baseline；首个目标不是立刻再开大规模重构，而是完成一轮覆盖全仓 Python / docs / config / tests / governance assets 的正式终极审阅，并把结论压成 `Phase 47+` 的可执行整改路线。

**Milestone status:** `Phase 46 audit complete; Phase 47 -> 50 complete (2026-03-21)`
**Default next command:** `$gsd-progress`（`Phase 50` 已完成并提升 closeout evidence；formalized route 已闭环）

### Phase 46: Exhaustive repository audit, standards conformance, and remediation routing

**Goal:** 以北极星主链、国际开源最佳实践与高级维护性标准，对 `lipro-hass` 的全部 Python 代码、测试、文档、配置与治理资产做一次不留盲点的 repo-wide 审阅，形成文件级证据、架构评分、热点定位与 `Phase 47+` 正式整改路线。
**Requirements**: [GOV-36, ARC-05, DOC-05, RES-12, TST-08, TYP-11, QLT-16]
**Depends on:** Phase 45
**Success Criteria**:
  1. 每个 Python / docs / config / workflow / planning truth 文件都被纳入 file-level 审阅范围，并按 formal root / adapter / helper / test / governance / archive 等身份分类，给出 strengths / gaps / action verdict。
  2. formal root hotspots、命名规范、目录结构、mega-test topology、typed debt、broad exception 使用、OSS contributor surface 与 release/support/security paths 都完成可追溯评分，并对照 north-star 与优秀开源案例给出清晰优先级。
  3. `Phase 46` 产出 promoted audit evidence、全仓审阅总报告与 `Phase 47+` remediation roadmap；后续整改不再依赖零散记忆或 conversation-only 结论。
**Status**: Complete (`2026-03-20`)
**Plans**: 4/4 complete
**Promoted audit package**: `46-AUDIT.md`, `46-SCORE-MATRIX.md`, `46-REMEDIATION-ROADMAP.md`, `46-SUMMARY.md`, `46-VERIFICATION.md`
**Follow-up route source**: `.planning/phases/46-exhaustive-repository-audit-standards-conformance-and-remediation-routing/46-REMEDIATION-ROADMAP.md`
**Formalized execution route**: `$gsd-plan-phase 47` → `$gsd-execute-phase 47`

### Phase 47: Continuity contract, governance entrypoint compression, and tooling discoverability

**Goal:** 把 `Phase 46` 审阅中仍分散的 continuity / docs index / tooling discoverability 问题压成单一正式合同：公开入口与维护者附录分层更清晰，scripts active-vs-deprecated 可发现，release custody / delegate / freeze / restoration 真相在 docs / templates / registry / metadata 中一致。
**Depends on:** Phase 46
**Requirements**: [GOV-37, DOC-06]
**Success Criteria**:
  1. `SUPPORT.md`、`SECURITY.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.github/CODEOWNERS`、issue/PR templates 与 governance registry 对 continuity / custody / delegate / freeze / restoration 讲同一条故事线，且不暗示 hidden delegate。
  2. `docs/README.md` 成为更显式的 documentation index；`project.urls.Documentation` 与公开文档入口对齐；maintainer-only 文档不再在 public fast path 第一层与普通用户入口混层。
  3. `scripts/` active tooling 与 retired compatibility stubs 有明确索引或自描述；stable-vs-preview wording 继续诚实，不削弱 verified release assets contract。
**Status**: Complete (`2026-03-21`)
**Plans**: 4/4 complete
**Promoted closeout package**: `47-SUMMARY.md`, `47-VERIFICATION.md`

Plans:
- [x] 47-01: formalize continuity truth across support, security, runbook, and CODEOWNERS (completed 2026-03-21)
- [x] 47-02: compress public documentation entrypoints and bilingual routing discoverability (completed 2026-03-21)
- [x] 47-03: classify active tooling versus retired compatibility stubs and sync package metadata (completed 2026-03-21)
- [x] 47-04: add governance guards for continuity, docs index, and tooling discoverability (completed 2026-03-21)

### Phase 48: Runtime-access and formal-root hotspot decomposition without public-surface drift

**Goal:** 沿现有正式 seams 继续给 `RuntimeAccess`、`Coordinator`、`__init__.py` 与 `EntryLifecycleController` 限流，减少 decision density，同时保持 lazy wiring、public surface 与 control/runtime boundary guard 不漂移。
**Depends on:** Phase 47
**Requirements**: [RUN-08, ARC-06]
**Success Criteria**:
  1. `control/runtime_access.py` 的 read-model / telemetry / system-health 逻辑被 topicize，控制面消费者继续通过正式入口读取 runtime 状态。
  2. `Coordinator`、`__init__.py` 与 `EntryLifecycleController` 决策密度下降，但不恢复 eager binding、第二 orchestration root 或 compat folklore。
  3. dependency/public-surface guards 继续覆盖 lazy wiring 与 boundary truth，不允许 formal root 热点反弹。
**Status**: Complete (`2026-03-21`)
**Plans**: 4/4 complete
**Promoted closeout package**: `48-SUMMARY.md`, `48-VERIFICATION.md`

Plans:
- [x] 48-01: topicize runtime access projections and system-health helpers (completed 2026-03-21)
- [x] 48-02: continue coordinator inward decomposition without changing public surface (completed 2026-03-21)
- [x] 48-03: slim init and entry-lifecycle wiring while preserving lazy composition (completed 2026-03-21)
- [x] 48-04: harden dependency and public-surface guards around the formal roots (completed 2026-03-21)

### Phase 49: Mega-test topicization and failure-localization hardening

**Goal:** 拆分治理 megaguards、runtime-root megatests 与 platform megatests，让失败直接命中具体 concern / facet / phase token，而不是让维护者继续在巨石测试里手工剥洋葱。
**Depends on:** Phase 48
**Requirements**: [TST-09, QLT-17]
**Success Criteria**:
  1. `tests/meta/test_governance_closeout_guards.py`、`tests/core/test_coordinator.py`、`tests/core/test_diagnostics.py` 与 `tests/platforms/test_update.py` 完成 concern/topic 切分。
  2. stray top-level tests 进入更自然的 domain home；assertion ids / parameterization 会报出实际 `(phase, doc, token)` 或 runtime facet。
  3. failure-localization 提升不以牺牲 coverage / guard honesty 为代价。
**Status**: Complete (`2026-03-21`)
**Plans**: 4/4 complete
**Promoted closeout package**: `49-SUMMARY.md`, `49-VERIFICATION.md`

Plans:
- [x] 49-01: split governance megaguards by concern and evidence family (completed 2026-03-21)
- [x] 49-02: topicize coordinator and diagnostics test surfaces (completed 2026-03-21)
- [x] 49-03: decompose update-platform megatests and re-home stray top-level tests (completed 2026-03-21)
- [x] 49-04: tighten assertion ids and failure summaries for faster localization (completed 2026-03-21)

### Phase 50: REST typed-surface reduction and command/result ownership convergence

**Goal:** 收紧 REST child façade family 的 `Any` / helper honesty，并把 command-result policy 与 diagnostics auth-error duplication 收敛到单一 formal home，在不扩张 public surface 的前提下继续压缩 conceptual ownership drift。
**Depends on:** Phase 49
**Requirements**: [TYP-12, ARC-07]
**Success Criteria**:
  1. `endpoint_surface.py`、`rest_facade.py`、`request_gateway.py` 与 related helpers 的 sanctioned-vs-backlog `Any` 分类更窄、更诚实。
  2. duplicated command/result policy logic 收敛到共享 formal home；diagnostics/helper auth-error duplication 向 `services/execution.py` 方向回收。
  3. REST public surface 与 command/query contract 保持稳定，typed budget guards 可验证 no-growth / net-reduction。
**Status**: Complete (`2026-03-21`)
**Plans**: 4/4 complete
**Promoted closeout package**: `50-SUMMARY.md`, `50-VERIFICATION.md`

Plans:
- [x] 50-01: reduce REST request and endpoint helper Any surfaces (completed 2026-03-21)
- [x] 50-02: narrow sanctioned-versus-backlog Any classifications (completed 2026-03-21)
- [x] 50-03: converge command-result policy ownership into one formal home (completed 2026-03-21)
- [x] 50-04: close diagnostics auth-error duplication and harden typed-budget guards (completed 2026-03-21)

## v1.8: Operational Continuity Automation, Formal-Root Sustainment & Hotspot Round 2

> `v1.8` 以 `v1.6` archived shipped truth 与 `v1.7` promoted audit/closeout evidence 为基线；目标不是重开审阅，而是把 continuity automation、formal-root second-round slimming、helper-hotspot formalization 与 mega-test/typing sustainment 变成更低摩擦、可执行、可验证的新里程碑。

**Milestone status:** `Phase 51 -> 55 complete (2026-03-21)`
**Default next command:** `$gsd-progress`（`Phase 55` 已完成；里程碑已具备 archive / next-milestone arbitration 条件）
**Seed input:** `.planning/reviews/V1_8_MILESTONE_SEED.md`

### Phase 51: Continuity automation, governance-registry projection, and release rehearsal hardening

**Goal:** 把 maintainer continuity / delegate / custody / freeze / restoration 真相升级为可演练合同，并继续降低 governance-registry 到 docs/templates/workflow 的手工同步成本，同时补齐 verify-only / non-publish release rehearsal 与按变更类型切分的最小充分验证矩阵。
**Depends on:** Phase 50
**Requirements**: [GOV-38, GOV-39, QLT-18]
**Success Criteria**:
  1. `SUPPORT.md`、`SECURITY.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`.github/CODEOWNERS`、issue/PR templates 与 governance registry 形成单一、可演练、无 hidden delegate 的 continuity contract。
  2. governance-registry truth 能稳定投影到 contributor / maintainer-facing metadata surfaces，减少 docs/templates/manual sync drift。
  3. release chain 支持 verify-only / non-publish rehearsal，且 contributor docs 能按 docs-only / governance-only / release-only 等 change type 提供最小充分验证 guidance。
**Status**: Complete (`2026-03-21`)
**Plans**: 3/3 complete
**Promoted closeout package**: `51-SUMMARY.md`, `51-VERIFICATION.md`

Plans:
- [x] 51-01: formalize the maintainer-unavailable drill across support, security, runbook, CODEOWNERS, and contributor handoff surfaces (completed 2026-03-21)
- [x] 51-02: project governance-registry maintenance metadata into lower-drift docs, templates, and contributor guidance (completed 2026-03-21)
- [x] 51-03: add verify-only release rehearsal and change-type validation guidance without weakening publish guards (completed 2026-03-21)

### Phase 52: Protocol-root second-round slimming and request-policy isolation

**Goal:** 继续 inward decomposition `LiproProtocolFacade` 与 request-policy collaborator family，在不改变唯一 protocol-plane root 真相的前提下降低 decision density。
**Depends on:** Phase 51
**Requirements**: [ARC-08]
**Success Criteria**:
  1. `LiproProtocolFacade` 的 login/status/command/OTA/schedule/MQTT-attach concern 进一步 inward topicize，而不是被新 façade 或 wrapper 替代。
  2. request pacing / retry / 429 / busy semantics 拥有更窄、更清晰的 collaborator seams。
  3. protocol child/root public truth、boundary direction 与 contract suites 维持不漂移。
**Status**: Complete (`2026-03-21`)
**Plans**: 3/3 complete
**Promoted closeout package**: `52-SUMMARY.md`, `52-VERIFICATION.md`

Plans:
- [x] 52-01: narrow protocol root body with support-only REST method seams, concern-local REST ports, and MQTT child-façade localization (completed 2026-03-21)
- [x] 52-02: isolate `429` / busy / pacing truth inside `RequestPolicy` and narrow gateway/executor ownership (completed 2026-03-21)
- [x] 52-03: freeze ownership via focused regressions, governance baselines, and explicit residual honesty (completed 2026-03-21)

### Phase 53: Runtime and entry-root second-round throttling

**Goal:** 沿现有 seams 继续给 `Coordinator`、`__init__.py` 与 `EntryLifecycleController` 限流，降低 orchestration density，同时保持 lazy wiring 与单一正式主链。
**Depends on:** Phase 52
**Requirements**: [HOT-12]
**Success Criteria**:
  1. runtime/entry 决策继续 inward decomposition，而不是回流 adapter folklore。
  2. activation / reload / unload / bootstrap concern 更清晰地各回 formal home。
  3. public behavior、dependency direction 与 wiring laziness 保持稳定。
**Status**: Complete (`2026-03-21`)
**Plans**: 3/3 complete
**Promoted closeout package**: `53-SUMMARY.md`, `53-VERIFICATION.md`

Plans:
- [x] 53-01: narrow coordinator bootstrapping ballast without changing the single-runtime-root story (completed 2026-03-21)
- [x] 53-02: split entry lifecycle mechanics into controller-private support operations (completed 2026-03-21)
- [x] 53-03: compress HA root adapter wiring and freeze lazy-composition truth (completed 2026-03-21)

### Phase 54: Helper-hotspot formalization for anonymous-share and diagnostics helper families

**Goal:** 把 `AnonymousShareManager`、diagnostics API helper family 与 request-policy companions 继续切薄，降低 helper-owned truth 与 privacy-sensitive decision density。
**Depends on:** Phase 53
**Requirements**: [HOT-13]
**Success Criteria**:
  1. `anonymous_share` manager/client/report builder concern 分层更清晰，不新增第二 public story。
  2. diagnostics API helper flows decision density 下降，service/privacy contract 仍稳定。
  3. request-policy companion seams 不回流新的 helper-owned truth。
**Status**: Complete (`2026-03-21`)
**Plans**: 4/4 complete
**Promoted closeout package**: `54-SUMMARY.md`, `54-VERIFICATION.md`

Plans:
- [x] 54-01: slim anonymous-share manager along scope-state and report-submission seams (completed 2026-03-21)
- [x] 54-02: split share-client token and transport outcome mechanics without changing worker contract (completed 2026-03-21)
- [x] 54-03: topicize diagnostics helper family without changing the control-plane public home (completed 2026-03-21)
- [x] 54-04: close request-policy companion residuals and freeze helper-hotspot truth (completed 2026-03-21)

### Phase 55: Mega-test topicization round 2 and repo-wide typing-metric stratification

**Goal:** 继续 topicize API/MQTT/platform mega-tests，并把 repo-wide typing truth 从 touched-zone 守卫提升到 production-vs-test-literal 分层指标。
**Depends on:** Phase 54
**Requirements**: [TST-10, TYP-13]
**Success Criteria**:
  1. `test_api_command_surface`、`test_transport_runtime` 与 platform entity megas 继续按 concern 拆解。
  2. repo-wide typing metrics 能区分 production debt 与 test/guard literal debt。
  3. no-growth guard posture 扩展到更诚实、更可解释的范围，而不是重回 giant meta-guard。
**Status**: Complete (`2026-03-21`)
**Plans**: 5/5 complete
**Promoted closeout package**: `55-SUMMARY.md`, `55-VERIFICATION.md`

Plans:
- [x] 55-01: topicize API command-surface mega tests by payload, auth, retry, and branch family (completed 2026-03-21)
- [x] 55-02: topicize MQTT transport mega tests by lifecycle, ingress, sync, and loop concerns (completed 2026-03-21)
- [x] 55-03: split light and fan platform megas into model, command, and behavior topics (completed 2026-03-21)
- [x] 55-04: split select and switch platform megas into entity-behavior topic families (completed 2026-03-21)
- [x] 55-05: stratify repo-wide typing metrics by production, tests, and meta-literal buckets (completed 2026-03-21)


## v1.9: Shared Backoff Neutralization & Cross-Plane Retry Hygiene

> `v1.9` 不重开大规模审阅或新架构路线，而是把 `Phase 52/54` 已显式登记的最后一条 active residual family 收口为诚实的 shared-primitive truth：generic exponential backoff 迁出 `RequestPolicy`，回到 neutral helper home。

**Milestone status:** `Phase 56 complete (2026-03-22)`
**Default next command:** `$gsd-complete-milestone v1.9`（opening phase 已完成；当前里程碑已具备 closeout 条件）
**Seed input:** `.planning/reviews/V1_9_MILESTONE_SEED.md`

### Phase 56: Shared backoff neutralization and cross-plane retry hygiene

**Goal:** 把 generic exponential backoff primitive 从 `request_policy.py` 迁到 neutral shared helper home，切断 command/runtime/MQTT 对 API policy home 的跨平面 import，同时保持 `RequestPolicy` 的 API-local `429` / busy / pacing truth 不漂移。
**Depends on:** Phase 55
**Requirements**: [RES-13, ARC-09, GOV-40]
**Success Criteria**:
  1. `custom_components/lipro/core/utils/backoff.py` 成为 neutral shared exponential-backoff primitive home；`request_policy.py` 不再导出 generic helper。
  2. `result_policy.py`、runtime `RetryStrategy` 与 `MqttSetupBackoff` 全部改从 neutral helper import primitive，但 plane-local retry semantics、caps、jitter 与 budgets 保持不变。
  3. `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`、baseline/review docs、promoted assets 与 focused meta guards 全部承认 residual 已在 `Phase 56` 关闭。
**Status**: Complete (`2026-03-22`)
**Plans**: 3/3 complete
**Promoted closeout package**: `56-SUMMARY.md`, `56-VERIFICATION.md`

Plans:
- [x] 56-01: create a neutral shared backoff helper home without changing API policy truth (completed 2026-03-22)
- [x] 56-02: rewire command runtime and MQTT callers to the neutral helper without changing plane semantics (completed 2026-03-22)
- [x] 56-03: freeze residual closure in baselines review ledgers and current milestone truth (completed 2026-03-22)

## v1.10: Command-Result Typed Outcome & Reason-Code Hardening

> `v1.10` 不重开 retry ownership 或 broad audit，而是把 `Phase 56` 明确递延的 command-result typed outcome / reason-code endgame 收口为 command-family typed contract：`result_policy.py` / `result.py` / runtime sender / diagnostics query consumers 共享同一 vocabulary，不再散落 raw strings。

**Milestone status:** `Phase 57 complete (2026-03-22)`
**Default next command:** `$gsd-complete-milestone v1.10`（opening phase 已完成；当前里程碑已具备 closeout 条件）
**Seed input:** `.planning/reviews/V1_10_MILESTONE_SEED.md`

### Phase 57: Command-result typed outcome and reason-code hardening

**Goal:** 把 command-result family 的 state / verification / failure-reason raw strings 收口为 shared typed contract，让 `result_policy.py` / `result.py` / runtime sender / diagnostics query consumers 复用同一 vocabulary，同时保持 outward behavior 与 ownership truth 稳定。
**Depends on:** Phase 56
**Requirements**: [ERR-12, TYP-14, GOV-41]
**Success Criteria**:
  1. `custom_components/lipro/core/command/result_policy.py` 与 `custom_components/lipro/core/command/result.py` 共享 typed command-result state / verification / failure-reason contract，classification/polling 与 failure arbitration ownership 不漂移。
  2. runtime sender 与 diagnostics `query_command_result` response typing 全部改为消费 shared contract，而 public payload shape 与 timeout semantics 保持稳定。
  3. `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`、baseline/review docs、promoted assets 与 focused meta guards 全部承认 command-result typed contract 已在 `Phase 57` formalized closeout。
**Status**: Complete (`2026-03-22`)
**Plans**: 3/3 complete
**Promoted closeout package**: `57-SUMMARY.md`, `57-VERIFICATION.md`

Plans:
- [x] 57-01: define one shared typed command-result vocabulary inside the formal command family (completed 2026-03-22)
- [x] 57-02: align runtime sender and diagnostics response typing to the shared command-result contract (completed 2026-03-22)
- [x] 57-03: freeze typed command-result truth in governance notes guards and promoted evidence (completed 2026-03-22)

## v1.11: Repository Audit Refresh & Next-Wave Remediation Routing

> `v1.11` 不把新的全仓终极审阅硬塞回 `v1.10` 的 command-result scope，而是以 `Phase 46` 审计资产、`v1.8 -> v1.10` closeout evidence 与当前用户指令为输入，重新刷新整仓 verdict，并把后续整改路由成 `Phase 59+` 的正式真相。

**Milestone status:** `Phase 58 complete (2026-03-22)`
**Default next command:** `$gsd-complete-milestone v1.11`（single-phase refreshed audit milestone 已具备 closeout 条件）
**Seed input:** `.planning/reviews/V1_11_MILESTONE_SEED.md`

### Phase 58: Repository audit refresh and next-wave routing

**Goal:** 以当前仓库真相为准，重新审阅所有 Python / docs / config / governance surfaces，对架构、代码质量、命名、目录结构、旧新代码边界、开源成熟度与验证可维护性给出刷新后的 file-level verdict，并把结论正式路由成 `Phase 59+`。
**Depends on:** Phase 57
**Requirements**: [AUD-03, ARC-10, OSS-06, GOV-42]
**Success Criteria**:
  1. refreshed audit package 覆盖 `custom_components` / `tests` / `scripts` / docs / root config / governance truth，明确 strengths、risks、hotspots、naming/directory verdicts 与 blind-spot disposition。
  2. refreshed open-source/governance audit 对 README / docs / support / security / contributing / packaging / tooling truth 给出当前 verdict，并说明与国际优秀开源实践相比的优点与不足。
  3. `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md` 与 promoted phase evidence 明确承认 `v1.11 / Phase 58` 作为新的 audit-routing truth，并给出 `Phase 59+` remediation route。
**Status**: Complete (`2026-03-22`)
**Plans**: 3/3 complete
**Promoted closeout package**: `58-SUMMARY.md`, `58-VERIFICATION.md`

Plans:
- [x] 58-01: refresh the architecture and code audit with file-level current-state evidence (completed 2026-03-22)
- [x] 58-02: refresh governance and open-source audit, then synthesize the next-wave remediation route (completed 2026-03-22)
- [x] 58-03: freeze `v1.11 / Phase 58` in current-story docs, guards, and promoted evidence (completed 2026-03-22)

## v1.13: Tooling Truth Decomposition, Formal-Home Slimming & Naming/Discoverability Convergence

> `v1.13` 已于 `2026-03-22` 完成 milestone audit 与 archive promotion：它承接 `v1.12` 的 localized verification baseline，先完成 tooling truth / file-governance hotspot inward decomposition，再收薄 large-but-correct production homes，最后把 support-seam naming 与 public discoverability 噪音冻结为 archived evidence。

**Archive status:** `archived / evidence-ready (2026-03-22)`
**Archive assets:** `.planning/v1.13-MILESTONE-AUDIT.md`, `.planning/reviews/V1_13_EVIDENCE_INDEX.md`, `.planning/milestones/v1.13-ROADMAP.md`, `.planning/milestones/v1.13-REQUIREMENTS.md`, `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-SUMMARY.md`, `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-VERIFICATION.md`, `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-SUMMARY.md`, `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-VERIFICATION.md`, `.planning/phases/62-naming-clarity-support-seam-governance-and-public-discoverability/62-SUMMARY.md`, `.planning/phases/62-naming-clarity-support-seam-governance-and-public-discoverability/62-VERIFICATION.md`
**Default next command:** `$gsd-new-milestone`

### Phase 60: Tooling truth decomposition and file-governance maintainability

**Goal:** 把 `scripts/check_file_matrix.py` 与 `tests/meta/test_toolchain_truth.py` 按 truth family inward decomposition 成更窄的 internal homes / focused suites，同时保持 CLI、import contract、authority chain 与 daily runnable roots 稳定。
**Depends on:** Phase 59
**Requirements**: [HOT-14, TST-12, GOV-44]
**Success Criteria**:
  1. `scripts/check_file_matrix.py` 退成 thin CLI root；inventory / classifier / validators / render / overrides 等 internal truth families 有了更清晰的 home，且既有 public import contract 不漂移。
  2. `tests/meta/test_toolchain_truth.py` 已 topicize 成更小的 focused suites 或 thin runnable roots；toolchain / release / docs / governance 断言不再混成单个 giant bucket。
  3. `.planning/reviews/FILE_MATRIX.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/codebase/TESTING.md` 与 current-story docs 全部准确记录新的 tooling truth topology 与 no-growth story。
**Status**: Complete (2026-03-22)
**Plans**: 3 completed

Plans:
- [x] 60-01: decompose the file-matrix checker into thin root and internal truth families (completed 2026-03-22)
- [x] 60-02: topicize toolchain truth guards by stable concern family (completed 2026-03-22)
- [x] 60-03: freeze tooling topology in governance truth and focused guards (completed 2026-03-22)
**Closeout evidence:** `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-SUMMARY.md`, `.planning/phases/60-tooling-truth-decomposition-and-file-governance-maintainability/60-VERIFICATION.md`

### Phase 61: Formal-home slimming for large-but-correct production modules

**Goal:** 沿现有 formal seams 继续切薄 `anonymous_share`、diagnostics API、OTA candidate 与 `select` 等 architecturally-correct 但仍偏厚的 production homes，提升 collaborator clarity、typed seams 与 focused verification。
**Depends on:** Phase 60
**Requirements**: [HOT-15, QLT-20, TYP-15]
**Success Criteria**:
  1. `anonymous_share`、diagnostics API、OTA / select touched homes 只做 inward split，不新增 public root、compat shell 或 helper-owned second story。
  2. 新形成的 collaborator / projection seams 继续保持 typed contract、honest ownership 与 plane boundary clarity，而不是以动态 fallback 掩盖复杂度。
  3. family-level focused regressions 与 maintainability evidence 能独立运行，证明 refactor 带来真实 failure-localization / readability 收益。
**Status**: Complete (2026-03-22)
**Plans**: 4/4 complete

Plans:
- [x] 61-01: slim anonymous-share formal homes into orchestration-only roots and focused submit collaborators (completed 2026-03-22)
- [x] 61-02: slim diagnostics service helpers and handlers behind the stable diagnostics public surface (completed 2026-03-22)
- [x] 61-03: slim OTA candidate certification and install-policy helpers while preserving candidate.py as the outward home (completed 2026-03-22)
- [x] 61-04: slim select platform internals and add focused maintainability evidence without changing select.py as the HA root (completed 2026-03-22)
**Closeout evidence:** `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-SUMMARY.md`, `.planning/phases/61-formal-home-slimming-for-large-but-correct-production-modules/61-VERIFICATION.md`

### Phase 62: Naming clarity, support-seam governance, and public discoverability

**Goal:** 继续收口 `*_support.py` / `*_surface.py` 命名语义、retired tooling discoverability 与 contributor/public fast path，让 support-only seams、public docs 与 governance guards 对“谁是 formal home”给出更低噪声答案。
**Depends on:** Phase 61
**Requirements**: [RES-14, DOC-07, GOV-45]
**Success Criteria**:
  1. `support` / `surface` 术语只留给真实角色；stale helper/public wording 不再让 internal backing seam 看起来像第二 formal root。
  2. README、docs index、contributor fast path、retired tooling discoverability 与 bilingual public entry 继续讲一条低噪声 story。
  3. current-story docs、review ledgers 与 grep/meta guards 都能阻止 stale terminology、duplicate discoverability route 与第二 helper/public story 回流。
**Status**: Complete (2026-03-22)
**Plans**: 4/4 complete

Plans:
- [x] 62-01: freeze keep-vs-rename decisions and land only the low-fanout DeviceExtras support rename (completed 2026-03-22)
- [x] 62-02: converge bilingual README and public docs fast path without reintroducing maintainer-only first hops (completed 2026-03-22)
- [x] 62-03: freeze post-Phase-61 naming and discoverability truth in baselines, ledgers, and verification governance (completed 2026-03-22)
- [x] 62-04: add anti-regression guards and close out current-story docs for naming and discoverability convergence (completed 2026-03-22)
**Closeout evidence:** `.planning/phases/62-naming-clarity-support-seam-governance-and-public-discoverability/62-SUMMARY.md`, `.planning/phases/62-naming-clarity-support-seam-governance-and-public-discoverability/62-VERIFICATION.md`

## v1.12: Verification Localization & Governance Guard Topicization

> `v1.12` 现已完成 milestone audit 与 archive promotion：它的职责是先把 `Phase 58` 路由出的 megaguards / megasuites 收窄到更诚实的 verification topology，再把 localized route 冻结成 archived closeout evidence，作为 `v1.13` 的低噪声起点。

**Archive status:** `archived / evidence-ready (2026-03-22)`
**Archive assets:** `.planning/v1.12-MILESTONE-AUDIT.md`, `.planning/reviews/V1_12_EVIDENCE_INDEX.md`, `.planning/milestones/v1.12-ROADMAP.md`, `.planning/milestones/v1.12-REQUIREMENTS.md`, `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-SUMMARY.md`, `.planning/phases/59-verification-localization-and-governance-guard-topicization/59-VERIFICATION.md`

### Phase 59: Verification localization and governance guard topicization

**Goal:** 把 public-surface / governance-history / follow-up-route megaguards 与 `test_device_refresh.py` topicize 成按 truth-family / concern boundary 划分的更窄套件，同时把新的 runnable topology 冻结回 verification / governance docs。
**Depends on:** Phase 58
**Requirements**: [TST-11, QLT-19, GOV-43]
**Success Criteria**:
  1. `tests/meta/test_public_surface_guards.py`、`tests/meta/test_governance_phase_history.py`、`tests/meta/test_governance_followup_route.py` 已收敛为 thin shell roots，`tests/core/test_device_refresh_{parsing,filter,snapshot,runtime}.py` 已形成 focused suites，failure radius 明显缩小。
  2. topicization 只沿现有 truth seams inward 推进，不新增新的 helper root、duplicate truth file 或 second governance story。
  3. `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE}.md`、verification matrix、`TESTING.md` 与 review truth 全部准确记录 localized verification topology、ownership boundary 与 no-growth story。
**Status**: Complete (`2026-03-22`)
**Plans**: 3/3 complete
**Promoted closeout package**: `59-SUMMARY.md`, `59-VERIFICATION.md`

Plans:
- [x] 59-01: topicize governance and public-surface megaguards by stable truth family (completed 2026-03-22)
- [x] 59-02: split `test_device_refresh.py` by parsing, filter semantics, snapshot building, and runtime behavior concerns (completed 2026-03-22)
- [x] 59-03: freeze localized verification topology in matrices, current-story docs, and focused guards (completed 2026-03-22)

### 🚧 v1.14 Governance Truth Realignment, Typed Runtime Access & Final Hidden-Root Closure

**Milestone Goal:** 以 `v1.13` archived evidence 为起点，先统一 governance latest-pointer / archive-route truth 与 anti-drift guards，再把 `RuntimeAccess` / `__init__.py` / tooling-test hidden-root / command-share typed seams，以及 telemetry / schedule / diagnostics 剩余 formal-contract hotspots 收口到更诚实、更薄、更可验证的正式主链。

**Current Status:** `Phase 63 -> 66 complete (2026-03-23)`；governance pointer / release-target fidelity、typed runtime access、tooling/test hidden-root closure、telemetry / schedule / diagnostics follow-through、runtime-access 去反射化、adapter-root cleanup、runtime alias 显式投影、anonymous-share outcome-native submit contract 与 focused protocol seam hardening 已完成，`v1.14` 当前回到 milestone closeout-ready 状态。

### Phase 63: Governance truth realignment, typed runtime access, and hidden-root closure

**Goal:** 修复 milestone/latest-pointer truth drift，继续把 `RuntimeAccess` 与 `__init__.py` 压回 typed / thin formal homes，并关闭 file-matrix、API/meta topic suites、command/share flows 中仍然存在的 hidden-root、stringly 与 `Any` 漏口。
**Depends on:** Phase 62
**Requirements**: [GOV-46, GOV-47, HOT-16, HOT-17, TST-13, TYP-16, QLT-21]
**Success Criteria**:
  1. `PROJECT / STATE / ROADMAP / REQUIREMENTS / MILESTONES / docs index / runbook / tests` 共同承认 `v1.13` latest archive-ready pointer 与 `v1.14` active route，CI guards 能阻止 stale pointer / stale route 回流。
  2. `RuntimeAccess` / `__init__.py` 继续走 typed read-model + thin adapter 收口；control/runtime truth 不再依赖 broad introspection helper 或根层动态聚合。
  3. `file-matrix` / API-meta topic suites / command-share follow-through 的 hidden-root、stringly 与 `Any` 漏口得到 inward closure，并以 focused tests + governance truth 同轮验证。
**Plans**: 5 total / 5 completed / 0 pending

Plans:
- [x] 63-01: align governance latest-pointer truth, latest closeout docs, and anti-drift guards (completed 2026-03-23)
- [x] 63-02: converge RuntimeAccess onto typed read-model ports and thin the HA root adapter (completed 2026-03-23)
- [x] 63-03: decompose file-matrix/tooling truth and unify local-vs-CI command contracts (completed 2026-03-23)
- [x] 63-04: close topic-suite hidden roots in API and governance/meta tests (completed 2026-03-23)
- [x] 63-05: tighten command failure summaries and anonymous-share transport typing (completed 2026-03-23)

### Phase 64: Telemetry typing, schedule contracts, and diagnostics hotspot slimming

**Goal:** 继续把 assurance/service/API 三个剩余热点收口到 typed / thin formal homes：让 telemetry exporter / ports / sinks 使用显式 JSON-safe contracts，让 schedule service 消除 `Any` + dynamic mesh-context 主逻辑，让 diagnostics API 退成 thin outward home 并把 OTA/history/query helpers inward split。
**Depends on:** Phase 63
**Requirements**: [ARC-11, HOT-18, HOT-19, TYP-17, TST-14, GOV-48, QLT-22]
**Success Criteria**:
  1. telemetry family（`models.py` / `ports.py` / `exporter.py` / `sinks.py`）以显式 JSON-safe typed contracts 讲同一条 story；`Any` 不再充当 formal exporter truth。
  2. `services/schedule.py` 的 mesh-context / normalized row / protocol-call contract 完成 formalization；service 主逻辑不再依赖 broad `Any` / `getattr`。
  3. `diagnostics_api_service.py` 退成 thin outward home，OTA / sensor-history / misc query helpers inward split；focused tests + `FILE_MATRIX` / current-story docs 同轮更新。
**Status**: Complete (2026-03-23)
**Plans**: 3/3 complete

Plans:
- [x] 64-01: converge telemetry exporter family onto explicit JSON-safe typed contracts (completed 2026-03-23)
- [x] 64-02: formalize schedule service contracts and remove dynamic mesh-context probing from the main path (completed 2026-03-23)
- [x] 64-03: split diagnostics API concerns inward while syncing current-story docs and file-matrix truth (completed 2026-03-23)
**Closeout evidence:** `.planning/phases/64-telemetry-typing-schedule-contracts-and-diagnostics-hotspot-slimming/64-SUMMARY.md`, `.planning/phases/64-telemetry-typing-schedule-contracts-and-diagnostics-hotspot-slimming/64-VERIFICATION.md`


### Phase 65: Runtime-access de-reflection and anonymous-share hotspot closure

**Goal:** 把 `control/runtime_access_support.py` 从测试驱动的反射/Mock-ghost 防御收口回显式 runtime read-model，并把 `DeviceExtras` 的 identity/mesh projections 与 `anonymous_share` 的 submit contract 继续 formalize：生产主路径不再为 `MagicMock` 或 bool-only test doubles 牺牲 contract honesty，raw `extra_data` 读取只保留在本地 mutator/compat 边界。
**Depends on:** Phase 64
**Requirements**: [ARC-12, HOT-20, HOT-21, TYP-18, TST-15, GOV-49, QLT-23]
**Success Criteria**:
  1. `custom_components/lipro/control/runtime_access_support.py` 不再依赖 mock-child / instance-dict introspection 充当正式 runtime truth；runtime-access focused tests 改用显式 fake entry/coordinator ports，public helper surface 保持稳定。
  2. `DeviceExtras` 对 identity aliases 与 mesh/IR gateway projections 提供正式读取面，control/runtime consumers 不再在生产路径直接读取 `device.extra_data` 决策主逻辑；raw side-car 仅保留在 localized mutator / legacy fallback 边界。
  3. `custom_components/lipro/core/anonymous_share/manager.py` / `manager_submission.py` / related tests 统一到 outcome-native submit contract，不再通过动态方法探测或 bool-only mock bridge 维持主路径；governance docs 与 file matrix 同轮冻结新 topology。
**Plans**: 3 total / 3 completed / 0 pending

Plans:
- [x] 65-01: de-reflect runtime access and replace ghost-prone mocks with explicit runtime fakes (completed 2026-03-23)
- [x] 65-02: formalize device extras projections and remove raw extra-data reads from production consumers (completed 2026-03-23)
- [x] 65-03: converge anonymous-share submission onto one typed outcome contract and freeze Phase 65 truth (completed 2026-03-23)
**Focused evidence:** `.planning/phases/65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure/65-01-SUMMARY.md`, `.planning/phases/65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure/65-02-SUMMARY.md`, `.planning/phases/65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure/65-03-SUMMARY.md`
**Closeout evidence:** `.planning/phases/65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure/65-SUMMARY.md`, `.planning/phases/65-runtime-access-de-reflection-and-anonymous-share-hotspot-closure/65-VERIFICATION.md`

### Phase 66: Release target fidelity, adapter-root cleanup, and focused protocol coverage hardening

**Goal:** 统一 tagged release / workflow_dispatch 校验对象与 active-governance freshness truth，并继续清理 HA 根适配器的 duplicated stub / dynamic import 残留，同时为 protocol transport / service / root hotspots 铺设 focused regression coverage，避免 mega matrix 继续独占这些 seam 的验证责任。
**Depends on:** Phase 65
**Requirements**: [GOV-50, OSS-07, ARC-13, HOT-22, TST-16, QLT-24]
**Success Criteria**:
  1. `.github/workflows/release.yml` 的 validate/release 路径对同一 tagged ref 讲同一条故事；`README*`、baseline、reviews 与 meta guards 不再保留 stale active-route / stale release-example drift。
  2. `custom_components/lipro/__init__.py`、`sensor.py` 与 `select.py` 继续压回 thin explicit adapter story；duplicated stub blocks、runtime-only dynamic import folklore 不再承担正式 contract。
  3. `transport_executor.py`、`protocol_service.py`、`protocol/facade.py` 与 `protocol/mqtt_facade.py` 获得 focused regression coverage；协议根链与 transport seam 不再主要依赖 mega matrix 守护。
**Status**: Complete (2026-03-23)
**Plans**: 4 total / 4 completed / 0 pending

Plans:
- [x] 66-01: align release-target validation with tagged refs and remove stale current-story install/governance drift (completed 2026-03-23)
- [x] 66-02: remove duplicated adapter-root stubs and replace platform dynamic-import folklore with explicit formal imports (completed 2026-03-23)
- [x] 66-03: add focused regression suites for transport executor, coordinator protocol service, and protocol root seams (completed 2026-03-23)
- [x] 66-04: freeze Phase 66 current-story, verification, and residual ledgers after execution (completed 2026-03-23)
**Focused evidence:** `.planning/phases/66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening/66-01-SUMMARY.md`, `.planning/phases/66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening/66-02-SUMMARY.md`, `.planning/phases/66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening/66-03-SUMMARY.md`, `.planning/phases/66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening/66-04-SUMMARY.md`
**Closeout evidence:** `.planning/phases/66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening/66-SUMMARY.md`, `.planning/phases/66-release-target-fidelity-adapter-root-cleanup-and-focused-protocol-coverage-hardening/66-VERIFICATION.md`
