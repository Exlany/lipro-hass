# Summary 113-01

## What changed
- 将 `custom_components/lipro/core/anonymous_share/share_client_submit.py` 从 455 行 submit hotspot 收窄为 170 行 thin orchestrator，只保留 preflight、refresh 与顶层提交编排。
- 新增 `custom_components/lipro/core/anonymous_share/share_client_submit_outcomes.py`，承接 submit HTTP failure / timeout / client error / unexpected error / rate-limit outcome builders。
- 新增 `custom_components/lipro/core/anonymous_share/share_client_submit_attempts.py`，承接 variant/token attempt loop、413→lite fallback、429 retry-after、token rejection 与 invalid-schema resolution。
- 保持 outward submit contract 与 importer story 不变：匿名分享主链仍经由 `share_client_flows.py` 进入 `share_client_submit.py`。

## Why it changed
- `QLT-46` 要求继续 burn down 当前 production hotspots，同时避免重开 `anonymous_share/manager.py` 或 share public root 的 blast radius。
- submit 流程天然可沿 outcome / attempt / orchestration 三层收口，是本 phase 最低风险且高收益的 inward split 点。

## Verification
- `uv run pytest -q tests/core/test_share_client_submit.py`
- `46 passed in 0.89s`
- `uv run ruff check custom_components/lipro/core/anonymous_share/share_client_submit.py custom_components/lipro/core/anonymous_share/share_client_submit_attempts.py custom_components/lipro/core/anonymous_share/share_client_submit_outcomes.py tests/core/test_share_client_submit.py`
- `All checks passed!`

## Outcome
- submit hotspot 现已变成清晰的 thin orchestrator，本地 helper 家族边界更诚实。
- focused submit tests 证明 token fallback、413→lite、429 backoff 与 outcome semantics 没有回归。
