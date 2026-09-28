"""Python SBOM from Poetry ranges in pyproject.toml.

Direct runtime ranges only. Optional docs and test extras are omitted.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from cra.cyclonedx import add_property, new_bom

DECLARED_SCOPE = "installed-alongside-wheel"


def pypi_name(name: str) -> str:
    return name.lower().replace("_", "-")


def sbom_filename(version: str) -> str:
    return f"onecode-{version}.cdx.json"


def is_sbom_asset(name: str) -> bool:
    return name.startswith("onecode-") and name.endswith(".cdx.json")


def runtime_dependencies(pyproject: Path) -> tuple[str, str, list[tuple[str, str]]]:
    """Return package name, version, and direct runtime (name, constraint) pairs."""
    data = tomllib.loads(pyproject.read_text())
    poetry = data["tool"]["poetry"]
    dependencies: list[tuple[str, str]] = []
    for name, spec in poetry["dependencies"].items():
        if isinstance(spec, str):
            dependencies.append((name, spec))
            continue
        if isinstance(spec, dict) and not spec.get("optional") and "version" in spec:
            dependencies.append((name, str(spec["version"])))
    return poetry["name"], poetry["version"], dependencies


def python_sbom(pyproject: Path) -> dict[str, Any]:
    name, version, dependencies = runtime_dependencies(pyproject)
    root_ref = f"pkg:pypi/{pypi_name(name)}@{version}"
    root: dict[str, Any] = {
        "bom-ref": root_ref,
        "type": "library",
        "name": name,
        "version": version,
        "purl": root_ref,
        "supplier": {"name": "DeepLime"},
        "licenses": [{"license": {"id": "MIT"}}],
    }
    components: list[dict[str, Any]] = []
    depends_on: list[str] = []
    for dep_name, constraint in dependencies:
        if dep_name == "python":
            ref = "pkg:generic/python"
            component: dict[str, Any] = {
                "bom-ref": ref,
                "type": "platform",
                "name": "python",
                "version": constraint,
                "purl": ref,
            }
        else:
            ref = f"pkg:pypi/{pypi_name(dep_name)}"
            component = {
                "bom-ref": ref,
                "type": "library",
                "name": dep_name,
                "version": constraint,
                "purl": ref,
            }
        add_property(component, "deeplime:ecosystem", "python")
        add_property(component, "deeplime:install-scope", DECLARED_SCOPE)
        add_property(component, "deeplime:version-constraint", constraint)
        components.append(component)
        depends_on.append(ref)
    return new_bom(
        root,
        components,
        [{"ref": root_ref, "dependsOn": depends_on}],
    )
