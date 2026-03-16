# 20-01 Summary

## Outcome

- Formalized `rest.list-envelope@v1` as an explicit registry-backed REST boundary family instead of leaving list-shape truth buried inside endpoint-specific helpers.
- Formalized `rest.schedule-json@v1` as the canonical schedule triple family and wired request-side `scheduleJson` encoding plus decode-side normalization to the same truth.
- Added authority/replay coverage for the remaining REST families so contract tests, replay harness, and asset guards can all see the same public-path story.

## Key Files

- `custom_components/lipro/core/protocol/boundary/rest_decoder.py`
- `custom_components/lipro/core/protocol/boundary/__init__.py`
- `custom_components/lipro/core/protocol/contracts.py`
- `custom_components/lipro/core/api/schedule_codec.py`
- `custom_components/lipro/core/api/schedule_endpoint.py`
- `custom_components/lipro/core/api/endpoints/schedule.py`
- `tests/fixtures/api_contracts/query_mesh_schedule_json.v1.json`
- `tests/fixtures/protocol_replay/rest/get_device_list.envelope.replay.json`
- `tests/fixtures/protocol_replay/rest/query_mesh_schedule_json.v1.replay.json`
- `tests/core/api/test_protocol_contract_matrix.py`
- `tests/core/api/test_protocol_replay_rest.py`
- `tests/core/api/test_schedule_codec.py`

## Validation

- `uv run pytest -q tests/core/api/test_protocol_contract_matrix.py tests/core/api/test_protocol_replay_rest.py -k "device_list or list or schedule_json or replay"`
- `uv run pytest -q tests/core/api/test_schedule_codec.py tests/core/api/test_schedule_endpoint.py tests/core/api/test_api_schedule_endpoints.py tests/core/api/test_api_schedule_service.py tests/core/api/test_api_schedule_candidate_queries.py tests/services/test_services_schedule.py tests/core/api/test_api.py -k "schedule"`
