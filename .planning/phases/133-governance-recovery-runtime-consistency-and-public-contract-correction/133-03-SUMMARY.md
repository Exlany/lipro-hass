# Plan 133-03 Summary

- `climate` 与 `vent fan` 的非法 preset / 未知 vendor mode 现已改为显式 no-op / `None`，不再伪装成合法默认值。
- README / README_zh / TROUBLESHOOTING / services.yaml / quality_scale 已与真实实现对齐。
- Public contract 现已把 developer probes 降级为 debug-mode-only escalation paths。
