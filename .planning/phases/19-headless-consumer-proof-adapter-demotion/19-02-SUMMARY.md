# 19-02 Summary

## Outcome

- Added `tests/harness/headless_consumer.py` as a proof-only consumer harness that authenticates through the shared headless boot seam and materializes devices/capability snapshots through the formal protocol and domain truth only.
- Added `tests/integration/test_headless_consumer_proof.py` to prove `auth -> device discovery -> replay/evidence bridge` reuses the same nucleus, including token-backed proof and non-authority proof identity checks.
- Extended replay/evidence authority regressions so headless proof families stay on the existing formal truth chain while proof assets remain outside the authority-source allowlist.

## Key Files

- `tests/harness/headless_consumer.py`
- `tests/integration/test_headless_consumer_proof.py`
- `tests/integration/test_protocol_replay_harness.py`
- `tests/integration/test_ai_debug_evidence_pack.py`
- `tests/harness/evidence_pack/sources.py`
- `tests/meta/test_evidence_pack_authority.py`

## Validation

- `uv run ruff check tests/harness/headless_consumer.py custom_components/lipro/headless/boot.py tests/integration/test_headless_consumer_proof.py tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/harness/evidence_pack/sources.py tests/meta/test_evidence_pack_authority.py`
- `uv run pytest -q tests/integration/test_headless_consumer_proof.py`
- `uv run pytest -q tests/integration/test_protocol_replay_harness.py tests/integration/test_ai_debug_evidence_pack.py tests/core/api/test_protocol_contract_matrix.py tests/core/capability/test_registry.py tests/snapshots/test_device_snapshots.py tests/meta/test_evidence_pack_authority.py`
