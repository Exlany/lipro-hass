# Phase 86 Validation

## Goal-backward validation

1. **Delete-gate honesty:** `ShareWorkerClient` 的 `_safe_read_json()` alias 与 bool `submit_share_payload()` shim 被真正删除，且 tests 不再围绕 legacy contract 组织断言。
2. **Single-root runtime truth:** `runtime_infra.py` 继续是唯一 outward formal home；若新增 local helper module，它只能被 `runtime_infra.py` inward import，不能演化成 second root 或 helper-owned public truth。
3. **Governance/baseline closeout:** `PROJECT / ROADMAP / REQUIREMENTS / STATE / MILESTONES / VERIFICATION_MATRIX / PUBLIC_SURFACES / DEPENDENCY_MATRIX / FILE_MATRIX / RESIDUAL_LEDGER / KILL_LIST / V1_23_TERMINAL_AUDIT` 必须共同承认 post-Phase-86 truth，而不是只改一半。
4. **Route progression clarity:** current route 必须诚实前推到 `Phase 86` 的执行态或 closeout 态，`default_next_command`、phase status、current phase / next phase 推断与 tests/meta truth helper 保持一致。
5. **No scope bleed:** `Phase 87` assurance giant topicization 与 `Phase 88` governance freeze / milestone closeout 继续保持 deferred，不得被 `Phase 86` 的 closeout 文案冒领。

## Validation Bundle

- `uv run pytest -q tests/core/test_share_client_primitives.py tests/core/test_share_client_refresh.py tests/core/test_share_client_submit.py tests/core/anonymous_share/test_manager_submission.py`
- `uv run pytest -q tests/core/test_runtime_infra.py tests/core/test_init_runtime_setup_entry.py tests/core/test_init.py tests/core/test_entry_root_wiring.py`
- `uv run pytest -q tests/meta/test_phase61_formal_home_budget_guards.py tests/meta/test_phase69_support_budget_guards.py tests/meta/test_phase70_governance_hotspot_guards.py tests/meta/test_phase72_runtime_bootstrap_route_guards.py tests/meta/dependency_guards_service_runtime.py tests/meta/test_phase85_terminal_audit_route_guards.py tests/meta/test_governance_route_handoff_smoke.py tests/meta/governance_followup_route_current_milestones.py tests/meta/test_version_sync.py`
- `uv run python scripts/check_file_matrix.py --check`
- `uv run python scripts/check_architecture_policy.py --check`

## Exit conditions

- `HOT-37`：production residual / hotspot carriers 的 delete-gate 与 inward split 结果能被代码、focused tests 与 ledger truth 一起解释。
- `ARC-22`：protocol / runtime / control / domain 仍然维持单一正式主链；没有新 second root、没有 helper-owned public truth、没有 backdoor。
- current route / verification docs / baseline docs / review ledgers 的 post-Phase-86 truth 一致，且 `gsd-tools` / meta guards 能自动识别。
