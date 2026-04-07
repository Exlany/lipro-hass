# 45-01 Summary

- Completed on `2026-03-20`.
- Split the `rest_decoder_support.py` hotspot along existing protocol-boundary seams by extracting catalog/status/member normalization helpers and moving schedule/MQTT-config endpoint-specific decoding closer to `rest_decoder.py`.
- Kept the formal decoder boundary stable: no new public root or package export was introduced, and schedule/MQTT payload fingerprinting continues to flow through the existing REST decoder contract.
- Expanded targeted helper coverage in `tests/core/api/test_helper_modules.py` while keeping the protocol contract matrix green against the unchanged boundary story.
- Verified with `uv run pytest tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_helper_modules.py -q` (`48 passed`).
