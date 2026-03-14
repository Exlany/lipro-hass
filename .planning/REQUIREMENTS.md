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

- [ ] **ISO-01**: `login`、`device_list`、`query_device_status`、`query_mesh_group_status`、OTA/support-critical payload 等高漂移 REST/MQTT 输入必须在 protocol boundary 输出 canonical contract；runtime/domain/control/platform 不得再自行解析 vendor envelope、field alias 或分页形态。
- [ ] **ISO-02**: host-neutral auth / session / query-result contracts 必须显式化；`config_flow`、`entry_auth` 与其他 control adapters 只能消费 formal use case / result contract，不得依赖 raw response dict shape。
- [ ] **ISO-03**: `core` formal public surface 必须继续与 HA runtime root 解耦；`Coordinator` 保持通过 `coordinator_entry` 暴露，`core/__init__.py` 不得把 HA runtime 当作 host-neutral core truth 的一部分继续输出。
- [ ] **ISO-04**: 与 API drift isolation 相关的 roadmap/context/research/validation/verification/governance docs、replay fixtures 与 meta guards 必须同轮更新；未来 CLI / 其他宿主只能建立在 formal boundary 之上，而不是反向长成 second root。

## Cross-Phase Arbitration

- `07.3` 锁定 telemetry contracts / redaction / cardinality / timestamp-pseudo-id compatibility
- `07.4` 锁定 replay manifests / deterministic driver / replay assertions / run summary
- `07.5` 锁定 governance matrices / evidence index / residual / delete gates
- `08` 锁定 AI debug packaging / exporter entrypoint / pack schema
- `09` 锁定 residual surface closure / compat seam narrowing / read-only runtime access / formal outlet-power primitive
- `10` 锁定 API drift isolation / core-boundary prep / host-neutral contracts；不得把跨平台 SDK 抽离提升为本里程碑正式 root

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
| ISO-01 | Phase 10 | Planned |
| ISO-02 | Phase 10 | Planned |
| ISO-03 | Phase 10 | Planned |
| ISO-04 | Phase 10 | Planned |

**Coverage:**
- active milestone requirements: 21 total
- mapped to phases: 21
- unmapped: 0 ✓

*Last updated: 2026-03-14 after adding Phase 10 API drift isolation / core-boundary prep requirements*
