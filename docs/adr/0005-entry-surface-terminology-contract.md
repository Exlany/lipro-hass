# ADR-0005: 入口适配器与 support/surface 术语契约

- **Status**: Accepted
- **Date**: 2026-03-28
- **Owners**: Architecture / maintainability

## 背景

随着 `v1.25 -> v1.28` 的多轮热点收敛，项目已经拥有较清晰的 formal home 拓扑，但在命名层仍残留一类认知噪音：`support`、`surface`、`wiring`、`handlers`、`facade` 经常同时出现，而读者未必能第一眼判断它们分别表示哪种职责边界。

这类噪音不会立刻造成功能错误，却会持续放大 onboarding、code review、phase planning 与 residual 审计的理解成本。尤其是根入口 thin adapter、control service callback family 与 protocol-plane façade 在同一轮重构中同时出现时，若术语没有契约，文档与测试很容易再次讲成两套故事。

## 决策

1. **`facade`** 只用于对外/跨层暴露的正式组合入口，例如 `LiproProtocolFacade`、`LiproRestFacade`、`LiproMqttFacade`
2. **`handlers`** 只用于 service callback 家族中的具体请求处理函数，不表示 formal root
3. **`support`** 只用于 inward collaborator / local helper home，表示对 formal home 的局部支撑，而不是第二主链
4. **`surface`** 只用于对上层暴露的稳定 read/write-facing surface，例如 diagnostics / system-health / telemetry surface
5. **`wiring`** 只用于显式装配与依赖绑定，不承担业务规则真源
6. HA 根层 `__init__.py`、`diagnostics.py`、`system_health.py`、`config_flow.py` 继续被描述为 **thin adapters**，不得再被叙述成 service/runtime/protocol 的真实 owner

## 取舍

### 收益

- review 与 phase planning 能更快判断“这是 formal home 还是 inward support”
- 文档、测试守卫与文件命名更容易围绕统一术语收敛
- 新增 support/helper 时更容易检查是否正在制造 second story

### 代价

- 一些历史命名暂时不会立刻全部改名，仍需要通过 ADR 与 phase note 做过渡解释
- 文档与测试要同步回写，否则会出现“代码已收敛、认知层未收敛”的短期维护成本

## 明确拒绝的替代方案

- 把 `support` 泛化成任何 helper 的统称：会再次模糊 formal home 与 local collaborator 的边界
- 把 `surface` 与 `facade` 混用：会让 protocol root、control surface、diagnostics API 难以区分
- 把 `wiring` 用作业务所有权术语：会把装配代码误讲成规则真源

## 后果

- 未来新增 `support` / `surface` / `handlers` / `wiring` / `facade` 命名时，必须能映射到本 ADR 的单一定义
- `docs/developer_architecture.md` 与 phase guards 需继续保持与本 ADR 一致
- 若某个模块既像 `support` 又像 `surface`，优先拆职责，而不是继续沿用混合命名

## 重议触发器

只有在以下情况之一出现时，才应重新讨论该决策：

1. Home Assistant 官方集成约定要求新的术语层级，且现有定义无法表达
2. protocol / runtime / control 出现新的正式对外 root，需要在 `facade` / `surface` 之外引入第三种长期术语
3. 当前术语契约被证明无法阻止第二主链或 helper-owned truth 的回流
