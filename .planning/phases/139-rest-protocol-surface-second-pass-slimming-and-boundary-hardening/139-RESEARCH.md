# Phase 139 Research

## Key Findings

- 当前最重的重复复杂度不在 transport executor 本身，而在多层 forwarding / wrapper / bound adapter family。
- `LiproRestFacade` 与 `rest_port.py` 已是 formal homes；最佳策略是 inward split，而不是制造新的 façade root。
- schedule family 中 `group_id` 在 protocol → rest → surface 链路存在语义漂移，是本轮真正的行为修复点。
- 嵌套 worktree 下 `gsd-tools` 对项目根识别不稳定，因此本 phase 需以 manual-equivalent GSD artifacts 为 route truth，而不伪造 CLI 输出。

## Chosen Strategy

1. `rest_port.py` 仅保留 typed contracts / family / bind helper，bound adapters 下沉到 `rest_port_bindings.py`。
2. `rest_facade.py` 仅保留 canonical composition / outward bindings，private mechanics 下沉到 `rest_facade_internal_methods.py`。
3. 用 focused tests + meta guards 冻结 line budgets、internal import locality 与 schedule forwarding truth。
4. 用 selector family / docs / baseline sync 把 `v1.43 active` route 真相一次切齐。
