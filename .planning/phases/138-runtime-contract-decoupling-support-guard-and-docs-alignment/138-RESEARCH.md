# Phase 138 Research

## Findings

1. `custom_components/lipro/runtime_types.py` 直接依赖 `services/contracts.py`，让 root-level runtime contract 倒向 service schema home。
2. `control/service_router_support.py` 名称保留了 `support`，但当前 formal role 是 service callback 热路径的唯一 `(device, coordinator)` bridge；需要 docs/tests 钉死“不是 public root”。
3. `docs/README.md` 与 `docs/developer_architecture.md` 已区分 current docs 与 archive appendix，但仍缺少对新 root-level service contract truth 的显式说明。
4. `status_service.py` 内部虽已建模 `ConnectStatusOutcome`，但 outward chain 仍通过 `query_connect_status() -> dict[str, bool]` 把 `API_ERROR / WRAPPED_NON_MAPPING / EMPTY_MAPPING` 一并压平成 `{}`。
5. selector family 当前停在 `Phase 137 complete`，若继续 closeout 会把 residual cleanup 再次留作隐性 tech debt。

## Chosen Approach

- 不大改 milestone 名称或 archived baseline story。
- 在同一 `v1.42` 下新增 `Phase 138` 作为 terminal cleanup phase，并把晚发现的 `OBS-01` outward-contract 缺口一并吸收。
- 先抽出 `service_types.py`，再用 docs/baselines/tests 把 formal-home、connect-status outcome 与 support naming 语义钉死。
