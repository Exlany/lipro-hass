"""Phase 119 MQTT boundary one-way dependency guards."""

from __future__ import annotations

from pathlib import Path

from tests.helpers.repo_root import repo_root

_ROOT = repo_root(Path(__file__))
_PRODUCTION_ROOT = _ROOT / "custom_components" / "lipro" / "core"


def test_phase119_boundary_owns_mqtt_support_truth_without_reverse_imports() -> None:
    decoder_text = (
        _PRODUCTION_ROOT / "protocol" / "boundary" / "mqtt_decoder.py"
    ).read_text(encoding="utf-8")
    payload_text = (_PRODUCTION_ROOT / "mqtt" / "payload.py").read_text(encoding="utf-8")
    topics_text = (_PRODUCTION_ROOT / "mqtt" / "topics.py").read_text(encoding="utf-8")
    processor_text = (
        _PRODUCTION_ROOT / "mqtt" / "message_processor.py"
    ).read_text(encoding="utf-8")

    assert "from ...mqtt.payload import _MAX_MQTT_PAYLOAD_BYTES" not in decoder_text
    assert "from ...mqtt.topics import normalize_mqtt_biz_id" not in decoder_text
    assert "_MAX_MQTT_PAYLOAD_BYTES = 64 * 1024" in decoder_text
    assert "def normalize_mqtt_biz_id(value: object) -> str | None:" in decoder_text

    assert "from ..protocol.boundary.mqtt_decoder import (" in payload_text
    assert "import_module(" not in payload_text
    assert "decode_mqtt_message_envelope_payload(" in payload_text
    assert "decode_mqtt_properties_payload(" in payload_text

    assert "from ..protocol.boundary.mqtt_decoder import (" in topics_text
    assert "import_module(" not in topics_text
    assert "decode_mqtt_topic_payload(" in topics_text
    assert 'topic.split("/")' not in topics_text

    assert "from ..protocol.boundary.mqtt_decoder import decode_mqtt_topic_payload" in processor_text
    assert "import_module(" not in processor_text
    assert "decode_mqtt_topic_payload(" in processor_text
