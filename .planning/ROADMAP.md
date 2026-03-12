# Roadmap: Lipro-HASS North Star Rebuild

## Overview

本路线图描述 `lipro-hass` 从“已存在但仍有历史结构残留的 HA 集成”收敛到“脱离历史成本约束的终态北极星架构”的完整路径。顺序原则是：**先建立协议真相基线，再资产化终态基准与护栏，再重建协议正式根，再统一控制/领域/运行/保障平面，最后完成全仓零残留治理**。

## Required Phase Outputs

每个 phase 完成时，除了代码与测试，还必须显式更新或确认以下输出：

- `.planning/reviews/FILE_MATRIX.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`
- `.planning/reviews/KILL_LIST.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`

## Phases

- [x] **Phase 1: 协议契约基线** - 固化关键协议入口真相，建立重构前的裁决基线
- [x] **Phase 1.5: 北极星基准资产化** - 把目标拓扑、依赖矩阵、public surfaces、验证矩阵正式落表并前置护栏
- [x] **Phase 2: REST Protocol Slice 重建** - 去除 mixin mega client 的正式地位，建立 `LiproRestFacade`
- [x] **Phase 2.5: 协议平面根统一** - 将 REST / MQTT 统一收口到 `LiproProtocolFacade`
- [x] **Phase 2.6: 外部边界收口** - formalize share / firmware / support payload / external endpoints
- [x] **Phase 3: Control Plane 收敛** - 把 lifecycle、flow、support surface、services 形成单一控制平面
- [ ] **Phase 4: Capability Model 统一** - 建立领域能力单一真源，清理平台/实体双轨规则
- [ ] **Phase 5: Runtime 主链加固** - 固化唯一正式运行时主链与 runtime invariants
- [ ] **Phase 6: Assurance Plane 正式化** - 将架构守卫、可观测性、CI 门禁升级为正式保障平面
- [ ] **Phase 7: 全仓治理与零残留收尾** - 彻底清理 compat、影子模块、旧文档与未归档残留

## Phase Details

### Phase 1: 协议契约基线
**Goal**: 对关键外部协议入口建立可重复、可审计、可阻断漂移的 contract baseline。
**Depends on**: Nothing
**Requirements**: [PROT-01, PROT-02, ASSR-01]
**Success Criteria**:
  1. 关键协议入口拥有可重复执行的 golden fixtures 与 contract matrix。
  2. 供应商返回结构或恢复链路一旦漂移，测试会直接失败并定位到入口。
  3. 协议不可变约束已有集中化台账，不再依赖口口相传。
**Plans**: 2 plans

Plans:
- [x] 01-01: 建立协议契约矩阵、golden fixtures 与 targeted tests
- [x] 01-02: 扩展 contract baseline 说明、不可变约束台账与 phase 收尾

### Phase 1.5: 北极星基准资产化
**Goal**: 在大规模重构前，把终态基准、依赖方向、正式 public surface 与验证闭环资产化，并建立最小可运行护栏。
**Depends on**: Phase 1
**Requirements**: [BASE-01, BASE-02, BASE-03, ARCH-04, ASSR-06]
**Success Criteria**:
  1. `TARGET_TOPOLOGY / DEPENDENCY_MATRIX / PUBLIC_SURFACES / VERIFICATION_MATRIX / AUTHORITY_MATRIX` 已形成正式基准资产包。
  2. 依赖方向与正式 public surface 已有最小可运行 guard，不再完全依赖人工审查。
  3. 后续各 phase 都可直接引用该资产包进行设计与验收。
**Plans**: 3 plans

Plans:
- [x] 01.5-01: 落地 north-star baseline assets 与 target topology
- [x] 01.5-02: 建立 dependency/public-surface seed guards
- [x] 01.5-03: 建立 verification matrix 与 phase 验收映射

### Phase 2: REST Protocol Slice 重建
**Goal**: 让 `REST / IoT` 协议主链只保留一条正式根，并以显式组合替代 mixin 聚合。
**Depends on**: Phase 1.5
**Requirements**: [ARCH-01, PROT-03, PROT-04, PROT-07]
**Success Criteria**:
  1. 维护者可以从 `LiproRestFacade` 读懂正式 REST 主链，而无需追继承链。
  2. `LiproClient` 不再承担正式架构根角色，只剩受控 compat shell 或已被删除。
  3. `AuthSession / RequestPolicy / normalizers / collaborators` 的边界清晰且可测试。
  4. Phase 1 的 contract tests 持续通过，证明重构未破坏正式外部行为。
**Plans**: 4 plans

