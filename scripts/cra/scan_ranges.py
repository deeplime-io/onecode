#!/usr/bin/env python3
"""Compare direct pyproject.toml ranges with OSV. Never fails the pull request for findings."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cra.findings import advisory_link, match_constraint, query_package, sort_findings  # noqa: E402
from cra.python_deps import pypi_name, runtime_dependencies  # noqa: E402


def render(findings) -> str:
    if not findings:
        return "No OSV advisories intersect the direct dependency ranges in pyproject.toml.\n"
    lines = [
        "## Dependency range advisories",
        "",
        "These are presence matches against declared ranges, not exploitability.",
        "",
        "| Advisory | Package | Constraint | Severity | Known exploited |",
        "| --- | --- | --- | --- | --- |",
    ]
    for finding in findings:
        lines.append(
            f"| {advisory_link(finding.vuln_id)} | {finding.package} | `{finding.version}` | "
            f"{finding.severity} | "
            f"{'yes' if finding.known_exploited else 'no'} |",
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def scan(pyproject: Path) -> str:
    _name, _version, dependencies = runtime_dependencies(pyproject)
    findings = []
    for dep_name, constraint in dependencies:
        if dep_name == "python":
            continue
        package = pypi_name(dep_name)
        payload = query_package(package, "PyPI")
        findings.extend(match_constraint(package, constraint, "PyPI", payload))
    return render(sort_findings(findings))


def main() -> None:
    pyproject = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("pyproject.toml")
    try:
        report = scan(pyproject)
    except Exception as exc:  # noqa: BLE001 — a scanner bug should be visible, findings must not fail CI
        report = f"Dependency range scan failed: {exc}\n"
        print(report, file=sys.stderr)
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary, "a", encoding="utf-8") as handle:
                handle.write(report)
        raise
    print(report)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(report)


if __name__ == "__main__":
    main()
