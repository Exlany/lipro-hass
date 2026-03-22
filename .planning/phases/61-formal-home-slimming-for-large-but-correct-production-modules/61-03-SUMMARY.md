# Plan 61-03 Summary

- `custom_components/lipro/core/ota/candidate.py` 继续作为唯一 outward OTA candidate home；certification / confirmation-window / install-policy logic 已 inward split 到 `custom_components/lipro/core/ota/candidate_support.py`。
- `custom_components/lipro/entities/firmware_update.py`、`tests/core/ota/test_ota_candidate.py` 与 `tests/platforms/test_update_install_flow.py` 继续从 `candidate.py` 导入稳定符号；`_InstallCommand`、`_OtaCandidate`、`OtaManifestTruth` 与 install/certification helpers 的 outward story 未漂移。
- 验证命令 `uv run pytest -q tests/core/ota/test_ota_candidate.py tests/core/ota/test_firmware_manifest.py tests/platforms/test_update.py tests/platforms/test_update_entity_refresh.py tests/platforms/test_update_install_flow.py tests/platforms/test_update_certification_policy.py tests/platforms/test_firmware_update_entity_edges.py tests/meta/test_firmware_support_manifest_repo_asset.py` 通过（`48 passed`）。
