# Lipro 重构完善计划

> **创建日期**: 2026-03-10  \
> **适用分支**: `cv/edf26778937a-`  \
> **目标**: 在既定“组合式 runtime + 薄 facade + 服务层委托”方向不回退的前提下，将本次重构收口为可长期维护、静态检查全绿、文档真实可信的高质量版本。

---

## 1. 背景与问题定义

当前分支已经完成大规模架构迁移，但仍处于“结构方向正确、工程收口不足”的状态，具体表现为：

- `ruff` 全绿（以 `uv run ruff check .` 输出为准）。
- `pytest` 应保持全绿（以 `uv run pytest -q` 输出为准）。
- `mypy` 仍存在错误（以 `uv run --extra dev mypy custom_components/lipro tests` 输出为准），集中在：API 兼容层缺失、runtime 协议错位、TypedDict 与真实 payload 不一致、协程签名错位、薄 facade 静态能力缺失、测试桩类型过严。
- 仓库存在生成型产物与失真文档，削弱代码评审与后续维护体验。

> 说明：本计划会在 **6. 最终验收结果** 回填每次 Phase 后的最新输出，避免文档长期漂移。

**本次完善的核心原则**：

1. 保持“组合优于继承”的重构方向，不回退到 mixin 拼装模式。
2. 优先修复根因，避免为过 lint / mypy 而引入临时型补丁。
3. 让运行时协议、对外 facade、测试桩三者共享同一份类型契约。
4. 文档只描述已验证事实，不保留夸大或失真的质量宣称。

---

## 2. 目标状态（完成标准）

### 2.1 必达目标

- [ ] `uv run ruff check .` 通过
- [ ] `uv run --extra dev mypy custom_components/lipro tests` 通过
- [ ] `uv run pytest -q` 通过
- [ ] 重构后的 runtime/service/device facade 保持既定拆分方向
- [ ] 仓库中不再追踪明显的本地产生型 benchmark 大文件
- [ ] 架构/状态文档与真实质量状态一致

### 2.2 质量目标

- [ ] 运行时接口命名、参数、返回值一致
- [ ] TypedDict / TypeAlias 与真实 payload 对齐
- [ ] facade 暴露的属性与使用方的静态预期一致
- [ ] 测试桩与生产接口一致，不依赖错误的宽松类型

---

## 3. 分阶段执行计划

### Phase A：静态卫生与基线清理

**目标**：先消除不影响设计的机械性噪音，为后续问题定位降噪。

- [x] A0. 记录基线输出（保存到执行记录）
- [x] A1. 执行 `uv run ruff check . --fix`（自动修复 `F401/I001/RUF100/RUF022`）
- [x] A2. 手工修复 `PLC0415/F821`（生产代码导入顶层化 + 未定义名称）
- [x] A3. 手工修复测试侧 `F811/RUF059/SIM117/RET504`（重复用例、未使用解包、嵌套 with、冗余 return）
- [x] A4. 重新运行 `uv run ruff check .`，确认 ruff 全绿

### Phase B：运行时协议与类型契约收口

**目标**：统一 `coordinator/types.py`、runtime helpers、command trace/result、status executor 的类型边界。

- [ ] B1. 修复 `CommandTrace` / `RuntimeMetrics` / 相关 TypedDict 定义不一致
- [ ] B2. 修复 command runtime 与 confirmation / sender / builder 的签名错位
- [ ] B3. 修复 status runtime、state runtime、tuning runtime、product config runtime 的返回类型
- [ ] B4. 修复 MQTT runtime / client runtime 的导入与返回值类型

### Phase C：薄 facade 与调用方一致性完善

**目标**：让 `LiproDevice`、`Coordinator` 与调用方 / 测试方拥有一致、清晰、可检查的公开能力。

- [ ] C1. 补齐 `LiproDevice` 对外属性声明，消除运行时有能力但静态不可见的问题
- [ ] C2. 修复 `Coordinator` 公开 API、构造依赖、回调签名不一致问题
- [ ] C3. 修复服务层与测试桩的参数类型、任务容器类型不匹配问题

### Phase D：仓库卫生与文档真实化

**目标**：删除不应入库的生成物，修正文档中未经验证的质量结论。

