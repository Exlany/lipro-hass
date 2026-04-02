# Phase 137 Context

- 触发原因：契约者要求继续下一步，把 `lipro-hass` 的终极审阅直接转为一次性、深度、彻底的 active execution route，而不是继续停留在 archived audit 或多轮浅层扫描。
- 当前 route：`v1.42 active milestone route / starting from latest archived baseline = v1.41`
- 直接输入真源：`.planning/reviews/V1_41_TERMINAL_AUDIT_REPORT.md`、`.planning/reviews/V1_41_REMEDIATION_CHARTER.md`、`docs/NORTH_STAR_TARGET_ARCHITECTURE.md`、`AGENTS.md`、`.planning/baseline/GOVERNANCE_REGISTRY.json`、`.planning/baseline/VERIFICATION_MATRIX.md`。
- 审阅优先级：先压低 governance derivation / semantic-guard blind spot，再处理 protocol/rest/auth 高优先热点，最后收口 device/command/observability。
- 高优先热点：`custom_components/lipro/core/api/rest_facade.py`、`custom_components/lipro/core/protocol/facade.py`、`custom_components/lipro/core/auth/manager.py`。
- 中优先热点：`custom_components/lipro/core/device/device.py`、`custom_components/lipro/core/command/dispatch.py`、`custom_components/lipro/core/api/status_service.py`。
- 治理同步面：`.planning/{PROJECT,ROADMAP,REQUIREMENTS,STATE,MILESTONES}.md`、`.planning/baseline/GOVERNANCE_REGISTRY.json`、`.planning/baseline/VERIFICATION_MATRIX.md`、`docs/developer_architecture.md`、`docs/MAINTAINER_RELEASE_RUNBOOK.md`、`tests/meta/governance_*`。
- 输出要求：不是“修一点热点”就结束，而是让 phase plans 覆盖治理、代码热点、命令/观测语义与最终审查映射。
- 非目标：不回流 mixin/compat shell，不新建第二 authority chain，不伪造“全部 debt 已清零”的结论。
