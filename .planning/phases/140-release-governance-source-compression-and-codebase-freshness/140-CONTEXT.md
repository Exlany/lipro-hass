# Phase 140 Context

## Goal

压缩 release/governance source duplication，刷新 stale verification commands，并把 public/internal docs contract 重新对齐：

- baseline / archived remediation docs 中仍引用已删除或迁移的测试路径
- `CHANGELOG.md` 的 Unreleased 段落混入 `.planning` / phase-internal 术语
- maintainer runbook 对 private-access / future public mirror / release asset reachability 的条件语义不够明确
- `tests/meta` 对 changelog public-summary 与 conditional release wording 的守卫不足

## Inputs

- `.planning/baseline/VERIFICATION_MATRIX.md`
- `.planning/reviews/V1_41_REMEDIATION_CHARTER.md`
- `CHANGELOG.md`
- `SUPPORT.md`
- `docs/MAINTAINER_RELEASE_RUNBOOK.md`
- `tests/meta/test_governance_release_docs.py`
- `tests/meta/test_governance_release_continuity.py`

## Exit Truth

## Additional Audit Findings

- `custom_components/lipro/control/service_router.py` / `service_router_handlers.py` / `service_router_support.py` 仍有 callback onion layering 与 underscore helper public-surface leakage，属于下一轮 control-plane narrowing 候选。
- `custom_components/lipro/runtime_types.py` 仍是跨平面 contract hub，需继续评估如何在不重引循环依赖的前提下压低 breadth。
- `custom_components/lipro/core/device/device.py` 仍保留较宽 façade + side-car extra-data 清理模式，后续应继续收紧 aggregate boundary。
- `custom_components/lipro/control/entry_root_support.py` 仍大量依赖 string module names / lazy import factories，属于开源维护税热点。

- current / archived verification commands 均不再引用不存在的测试路径
- `CHANGELOG.md` 回到 public-facing release summary 身份，不再承载 internal selector / `.planning` jargon
- private-access / mirror reachability / release asset availability 在 README/SUPPORT/runbook/tests 中使用一致条件语义
- docs/governance freshness drift 拥有 focused meta guards，而不是继续依赖人工复查
