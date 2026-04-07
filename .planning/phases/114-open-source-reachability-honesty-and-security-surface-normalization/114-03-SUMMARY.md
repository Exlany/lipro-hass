# Summary 114-03

## What changed
- 把 `.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/REQUIREMENTS.md`、`.planning/STATE.md`、`.planning/MILESTONES.md` 与 `tests/meta/governance_current_truth.py` 一次性前推到 `v1.31 active route / Phase 114 complete / closeout-ready`。
- 修复 `ROADMAP.md` 与 `STATE.md` 的 progress drift：`Phase 113/114` 不再出现 `0/TBD`、`Not started` 或重复脏行；state frontmatter、完成数与计划数现与 phase 资产和 `gsd-tools` 输出一致。
- 将默认下一步统一切换为 `$gsd-complete-milestone v1.31`，使 `gsd-next` 的自然落点与 route truth 完全一致。

## Why it changed
- 若 route/progress/governance current truth 仍停在 discussion-ready，仓库就会再次出现“代码与 phase 资产已完成，但机器真相仍停在旧态”的半收口状态。
- Wave 3 的职责不是新增功能，而是把已完成的 `Phase 114` 与下一跳 milestone closeout 讲成同一条可审计故事线。

## Verification
- `uv run pytest -q tests/flows/test_flow_credentials.py tests/services/test_services_registry.py tests/meta/test_governance_release_docs.py tests/meta/test_governance_release_continuity.py tests/meta/test_version_sync.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/test_phase114_open_source_surface_honesty_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py`
- `90 passed in 2.10s`
- `bash -n scripts/lint`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run ruff check custom_components/lipro/flow/credentials.py tests/flows/test_flow_credentials.py tests/meta/test_phase114_open_source_surface_honesty_guards.py tests/meta/test_governance_release_continuity.py tests/meta/test_version_sync.py tests/meta/toolchain_truth_docs_fast_path.py tests/meta/governance_current_truth.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" state json`
- `node "$HOME/.codex/get-shit-done/bin/gsd-tools.cjs" init progress`

## Outcome
- `Phase 114` 的 active-route 真相现已切换到 closeout-ready；剩余动作只应是 milestone closeout，而不是继续开启新的 active phase。
