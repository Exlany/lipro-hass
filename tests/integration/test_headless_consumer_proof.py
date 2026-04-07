"""Integration-style proof that a headless consumer reuses the canonical nucleus."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.lipro.core.auth import AuthBootstrapSeed, AuthSessionSnapshot
from tests.core.api.test_protocol_contract_boundary_decoders import (
    EXPECTED_DEVICE_LIST_DEVICES,
    EXPECTED_DEVICE_STATUS_ROWS,
    EXPECTED_MESH_GROUP_STATUS_ROWS,
)
from tests.harness.evidence_pack.collector import AiDebugEvidenceCollector
from tests.harness.evidence_pack.sources import (
    API_CONTRACT_ROOT,
    NON_AUTHORITY_PROOF_PATHS,
)
from tests.harness.headless_consumer import (
    HEADLESS_PROOF_ASSERTION_FAMILIES,
    HEADLESS_PROOF_PUBLIC_PATHS,
    HeadlessConsumerHarness,
)
from tests.harness.protocol import iter_replay_manifests


def _auth_session() -> AuthSessionSnapshot:
    return AuthSessionSnapshot(
        access_token='access',
        refresh_token='refresh',
        user_id=10001,
        expires_at=123.0,
        phone_id='proof-phone-id',
        biz_id='proof-biz-id',
    )


@pytest.mark.asyncio
async def test_headless_consumer_proof_materializes_devices_from_formal_truth() -> None:
    seed = AuthBootstrapSeed(
        phone='13800000000',
        phone_id='proof-phone-id',
        password_hash='hashed-value',
    )
    protocol = MagicMock(name='protocol')
    protocol.get_devices = AsyncMock(
        return_value={
            'devices': EXPECTED_DEVICE_LIST_DEVICES,
            'has_more': True,
        }
    )
    protocol.query_device_status = AsyncMock(return_value=EXPECTED_DEVICE_STATUS_ROWS)
    protocol.query_mesh_group_status = AsyncMock(
        return_value=EXPECTED_MESH_GROUP_STATUS_ROWS
    )
    boot_context = MagicMock(name='boot_context')
    boot_context.protocol = protocol
    boot_context.async_login_with_password_hash = AsyncMock(return_value=_auth_session())

    with patch(
        'tests.harness.headless_consumer.build_headless_boot_context',
        return_value=boot_context,
    ) as mock_build:
        proof = await HeadlessConsumerHarness(
            session=MagicMock(name='session'),
        ).async_collect(seed)

    assert proof.auth_session == _auth_session()
    assert proof.public_paths == HEADLESS_PROOF_PUBLIC_PATHS
    assert proof.assertion_families == HEADLESS_PROOF_ASSERTION_FAMILIES
    assert [device.serial for device in proof.devices] == [
        '03ab5ccd7c000001',
        'mesh_group_10001',
    ]
    assert proof.devices[0].wifi_ssid == 'mesh-net'
    assert proof.devices[0].capabilities == proof.capability_snapshots['03ab5ccd7c000001']
    assert proof.devices[1].is_group is True
    assert proof.devices[1].is_on is True
    mock_build.assert_called_once()
    protocol.get_devices.assert_awaited_once_with()
    protocol.query_device_status.assert_awaited_once_with(
        ['03ab5ccd7c000001', 'mesh_group_10001']
    )
    protocol.query_mesh_group_status.assert_awaited_once_with(['mesh_group_10001'])


@pytest.mark.asyncio
async def test_headless_consumer_proof_can_reuse_existing_tokens() -> None:
    seed = AuthBootstrapSeed(
        phone='13800000000',
        phone_id='proof-phone-id',
        access_token='access',
        refresh_token='refresh',
    )
    protocol = MagicMock(name='protocol')
    protocol.get_devices = AsyncMock(return_value={'devices': [], 'has_more': False})
    protocol.query_device_status = AsyncMock(return_value=[])
    protocol.query_mesh_group_status = AsyncMock(return_value=[])
    boot_context = MagicMock(name='boot_context')
    boot_context.protocol = protocol
    boot_context.async_login_with_password_hash = AsyncMock()
    boot_context.async_ensure_authenticated = AsyncMock(return_value=_auth_session())

    with patch(
        'tests.harness.headless_consumer.build_headless_boot_context',
        return_value=boot_context,
    ):
        proof = await HeadlessConsumerHarness(
            session=MagicMock(name='session'),
        ).async_collect(seed)

    assert proof.auth_session == _auth_session()
    boot_context.async_ensure_authenticated.assert_awaited_once_with()
    assert boot_context.async_login_with_password_hash.await_count == 0


def test_headless_consumer_proof_bridges_to_replay_and_evidence_truth() -> None:
    replay_families = {manifest.family for manifest in iter_replay_manifests()}
    evidence_payload = AiDebugEvidenceCollector().collect(
        report_id='headless-proof-bridge',
        generated_at='2026-03-16T00:00:00Z',
    ).to_dict()

    assert set(HEADLESS_PROOF_ASSERTION_FAMILIES).issubset(replay_families)
    assert API_CONTRACT_ROOT in evidence_payload['boundary']['source_paths']
    assert API_CONTRACT_ROOT in evidence_payload['index']['section_authority_trace']['boundary']
    for proof_path in NON_AUTHORITY_PROOF_PATHS:
        assert proof_path not in evidence_payload['boundary']['source_paths']
        assert proof_path not in evidence_payload['governance']['source_paths']
