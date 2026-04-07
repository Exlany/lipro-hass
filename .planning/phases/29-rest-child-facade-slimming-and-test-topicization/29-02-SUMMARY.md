# 29-02 Summary

## Outcome

- command / pacing 相关断言已从巨型 `tests/core/api/test_api.py` 中抽出更明确的主题切片，`RequestPolicy` 继续作为 busy-retry 与 pacing contract 的正式 owner。
- `custom_components/lipro/core/api/client.py` 的 `iot_request_with_busy_retry()` 现在通过 `RequestPolicy` 执行正式 busy-retry contract，而不是把 pacing 细节重新散落回 façade 私有 helper。
- `tests/core/test_command_dispatch.py` 与 `tests/core/api/test_protocol_contract_matrix.py` 保持 command / pacing / busy 的正式黑盒断言，不因 topicization 牺牲行为覆盖。

## Key Files

- `custom_components/lipro/core/api/client.py`
- `custom_components/lipro/core/api/request_policy.py`
- `custom_components/lipro/core/api/command_api_service.py`
- `tests/core/api/test_api.py`
- `tests/core/test_command_dispatch.py`
- `tests/core/api/test_protocol_contract_matrix.py`

## Validation

- `uv run pytest -q tests/core/api/test_api.py tests/core/test_command_dispatch.py tests/core/api/test_protocol_contract_matrix.py -k "command or pacing or busy"`

## Notes

- 本 plan 没有创造第二条 command path；收口全部仍 anchored 在 REST child façade -> request policy -> command service 的单一路径。
