---
requirements-completed: [ARC-26]
---

# 103-01 Summary

- 把 `custom_components/lipro/__init__.py` 中的 lazy-load / entry-auth / service-registry adapter 支撑抽回 `custom_components/lipro/control/entry_root_support.py`。
- 保持 `LiproProtocolFacade`、`LiproAuthManager` 与 `Coordinator` 的 outward contract 不变，测试 patch 面继续停在根入口。
