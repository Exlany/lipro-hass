# Plan 124-03 Summary

## What changed

- `custom_components/lipro/services/contracts.py` 已新增 schedule direct-call payload normalizer、typed result contract 与 normalized row surface。
- `custom_components/lipro/services/schedule_support.py` 已接管 payload validation、request building 与 row normalization，让 schedule support truth 不再挤压正式 orchestration 模块。
- `custom_components/lipro/services/schedule.py` 已改为只保留 shared execution/error orchestration，并显式继续声明 translated `invalid_schedule_request`。
- `custom_components/lipro/translations/en.json` 与 `custom_components/lipro/translations/zh-Hans.json` 已补齐 `invalid_schedule_request`。

## Outcome

- `ARC-36` / `TST-46` 的 schedule direct-call formal contract 已冻结。
- schedule handler path 不再维持第二套 handler-local ad-hoc dict 语义。
- `services/schedule.py` 已压回 Phase 69 line-budget 之内，同时保持 formal contract truth 不分叉。
