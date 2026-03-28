# 104-01 Summary

- 把 `custom_components/lipro/control/service_router_handlers.py` 收窄为 thin family index。
- 新增 `service_router_{command,schedule,share,diagnostics,maintenance}_handlers.py`，分别承接 focused callback family。
