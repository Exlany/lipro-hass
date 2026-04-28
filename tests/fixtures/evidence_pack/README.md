# Evidence Pack Fixture Rules

- `AI Debug Evidence Pack` 只允许 pull 正式真源：`07.3` exporter truth、`07.4` replay evidence、`07.5` governance/evidence index 与已登记 authority docs。
- evidence pack 允许真实时间戳，用于 AI 调试与问题定位。
- `entry_ref` / `device_ref` 等引用必须报告内稳定、跨报告不可关联。
- token / secret / `password_hash` / `access_key` / `refresh_access_key` 等凭证等价物永不允许进入 pack。
- exporter entrypoint 只能是 `scripts/export_ai_debug_evidence_pack.py`。
