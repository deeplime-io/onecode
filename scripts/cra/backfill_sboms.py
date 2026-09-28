#!/usr/bin/env python3
"""Attach CycloneDX SBOMs to published GitHub releases that do not have one.

Only existing releases are updated. Tags without a GitHub release are left alone.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cra.make_release_sbom import build  # noqa: E402
from cra.monitor_releases import REPO, _gh, list_releases, release_has_sbom  # noqa: E402


def pyproject_at_tag(tag: str, dest: Path) -> None:
    result = subprocess.run(
        ["git", "show", f"{tag}:pyproject.toml"],
        check=True,
        capture_output=True,
    )
    dest.write_bytes(result.stdout)


def backfill() -> list[str]:
    """Upload a missing SBOM for each published release. Return tags that failed."""
    failed: list[str] = []
    for release in list_releases():
        tag = release["tag_name"]
        if release_has_sbom(release):
            print(f"{tag}: SBOM already attached")
            continue
        try:
            with tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                pyproject = folder / "pyproject.toml"
                pyproject_at_tag(tag, pyproject)
                path = build(pyproject, folder)
                _gh(
                    "release",
                    "upload",
                    tag,
                    str(path),
                    "--clobber",
                    "--repo",
                    REPO,
                )
                print(f"{tag}: uploaded {path.name}")
        except Exception as exc:  # noqa: BLE001 — keep going so one old tag does not stop the rest
            failed.append(f"{tag}: {exc}")
            print(f"{tag}: failed: {exc}", file=sys.stderr)
    return failed


def main() -> None:
    failed = backfill()
    if failed:
        raise SystemExit(f"{len(failed)} release(s) could not be updated")


if __name__ == "__main__":
    main()
