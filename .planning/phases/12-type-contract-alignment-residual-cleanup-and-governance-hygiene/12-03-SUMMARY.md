# 12-03 Summary

- 删除 `core.api.LiproClient`、`LiproProtocolFacade.get_device_list`、`LiproMqttFacade.raw_client` 与 `DeviceCapabilities` 生产 compat seam。
- `core/api/__init__.py`、`core/device/__init__.py` 与 tests imports 同步切到正式 surface。
