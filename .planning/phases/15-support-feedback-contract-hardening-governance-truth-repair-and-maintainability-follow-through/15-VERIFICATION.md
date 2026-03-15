# 15 Verification

status: passed

- `SPT-01`: developer feedback upload contract 已明确保留 `iotName` 等供应商判型真源，同时匿名化用户自定义标签；local debug view 与 upload projector 分家。
- `GOV-13`: `PROJECT.md` / `ROADMAP.md` / `STATE.md` / `REQUIREMENTS.md` 与 Phase 15 assets 已同步到同一完成态，active source paths 由 `scripts/check_file_matrix.py` fail-fast 校验。
- `DOC-01`: README / README_zh / CONTRIBUTING / SUPPORT / SECURITY / bug template / CI 对最低支持 `Home Assistant 2026.3.1` 与 private-repo HACS caveat 保持一致。
- `HOT-03` / `TYP-03`: `service_router.py` 保持 public handler home，developer/support helper 与 `runtime_access.py` 的类型边界继续收薄。
- `QLT-01` / `RES-01`: `coverage_diff.py`、benchmark、dev `pip-audit` 与 residual locality 已形成 guard-backed documented arbitration；`_ClientBase` 与 `LiproMqttClient` 未回流为正式 surface。
