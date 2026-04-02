# Phase 135 Context

- 触发原因：契约者在 `Phase 134` closeout-ready 后继续要求一次性、彻底地清理 repo-wide 剩余 sanctioned hotspots。
- 目标对象：`custom_components/lipro/control/runtime_access.py`、`custom_components/lipro/core/coordinator/services/auth_service.py`、`custom_components/lipro/core/command/dispatch.py` 及其直接 contract consumers。
- 执行原则：不新增第二条故事线；继续沿 single formal home、typed contract、inward support split、focused guards 推进。
- 当前 phase 只解决仍值得进入正式路线的剩余热点，不重写已在 `Phase 134` 完成的 owner/projection/fan truth story。