Plans:
- [x] 02-01: 建立 REST protocol target design 与文件治理矩阵
- [x] 02-02: 重写 facade/transport/auth/policy 协作边界
- [x] 02-03: 迁移 endpoint collaborators 与 normalizers
- [x] 02-04: 收口 compat shell、旧 public names 与残留台账

### Phase 2.5: 协议平面根统一
**Goal**: 把 `REST / MQTT` 统一为同一个 protocol plane root，而不是两个分裂实现根。
**Depends on**: Phase 2
**Requirements**: [PROT-05, PROT-06]
**Success Criteria**:
  1. `LiproProtocolFacade` 成为唯一正式协议根。
  2. `LiproMqttFacade` 作为子门面并入统一协议平面，与 REST 共享明确 contracts。
  3. runtime plane 不再理解“REST 根 + MQTT 根”双模型。
  4. 归一化后的协议 contracts 成为 runtime/domain 的唯一输入形态。
**Plans**: 3 plans

Plans:
- [x] 02.5-01: 建立 unified protocol root 设计与 shared contracts
- [x] 02.5-02: 迁移 MQTT 生命周期与 telemetry/auth shared boundaries
- [x] 02.5-03: 清退旧协议双根 public surface 与 compat adapters

### Phase 2.6: 外部边界收口
**Goal**: 对 share、firmware、support payload 与其他外部边界建立 formal owner、contract、fixture 与 authority source。
**Depends on**: Phase 2.5
**Requirements**: [INTG-01, INTG-02]
**Success Criteria**:
  1. 外部边界均有 owner、contract、fixture、drift detection。
  2. `docs / fixtures / generated / implementation` 的权威来源与同步方向被正式记录。
  3. control plane 与 diagnostics/support surface 建立在已定型的外部边界之上，而非继续靠隐式约定。
**Plans**: 3 plans

Plans:
- [x] 02.6-01: 梳理 external boundary inventory 与 authority sources
- [x] 02.6-02: 为 share / firmware / support payload 建立 contracts 与 fixtures
- [x] 02.6-03: 收口边界说明文档与 drift-detection 验收

### Phase 3: Control Plane 收敛
**Goal**: 让入口、配置、诊断、健康度、服务注册形成单一控制平面叙事。
**Depends on**: Phase 2.6
**Requirements**: [CTRL-01, CTRL-02, CTRL-03, CTRL-04]
**Success Criteria**:
  1. `EntryLifecycleController / ServiceRegistry / DiagnosticsSurface / SystemHealthSurface` 形成明确正式边界。
  2. control plane 通过稳定 public surface 访问 runtime，而不是散落的 coordinator backdoor。
  3. 控制面变更具备 flow/diagnostics/service 级测试与 redaction 验证。
**Plans**: 3 plans

Plans:
- [x] 03-01: 梳理 entry lifecycle controller 与 control contracts
- [x] 03-02: 收敛 diagnostics / system health / services support surface
- [x] 03-03: 补齐 control-plane tests 与 redaction lifecycle guards

### Phase 4: Capability Model 统一
**Goal**: 建立领域能力单一真源，清理平台、实体、helpers 中重复生长的规则系统。
**Depends on**: Phase 2.6
**Requirements**: [DOM-01, DOM-02, DOM-03, DOM-04, DOM-05]
**Success Criteria**:
  1. `CapabilityRegistry / CapabilitySnapshot` 成为平台、实体、命令、属性的统一来源。
  2. 新能力新增点集中到 capability model，而不是扩散到多个平台分支。
  3. 旧的双轨规则与影子 helper 被删除或明确归档。
**Plans**: 3 plans

Plans:
- [x] 04-01: 设计 capability registry / snapshot / contracts
- [ ] 04-02: 迁移 entity/platform/helpers 到统一能力投影
- [ ] 04-03: 清退重复能力规则与旧访问面

### Phase 5: Runtime 主链加固
**Goal**: 让 runtime plane 在结构和验证上都符合“唯一正式编排根 + 显式协作”的北极星标准。
**Depends on**: Phase 3, Phase 4
**Requirements**: [ARCH-02, RUN-01, RUN-02, RUN-03, RUN-04]
**Success Criteria**:
  1. `Coordinator` 仍是唯一正式运行时编排根。
  2. 命令、刷新、状态应用、MQTT 生命周期都只有一条正式主链。
  3. runtime invariants 自动化测试能阻止旁路刷新、旁路写状态、异常吞没、重复订阅等回归。
  4. runtime public surface 足够薄、稳定、可推断。
**Plans**: 3 plans

Plans:
- [ ] 05-01: 收紧 runtime public surface 与 orchestration boundaries
- [ ] 05-02: 建立 command/refresh/state/mqtt invariant suite
- [ ] 05-03: 接入 runtime telemetry hooks 与关键路径观测点

