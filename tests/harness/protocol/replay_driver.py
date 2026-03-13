"""Deterministic replay driver for protocol fixtures and canonical assertions."""

from __future__ import annotations

from typing import cast

from custom_components.lipro.core.protocol import LiproProtocolFacade
from custom_components.lipro.core.protocol.boundary import (
    decode_mqtt_properties_payload,
)
from tests.harness.protocol.replay_loader import load_replay_fixture
from tests.harness.protocol.replay_models import (
    LoadedReplayFixture,
    ReplayExecutionResult,
    ReplayManifest,
)


class ProtocolReplayDriver:
    """Run replay scenarios through the formal protocol public path only."""

    def __init__(
        self,
        *,
        protocol_factory: type[LiproProtocolFacade] = LiproProtocolFacade,
    ) -> None:
        self._protocol_factory = protocol_factory

    def run_manifest(self, manifest: ReplayManifest) -> ReplayExecutionResult:
        """Load one manifest and run it through the formal path."""
        return self.run_fixture(load_replay_fixture(manifest))

    def run_fixture(self, fixture: LoadedReplayFixture) -> ReplayExecutionResult:
        """Execute one loaded replay fixture deterministically."""
        manifest = fixture.manifest
        started_at = manifest.controls.clock_baseline
        finished_at = manifest.controls.clock_baseline
        try:
            if manifest.operation == "protocol.contracts.normalize_mqtt_config":
                protocol = self._protocol_factory(
                    "replay-phone-id",
                    entry_id=f"replay:{manifest.scenario_id}",
                )
                canonical = protocol.contracts.normalize_mqtt_config(
                    fixture.authority_payload
                )
                return ReplayExecutionResult(
                    manifest=manifest,
                    public_path="LiproProtocolFacade.contracts.normalize_mqtt_config",
                    started_at=started_at,
                    finished_at=finished_at,
                    canonical=canonical,
                    drift_flags=(),
                    error_category=None,
                )

            if manifest.operation == "protocol.boundary.decode_mqtt_properties":
                metadata = fixture.authority_metadata
                payload = metadata.get("payload")
                result = decode_mqtt_properties_payload(payload)
                return ReplayExecutionResult(
                    manifest=manifest,
                    public_path="core.protocol.boundary.decode_mqtt_properties_payload",
                    started_at=started_at,
                    finished_at=finished_at,
                    canonical=result.canonical,
                    drift_flags=(),
                    error_category=None,
                    fingerprint=result.fingerprint,
                )

            msg = f"Unsupported replay operation: {manifest.operation}"
            raise ValueError(msg)
        except Exception as err:  # noqa: BLE001
            return ReplayExecutionResult(
                manifest=manifest,
                public_path=manifest.operation,
                started_at=started_at,
                finished_at=finished_at,
                canonical=None,
                drift_flags=("driver_error",),
                error_category=type(err).__name__,
            )

    @staticmethod
    def authority_canonical(fixture: LoadedReplayFixture) -> object | None:
        """Return the canonical contract recorded on one authority fixture, if any."""
        return fixture.authority_metadata.get("canonical")

    @staticmethod
    def authority_fingerprint(fixture: LoadedReplayFixture) -> str | None:
        """Return the authority fingerprint recorded on one fixture, if any."""
        fingerprint = fixture.authority_metadata.get("fingerprint")
        return cast(str, fingerprint) if isinstance(fingerprint, str) else None
