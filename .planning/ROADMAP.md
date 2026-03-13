# Roadmap: Lipro-HASS North Star Evolution

## Milestones

- ✅ **v1.0 North Star Rebuild** - Phases 1-7 (+ 1.5 / 2.5 / 2.6), shipped 2026-03-13
- 🚧 **v1.1 Protocol Fidelity & Operability** - Phases 7.1-7.5, initialized 2026-03-13

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

**Milestone Goal:** 在不破坏既有北极星单一主链的前提下，正式引入 boundary decoder family、architecture policy enforcement、runtime telemetry exporter 与 replay evidence。

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
- [ ] 07.5-01: 回写 governance truth sources 与 file-level ownership
- [ ] 07.5-02: 生成 v1.1 verification/closeout package 与 next-step recommendations

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
- [ ] 08-01: 定义 evidence pack schema、pseudo-id 与 redaction 策略
- [ ] 08-02: 实现 evidence pack exporter + tests + governance handoff

## Cross-Phase Arbitration (7.3-8)

- `07.3` 只拥有 telemetry truth：exporter contracts、redaction、cardinality、timestamp / pseudo-id compatibility
- `07.4` 只拥有 replay truth：manifests、deterministic driver、replay assertions、run summary
- `07.5` 只拥有 governance closeout：matrices、evidence index、residual、delete gates
- `08` 只拥有 AI debug packaging：pull-only collector、pack schema、exporter entrypoint
- 执行顺序固定为 `7.3 -> 7.4 -> 7.5 -> 8`，避免真源反转与职责重叠

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-7 (+1.5/2.5/2.6) | v1.0 | 32/32 | Complete | 2026-03-13 |
| 7.1 Boundary Schema/Decoder | v1.1 | 3/3 | Complete | 2026-03-13 |
| 7.2 Enforcement | v1.1 | 2/2 | Complete | 2026-03-13 |
| 7.3 Telemetry Exporter | v1.1 | 2/2 | Complete | 2026-03-13 |
| 7.4 Replay Harness | v1.1 | 3/3 | Complete | 2026-03-13 |
| 7.5 Governance & Verification | v1.1 | 0/2 | Planned | - |
| 8 AI Debug Evidence Pack | v1.1 | 0/2 | Planned | - |