- [x] D1. 清理 benchmark 生成大文件与无必要基准产物
- [x] D2. 更新 `.gitignore` 与相关文档，明确生成物策略
- [x] D3. 更新架构/状态文档，移除夸大表述，改为基于本次验证结果的真实描述

### Phase F：架构模块化与边界收敛（在静态检查全绿后执行）

**目标**：在不回退既定方向的前提下，把当前“上帝对象/巨物文件”的压力释放到可维护模块。

- [ ] F1. `Coordinator` 减肥：从“上帝对象”收敛为“编排器”（抽出 entity registry / MQTT lifecycle / 更新循环编排）
- [ ] F2. `diagnostics_service.py` 拆包：contracts/coercions/capabilities/command_result/sensor_history 分层，并保留旧入口 re-export
- [ ] F3. 服务层边界硬化：禁止 service 触达 `runtime._xxx` 私有链（例如 state_service 对 updater 的私有访问）
- [ ] F4. Protocol 与实现分层：contracts 只保留合同，不夹带实现类
- [ ] F5. 命名一致性：统一“同一概念只有一种叫法”，旧名集中于 shim/兼容层

#### Phase F 拆分路线（最小风险）

- [ ] F1.1 抽出 entity registry/索引胶水（Coordinator → StateRuntime）
- [ ] F1.2 抽出 MQTT lifecycle（setup/connect/disconnect）并保持 Coordinator API 不变
- [ ] F1.3 抽出更新循环编排器（UpdateOrchestrator），Coordinator 仅保留 HA glue + 注入
- [ ] F2.1 新增 `services/diagnostics/` 包，先迁移纯函数与 TypedDict
- [ ] F2.2 `diagnostics_service.py` 收敛为 re-export + 薄胶水（保持原 import 路径兼容）
- [ ] F3.1 Runtime 增补必要 public 方法，移除 service 对私有属性/内部类的依赖
- [ ] F4.1 新建 contracts/protocols 文件，仅放 Protocol/TypeAlias/TypedDict
- [ ] F4.2 contracts 不反向 import 实现；实现留在 `runtime/` 下
- [ ] F5.1 建立“术语对照表”（canonical 命名）并在 shim/compat 层集中兼容旧名

> 验收建议：执行 Phase F 后，`coordinator.py` 目标 < 350 行；`diagnostics_service.py` 目标 < 150 行（仅胶水/导出）。

### Phase G：长期可维护性升级（可选）

**目标**：在 A–F 全绿后再进入“深水区”拆分，降低一次性风险。

- [ ] G1. 拆 `core/command/result.py`（大文件）为包化子模块，并保留原路径 re-export
- [ ] G2. 拆 `core/api/status_service.py` 为 `core/api/status/` 子模块，降低冲突与复杂度

### Phase E：全量验证与收尾

**目标**：以统一命令完成最终验收，并将结果回填到本计划文档。

- [ ] E1. 运行 `uv run ruff check .`
- [ ] E2. 运行 `uv run --extra dev mypy custom_components/lipro tests`
- [ ] E3. 运行 `uv run pytest -q`
- [ ] E4. 回填最终结果与剩余风险（若无则标注“无”）

---

## 4. 风险与处理策略

| 风险 | 表现 | 处理策略 |
|---|---|---|
| 契约面过大 | 一个 TypedDict 改动引发多处连锁 | 先统一定义，再批量收口调用方 |
| facade 静态能力缺失 | 运行时能访问，mypy 不认可 | 优先补充显式属性/协议，而非到处 `cast` |
| 测试误导设计 | 为兼容旧测试回退接口 | 以生产代码真实边界为准，必要时更新测试 |
| 文档再次失真 | 手工维护后很快过期 | 仅写入本次验证得到的事实和命令结果 |

---

## 5. 本次执行记录

- [x] 建立重构完善计划文档
- [x] 完成 Phase A（ruff/pytest 全绿）
- [x] 开始 Phase B
- [ ] 开始 Phase C
- [x] 开始 Phase D
- [ ] 开始 Phase E
- [ ] 开始 Phase F
- [ ] 开始 Phase G

## 6. 最终验收结果

> 待执行完成后回填。

- `ruff`: 待回填
- `mypy`: 待回填
- `pytest`: 待回填
- 剩余风险: 待回填
