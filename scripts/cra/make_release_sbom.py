#!/usr/bin/env python3
"""Build a CycloneDX 1.6 SBOM for an OneCode release.

Python dependencies keep the version ranges declared in pyproject.toml.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cra.cyclonedx import write_bom  # noqa: E402
from cra.python_deps import python_sbom, sbom_filename  # noqa: E402


def build(pyproject: Path, out_dir: Path) -> Path:
    document = python_sbom(pyproject)
    version = document["metadata"]["component"]["version"]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / sbom_filename(version)
    write_bom(document, path)
    return path


def main() -> None:
    if sys.version_info < (3, 11):
        raise SystemExit("make_release_sbom.py requires Python 3.11 or newer")
    parser = argparse.ArgumentParser(
        description="Write a CycloneDX 1.6 SBOM for an OneCode release",
    )
    parser.add_argument("--pyproject", default="pyproject.toml")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    print(build(Path(args.pyproject), Path(args.out_dir)))


if __name__ == "__main__":
    main()
