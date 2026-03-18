# 27-03 Summary

## Outcome

- `.planning/baseline/PUBLIC_SURFACES.md`、`.planning/baseline/DEPENDENCY_MATRIX.md`、`.planning/baseline/VERIFICATION_MATRIX.md`、`.planning/codebase/STRUCTURE.md` 与 `.planning/reviews/RESIDUAL_LEDGER.md` 已统一到 `protocol_service` 正式能力口与 forwarder retirement 的新真相。
- 文档现在诚实记录 `LiproRestFacade` 的剩余热点属于 child-façade maintainability debt，而不是 second root 或被误包装成“已解决”。
- `Coordinator.client` ghost seam 的退场、runtime-owned formal surface 与 residual honesty 已形成单源叙事，不再允许 derived map 继续讲旧故事。

## Key Files

- `.planning/baseline/PUBLIC_SURFACES.md`
- `.planning/baseline/DEPENDENCY_MATRIX.md`
- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/codebase/STRUCTURE.md`
- `.planning/reviews/RESIDUAL_LEDGER.md`

## Validation

- `uv run pytest -q tests/meta/test_governance_guards.py tests/meta/test_governance_closeout_guards.py tests/meta/test_public_surface_guards.py tests/meta/test_version_sync.py tests/meta/test_toolchain_truth.py` → `74 passed`

## Notes

- `.planning/codebase/*.md` 继续只是 derived collaboration maps；本 tranche 的目标是让派生图谱追上权威真源，而不是反向定义真相。
