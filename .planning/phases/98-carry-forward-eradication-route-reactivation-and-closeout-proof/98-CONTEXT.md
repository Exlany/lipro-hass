# Phase 98: Carry-forward eradication, route reactivation, and closeout proof - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

`Phase 98` 承接 `v1.26` archived closeout之后真实已经发生但尚未被 current-route 诚实承认的变化：`outlet_power` legacy side-car fallback 已物理删除，但 planning/governance/parser truth 仍停在 archived-only route。本 phase 的职责是把这段真实 carry-forward eradication 与 route reactivation 写回成一条 active / closeout-ready 主线。
</domain>

<decisions>
## Implementation Decisions
- **D-01:** `v1.26` archived bundle 继续保持 pull-only latest archived baseline 身份，不允许反向回写成 live current story。
- **D-02:** `Phase 98` 只处理真实已发生的 carry-forward 收口、route reactivation、focused guards 与 proof chain，不借机重开新功能或伪造第二条重构故事线。
- **D-03:** large formal homes (`command_runtime.py`、`mqtt_runtime.py`、`anonymous_share/manager.py`) 继续保持 formal-home truth；本 phase 只做低风险、可证明的局部收口，而不冒进展开大拆迁。
</decisions>
