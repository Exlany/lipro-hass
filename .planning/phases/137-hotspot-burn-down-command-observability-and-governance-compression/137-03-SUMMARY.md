# Plan 137-03 Summary

- 已修复 `custom_components/lipro/core/command/dispatch.py` 的 group-error fallback 双发缺陷，并把 fallback warning 收紧为 redacted identifier + safe error placeholder。
- 已重构 `custom_components/lipro/core/api/status_service.py` 的 connect-status path：内部显式区分 API error / malformed / wrapped non-mapping / empty mapping，只向外投影 sanitized request set。
- 已为 `custom_components/lipro/core/device/device.py` 补足 outlet-power copy / MQTT freshness regressions，并同步 focused device/command/status tests。
