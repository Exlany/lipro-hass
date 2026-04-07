# Phase 04: Capability Model 统一 - Research

**Researched:** 2026-03-12
**Status:** Active

## Research Question

在不受历史兼容成本约束的北极星标准下，设备能力真相应放在哪里、以什么对象暴露、如何让 `core/device`、platform、entity 与后续 command model 都围绕它演进？

## Evaluated Options

### Option A — 继续把 capability truth 放在 `core/device/`
- **优点**：改动最小；
- **缺点**：设备聚合、能力真相、平台投影继续纠缠，难以建立清晰 formal home；
- **裁决**：拒绝。它会延续“设备 facade 顺便拥有一切规则”的历史路径。

### Option B — 用零散 helper / 常量表拼装能力
- **优点**：迁移成本低；
- **缺点**：没有明确 owner，平台/实体极易继续生长第二套规则；
- **裁决**：拒绝。它不能满足 `DOM-01 ~ DOM-05`。

### Option C — 建立 `core/capability/` 正式领域面
- **优点**：formal home 清晰；snapshot 可稳定投影给平台/实体；compat bridge 可显式受控；
- **缺点**：需要一次性回写 device slice 与治理文档；
- **裁决**：接受。这是最符合北极星终态的结构。

## Chosen Shape

`04-01` 采用以下落地形态：
- `CapabilitySnapshot`：不可变能力快照，承载 category、platforms、capability flags、设备能力边界值；
- `CapabilityRegistry`：唯一正式构造入口，负责把 device profile / device aggregate 归一成 snapshot；
- `DeviceCapabilities`：显式 compat bridge，仅服务历史导入路径；
- `device_snapshots.py` / `device_views.py`：改为消费 registry / snapshot，而不是再自行求值。

## Why This Is Optimal

- **显式组合**：registry 负责构造，snapshot 负责表达，device 负责聚合；
- **单一主链**：category / platforms / boolean capability flags 都收敛到 snapshot；
- **兼容可计数**：`DeviceCapabilities` 被降级为桥，不再是 formal owner；
- **后续可扩展**：`04-02` 可以把 entity/platform 统一切到 snapshot，`04-03` 再清退重复规则与旧 helper。

## Non-Goals for 04-01

- 不在本轮引入 command model；
- 不在本轮删掉所有旧访问名；
- 不在本轮引入重型 schema 框架或额外依赖；
- 不在本轮把所有平台文件一起重构完。
