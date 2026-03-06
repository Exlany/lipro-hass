from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.helpers.repo_root import repo_root

BLUEPRINT_DIR = repo_root(Path(__file__)) / "blueprints" / "automation" / "lipro"
MOTION_BLUEPRINT = BLUEPRINT_DIR / "motion_light.yaml"
OFFLINE_BLUEPRINT = BLUEPRINT_DIR / "device_offline_alert.yaml"


class _BlueprintLoader(yaml.SafeLoader):
    """YAML loader that supports Home Assistant blueprint tags."""


def _input_constructor(loader: _BlueprintLoader, node: Any) -> Any:
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


_BlueprintLoader.add_constructor("!input", _input_constructor)


def _load_blueprint(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        loaded = yaml.load(file, Loader=_BlueprintLoader)  # noqa: S506

    assert isinstance(loaded, dict)
    return loaded


@pytest.mark.parametrize("path", [MOTION_BLUEPRINT, OFFLINE_BLUEPRINT])
def test_blueprint_required_structure(path: Path) -> None:
    data = _load_blueprint(path)

    assert path.exists()
    assert "blueprint" in data
    assert "trigger" in data
    assert "action" in data
    assert "mode" in data

    blueprint_meta = data["blueprint"]
    assert isinstance(blueprint_meta, dict)
    assert blueprint_meta["domain"] == "automation"
    assert "name" in blueprint_meta
    assert isinstance(blueprint_meta.get("input"), dict)
    assert str(blueprint_meta.get("source_url", "")).endswith(path.name)


def test_motion_light_blueprint_key_fields() -> None:
    data = _load_blueprint(MOTION_BLUEPRINT)
    blueprint_inputs = data["blueprint"]["input"]

    assert {"motion_sensor", "light_target", "no_motion_wait"} <= set(blueprint_inputs)

    trigger = data["trigger"][0]
    assert trigger["platform"] == "state"
    assert trigger["entity_id"] == "motion_sensor"
    assert trigger["to"] == "on"

    services = [step["service"] for step in data["action"] if "service" in step]
    assert "light.turn_on" in services
    assert "light.turn_off" in services

    wait_trigger = data["action"][1]["wait_for_trigger"][0]
    assert wait_trigger["to"] == "off"
    assert wait_trigger["for"]["seconds"] == "no_motion_wait"


def test_device_offline_alert_blueprint_key_fields() -> None:
    data = _load_blueprint(OFFLINE_BLUEPRINT)
    blueprint_inputs = data["blueprint"]["input"]

    assert {
        "monitored_entities",
        "offline_for",
        "notify_service",
        "title",
        "message",
    } <= set(blueprint_inputs)

    trigger = data["trigger"][0]
    assert trigger["platform"] == "state"
    assert trigger["entity_id"] == "monitored_entities"
    assert trigger["to"] == "unavailable"
    assert trigger["for"]["seconds"] == "offline_for"

    notify_action = data["action"][0]
    assert notify_action["service"] == "notify_service"
    assert notify_action["data"]["title"] == "title"
    assert notify_action["data"]["message"] == "message"
