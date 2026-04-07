---
phase: 130-runtime-command-and-firmware-update-hotspot-decomposition
plan: "02"
summary: true
---

# Plan 130-02 Summary

## Completed

- `custom_components/lipro/entities/firmware_update.py` 已继续压回 thin entity shell：install request resolution、OTA query-context、refresh projection 与 background-task outcome 统一下沉到 `custom_components/lipro/entities/firmware_update_support.py`。
- `custom_components/lipro/entities/firmware_update_support.py` 新增 `resolve_install_request()`、`build_ota_query_context()`、`build_refresh_projection()`、`resolve_refresh_task_outcome()` 等 formal helpers；task done callback 命名已收口为 `_handle_refresh_task_done()`，同步/异步语义更诚实。
- `tests/platforms/test_update_background_tasks.py`、`tests/platforms/test_update_task_callback.py` 与 `tests/platforms/test_firmware_update_entity_edges.py` 已改成直接冻结 refresh-task outcome、projection apply 与 edge behavior；OTA unit suites 继续守住 bundled manifest / candidate / row-cache / selector authority。

## Outcome

- `LiproFirmwareUpdateEntity` 继续保持 runtime-boundary 之上的 protected thin projection shell，没有回流成第二个 OTA logic hub，也没有突破 `Phase 111` runtime/entity boundary。
- firmware-half 已满足本 phase 的 `ARC-41` / `HOT-60` / `TST-51` 范围：install/task/query/projection seams 更窄，命名与 ownership 更一致，focused proofs 能直接拦截 task lifecycle 与 projection drift。
