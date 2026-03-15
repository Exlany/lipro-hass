# 17 Verification

status: passed

- `RES-03`: `_ClientTransportMixin`、`_ClientBase` skeleton 与 endpoint legacy mixin family 已从 production truth 退场；formal REST path 只剩显式 collaborator composition + local typed ports。
- `TYP-05`: token persistence 只消费 `AuthSessionSnapshot`；outlet-power helper/runtime formal path 只承认 explicit `row | list[row]` contract，不再生成 synthetic `{"data": rows}`。
- `MQT-01`: legacy `LiproMqttClient` naming 已退出治理与生产主线；`MqttTransportClient` 只保留为 localized concrete transport，并受 no-export bans 与 locality guard 约束。
- `GOV-15`: `ROADMAP`、`REQUIREMENTS`、`STATE`、baseline、review ledgers、Phase 17 artifacts 与 `v1.1` milestone audit 已讲同一条 closeout story；未发现新的 silent defer。

## Final Audit Summary

- Final gate on `2026-03-15` passed as one coherent closeout chain:
  - `uv run ruff check .`
  - `uv run python scripts/check_architecture_policy.py --check`
  - `uv run python scripts/check_file_matrix.py --check`
  - `uv run mypy`
  - `uv run pytest -q`
- Result summary:
  - `ruff` ✅
  - governance scripts ✅
  - `mypy` ✅ (`Success: no issues found in 440 source files`)
  - full `pytest` ✅ (`2196 passed in 38.32s`)
- Targeted Phase 17 regression slices also passed:
  - API/auth/power slice: `383 passed in 5.19s`
  - MQTT/locality slice: `174 passed in 2.51s`
  - governance/meta slice: `59 passed in 4.23s`
- Final repo audit recount for `custom_components/lipro`:
  - `Any=0`
  - `except Exception=36`
  - `type: ignore=1`
- Remaining debt is now restricted to explicit out-of-scope/de-scope items recorded in `.planning/v1.1-MILESTONE-AUDIT.md`; no Phase 16 carry-forward residual remains active.
