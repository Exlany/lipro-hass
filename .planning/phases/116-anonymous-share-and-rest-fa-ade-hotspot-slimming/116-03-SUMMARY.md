# Summary 116-03

## What changed
- 把 `.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md` 的 machine-readable route contract、prose 状态与默认下一步统一前推到 `Phase 116 complete; Phase 117 discuss-ready`。
- 更新 `docs/developer_architecture.md` 与 `.planning/baseline/VERIFICATION_MATRIX.md` 的 current-route/default-next wording。
- 更新 `tests/meta/governance_current_truth.py`、`tests/meta/test_governance_route_handoff_smoke.py` 与 `tests/meta/test_phase112_formal_home_governance_guards.py`，让 parser-visible truth、handoff smoke 与 developer-facing note 保持同一条 current story。

## Why it changed
- 如果只完成代码热点而不推进 route truth，`$gsd-next` 与 focused governance guards 就会继续停留在 `Phase 116 discuss-ready`，形成 docs/parser/test 三方分叉。
- `Phase 116` 的成功标准不仅是代码瘦身，还包括 current-route continuity 与 machine-checkable selector family 的同步前推。

## Verification
- `uv run pytest -q tests/meta/test_governance_bootstrap_smoke.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/test_phase112_formal_home_governance_guards.py`

## Outcome
- `v1.32` active route 现在明确停在 `Phase 116 complete; Phase 117 discuss-ready`，`$gsd-next` 将自然前推到 `Phase 117` continuation。