### Phase 6: Assurance Plane 正式化
**Goal**: 把北极星约束落到自动守卫、观测与 CI 质量门上，防止未来继续回退。
**Depends on**: Phase 5
**Requirements**: [ASSR-02, ASSR-03, ASSR-04, ASSR-05]
**Success Criteria**:
  1. 关键运行信号具备可观测性与明确测试覆盖。
  2. architecture/meta guards 能阻止跨层直连、compat 回流、双主链复发。
  3. 测试结构已与新架构对齐，不再继续围绕旧 public names 打补丁。
  4. CI 质量门能够证明结构未退化，而非仅证明功能能跑。
**Plans**: 4 plans

Plans:
- [ ] 06-01: 定义 assurance taxonomy、观测点与指标口径
- [ ] 06-02: 强化 architecture enforcement 与 meta guards
- [ ] 06-03: 扩展 snapshot/integration/contract coverage 到新正式结构
- [ ] 06-04: 收口 CI gates、coverage 与 phase 验收模板

### Phase 7: 全仓治理与零残留收尾
**Goal**: 以全仓视角完成文件治理、残留清理、文档归一与最终复核闭环。
**Depends on**: Phase 6
**Requirements**: [ARCH-03, GOV-01, GOV-02, GOV-03, GOV-04, GOV-05]
**Success Criteria**:
  1. 全部 `406` 个 Python 文件都已被归类并完成对应去向。
  2. compat adapter、影子模块、旧命名、无效 docs 已删除或被正式归档，不再混入主叙事。
  3. `FILE_MATRIX` 已成为 file-level 权威视图，含 owner phase、残留链接与完成度。
  4. 北极星文档、开发文档、`.planning/`、测试矩阵与代码状态保持单一口径。
  5. 仓库能够交付一份完整的终态审查/收尾报告。
**Plans**: 4 plans

Plans:
- [ ] 07-01: 完成全仓文件治理矩阵与残留台账终版
- [ ] 07-02: 删除 compat/legacy/shadow modules 与无效文档
- [ ] 07-03: 对齐 north-star docs / developer docs / planning docs / test matrix
- [ ] 07-04: 生成最终复核报告与后续演进建议

## Cross-Cutting Tracks

### Track X0: 终态基准资产化
- 覆盖范围：目标拓扑、依赖方向、public surfaces、验证矩阵、authority source
- 目标：让 `.planning` 从“路线图”升级为“可执行基准”
- 收口阶段：Phase 1.5

### Track X1: 全仓文件治理矩阵
- 覆盖范围：全部 `406` 个 Python 文件
- 目标：每个 phase 执行时同步回写 `保留 / 重构 / 迁移适配 / 删除`
- 收口阶段：Phase 7

### Track X2: 残留与兼容收口
- 覆盖范围：compat adapters、旧 public names、影子模块、历史命名
- 目标：每个 phase 都显式声明“新增了什么残留、删除了什么残留、剩余什么残留”
- 收口阶段：Phase 7

### Track X3: 文档与架构口径同步
- 覆盖范围：`docs/`、`.planning/`、测试矩阵、ADR
- 目标：避免“代码一套、文档一套、计划一套”再次出现
- 收口阶段：全阶段持续执行，Phase 7 总结清零

## Progress

| Phase / Track | Plans Complete | Status | Completed |
|---------------|----------------|--------|-----------|
| Track X0 终态基准资产化 | 0 | Planned | - |
| Track X1 文件治理矩阵 | 0 | In progress | - |
| Track X2 残留与兼容收口 | 0 | In progress | - |
| Track X3 文档与架构口径同步 | 0 | In progress | - |
| 1. 协议契约基线 | 2/2 | Complete | 2026-03-12 |
| 1.5 北极星基准资产化 | 3/3 | Complete | 2026-03-12 |
| 2. REST Protocol Slice 重建 | 4/4 | Complete | 2026-03-12 |
| 2.5 协议平面根统一 | 3/3 | Complete | 2026-03-12 |
| 2.6 外部边界收口 | 3/3 | Complete | 2026-03-12 |
| 3. Control Plane 收敛 | 3/3 | Complete | 2026-03-12 |
| 4. Capability Model 统一 | 1/3 | In progress | 2026-03-12 (`04-01`) |
| 5. Runtime 主链加固 | 0/3 | Planned | - |
| 6. Assurance Plane 正式化 | 0/4 | Planned | - |
| 7. 全仓治理与零残留收尾 | 0/4 | Planned | - |

---
*Roadmap rebuilt: 2026-03-12 after gsd-new-project arbitration pass*
