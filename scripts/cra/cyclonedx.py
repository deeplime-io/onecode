"""Minimal CycloneDX 1.6 JSON documents."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPEC_VERSION = "1.6"
TOOL_NAME = "deeplime-cra-sbom"
TOOL_VERSION = "1"


def new_bom(
    root: dict[str, Any],
    components: list[dict[str, Any]],
    dependencies: list[dict[str, Any]],
    extra_tools: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    tools = [
        {
            "type": "application",
            "name": TOOL_NAME,
            "version": TOOL_VERSION,
        },
        *(extra_tools or []),
    ]
    return {
        "$schema": f"http://cyclonedx.org/schema/bom-{SPEC_VERSION}.schema.json",
        "bomFormat": "CycloneDX",
        "specVersion": SPEC_VERSION,
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tools": {"components": tools},
            "component": root,
        },
        "components": components,
        "dependencies": dependencies,
    }


def write_bom(document: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2) + "\n")


def add_property(component: dict[str, Any], name: str, value: str) -> None:
    properties = component.setdefault("properties", [])
    properties.append({"name": name, "value": value})
