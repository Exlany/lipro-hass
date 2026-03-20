# Phase 45 Research

**Date:** 2026-03-20
**Status:** Final
**Plans / Waves:** 4 plans / 4 waves

## What The Review Confirmed

- `custom_components/lipro/core/protocol/boundary/rest_decoder_support.py` (`401` 行)、`custom_components/lipro/core/api/diagnostics_api_service.py` (`313` 行)、`custom_components/lipro/core/anonymous_share/share_client.py` (`246` 行)、`custom_components/lipro/core/mqtt/message_processor.py` (`193` 行) 仍是最显著的热点聚集区；
- `share_client.py` 的 `apply_token_payload()`、`refresh_install_token()`、`submit_share_payload()` 广泛使用 `bool` 返回与 `return False`，把 token invalid、rate limit、timeout、schema error、HTTP failure 等差异抹平成单一失败语义；
- `custom_components/lipro/core/coordinator/runtime/mqtt/message_handler.py` 仍以 `bool` 表达 message 应用结果，无法稳定区分 unknown device、empty props、no applied properties 与 real failure；
- `diagnostics_api_service.py` 在 OTA v1/v2/controller fallback 上已有丰富 degrade 逻辑，但缺少稳定的 typed outcome / reason code 契约，仍偏向“日志可读、机器难消费”；
- `.github/workflows/ci.yml` 与 `tests/meta/test_toolchain_truth.py` / `tests/meta/test_governance_release_contract.py` 继续把 benchmark 描述为 `advisory-with-artifact`，说明当前只做产物留存，尚未达到 baseline compare / threshold warning / no-regression gate 的正式要求。

## Risk Notes

- 如果只把热点文件拆成更小文件，而不顺手收 typed failure semantics，复杂度只是移动位置，不会真正降低维护成本；
- typed result / reason code 若重新发明 vocabulary，会与仓内既有 `failure_summary` taxonomy、protocol boundary result 模式和 command/result 分类语言并存，反而制造第三套失败故事；
- benchmark 从 advisory 升到 anti-regression contract 若一步过猛，容易把波动较大的性能测试直接变成 flaky gate；必须先定义 baseline、阈值与适用场景，再决定是否阻断；
- hotspot decomposition 若扩张 public surface 或新造 manager hierarchy，会违背 north-star 的单链/显式组合原则。

## Chosen Strategy

1. 先沿现有 boundary / façade seams 拆 `rest_decoder_support.py`，优先抽离 normalization / mapping / fallback 家族，而不是另起新 root；
2. 再对 diagnostics 与 anonymous-share 路径建立 typed result / reason code contract，复用仓内已有 failure taxonomy vocabulary；
3. 然后收 MQTT message processing / handler 的 typed outcome，并同时补 touched-zone typed budget / no-growth guard；
4. 最后把 benchmark 升级成带 baseline compare、threshold warning 与 no-regression 语义的质量故事，并同步 workflow、docs 与 meta guards。

## Validation Focus

- `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_api_diagnostics_service.py -q`
- `uv run pytest tests/core/test_share_client.py tests/services/test_services_share.py -q`
- `uv run pytest tests/core/mqtt/test_message_processor.py tests/benchmarks/test_command_benchmark.py tests/benchmarks/test_mqtt_benchmark.py tests/benchmarks/test_device_refresh_benchmark.py tests/benchmarks/test_coordinator_performance.py -q`
- `uv run pytest tests/meta/test_toolchain_truth.py tests/meta/test_governance_release_contract.py tests/meta/test_governance_closeout_guards.py -q`
