#!/usr/bin/env python3
"""Rescan release SBOMs for newly published advisories and update one issue per release."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from cra.findings import (  # noqa: E402
    Finding,
    advisory_link,
    findings_for_vulns,
    is_constraint,
    match_constraint,
    query_exact,
    query_package,
    sort_findings,
)
from cra.python_deps import is_sbom_asset, pypi_name  # noqa: E402

REPO = "deeplime-io/onecode"
LABEL = "cra-vulnerability"
FINGERPRINT_RE = re.compile(r"<!-- cra-fingerprint: ([0-9a-f]+) -->")


def _prop(component: dict[str, Any], name: str) -> str | None:
    for item in component.get("properties") or []:
        if item.get("name") == name:
            return str(item.get("value"))
    return None


def fingerprint(findings: list[Finding]) -> str:
    encoded = [list(item.key()) for item in sort_findings(findings)]
    payload = json.dumps(encoded, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def notification_body(tag: str, findings: list[Finding], logins: list[str]) -> str:
    mentions = " ".join(f"@{login}" for login in logins)
    exploited = sum(1 for item in findings if item.known_exploited)
    return (
        f"{mentions} {len(findings)} advisories match release `{tag}` "
        f"({exploited} known-exploited).\n"
    )


def render_run_summary(scanned: list[tuple[str, list[Finding]]]) -> str:
    affected = [(tag, findings) for tag, findings in scanned if findings]
    lines = [
        "## CRA vulnerability scan",
        "",
        f"Scanned {len(scanned)} releases. {len(affected)} "
        f"{'has' if len(affected) == 1 else 'have'} matching advisories.",
        "",
        "| Release | Advisories | Known exploited |",
        "| --- | ---: | ---: |",
    ]
    if not affected:
        lines.append("| none | 0 | 0 |")
    for tag, findings in affected:
        exploited = sum(1 for item in findings if item.known_exploited)
        lines.append(f"| {tag} | {len(findings)} | {exploited} |")
    lines.append("")
    return "\n".join(lines) + "\n"


def publish_run_summary(text: str) -> None:
    print(text, end="")
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(text)


def _notify_logins() -> list[str]:
    logins: list[str] = []
    for item in os.environ.get("CRA_NOTIFY", "").split(","):
        login = item.strip().lstrip("@")
        if re.fullmatch(r"[A-Za-z0-9-]+", login):
            logins.append(login)
    return logins


def render_body(findings: list[Finding]) -> str:
    ordered = sort_findings(findings)
    marker = f"<!-- cra-fingerprint: {fingerprint(ordered)} -->"
    if not ordered:
        return f"{marker}\n\nNo advisories currently match this release SBOM.\n"
    exploited = sum(1 for item in ordered if item.known_exploited)
    lines = [
        marker,
        "",
        f"Known-exploited advisories affecting this release: {exploited}",
        "",
        "A match means the advisory's affected range intersects the SBOM entry.",
        "It is not an exploitability decision.",
        "",
        "| Advisory | Package | Version or constraint | Severity | Known exploited | Ecosystem |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in ordered:
        summary = item.summary[:120].replace("|", "/")
        lines.append(
            f"| {advisory_link(item.vuln_id)} | {item.package} | `{item.version}` | "
            f"{item.severity} | {'yes' if item.known_exploited else 'no'} | {item.ecosystem} |",
        )
        if summary:
            lines.append(f"|  |  | {summary} |  |  |  |")
    lines.append("")
    body = "\n".join(lines) + "\n"
    if len(body) > 60000:
        body = body[:60000] + "\n\nTruncated.\n"
    return body


def _gh(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["gh", *args], check=check, capture_output=True, text=True)


def list_releases() -> list[dict[str, Any]]:
    result = _gh("api", f"repos/{REPO}/releases?per_page=100")
    releases = json.loads(result.stdout)
    return [release for release in releases if not release.get("draft")]


def release_has_sbom(release: dict[str, Any]) -> bool:
    return any(is_sbom_asset(asset.get("name") or "") for asset in release.get("assets") or [])


def _python_findings(component: dict[str, Any]) -> list[Finding]:
    if component.get("name") == "python":
        return []
    constraint = _prop(component, "deeplime:version-constraint") or str(
        component.get("version") or "",
    )
    package = pypi_name(str(component.get("name") or ""))
    if is_constraint(constraint):
        return match_constraint(package, constraint, "PyPI", query_package(package, "PyPI"))
    payload = query_exact(package, "PyPI", constraint)
    return findings_for_vulns(package, constraint, "PyPI", payload.get("vulns") or [])


def scan_product(document: dict[str, Any]) -> list[Finding]:
    components = list(document.get("components") or [])
    root = (document.get("metadata") or {}).get("component")
    if root:
        components.append(root)
    findings: list[Finding] = []
    for component in components:
        if _prop(component, "deeplime:ecosystem") != "python":
            continue
        findings.extend(_python_findings(component))
    return sort_findings(findings)


def _ensure_label() -> None:
    _gh(
        "label",
        "create",
        LABEL,
        "--repo",
        REPO,
        "--color",
        "B60205",
        "--description",
        "CRA vulnerability monitor",
        check=False,
    )


def _issues() -> list[dict[str, Any]]:
    result = _gh(
        "issue",
        "list",
        "--repo",
        REPO,
        "--state",
        "all",
        "--limit",
        "200",
        "--label",
        LABEL,
        "--json",
        "number,title,state,body",
    )
    return json.loads(result.stdout or "[]")


def _issue_with_title(issues: list[dict[str, Any]], title: str) -> dict[str, Any] | None:
    for issue in issues:
        if issue.get("title") == title:
            return issue
    return None


def _write_issue(
    title: str,
    body: str,
    existing: dict[str, Any] | None,
    reopen: bool,
    close: bool,
) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
        handle.write(body)
        body_path = handle.name
    try:
        if existing is None:
            created = _gh(
                "issue",
                "create",
                "--repo",
                REPO,
                "--title",
                title,
                "--label",
                LABEL,
                "--body-file",
                body_path,
            )
            match = re.search(r"/issues/(\d+)", created.stdout)
            if match is None:
                raise RuntimeError(f"could not read the new issue number from {created.stdout!r}")
            return match.group(1)
        number = str(existing["number"])
        _gh("issue", "edit", number, "--repo", REPO, "--body-file", body_path)
        state = str(existing.get("state") or "").upper()
        if reopen and state == "CLOSED":
            _gh("issue", "reopen", number, "--repo", REPO)
        if close and state == "OPEN":
            _gh("issue", "close", number, "--repo", REPO, "--reason", "completed")
        return number
    finally:
        Path(body_path).unlink(missing_ok=True)


def _comment(number: str, body: str) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as handle:
        handle.write(body)
        body_path = handle.name
    try:
        _gh("issue", "comment", number, "--repo", REPO, "--body-file", body_path)
    finally:
        Path(body_path).unlink(missing_ok=True)


def _download(tag: str, name: str, dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "gh",
            "release",
            "download",
            tag,
            "--repo",
            REPO,
            "--pattern",
            name,
            "--dir",
            str(dest),
            "--clobber",
        ],
        check=True,
    )
    return dest / name


def sync_release(release: dict[str, Any], issues: list[dict[str, Any]]) -> list[Finding]:
    tag = release["tag_name"]
    names = [
        asset["name"]
        for asset in release.get("assets") or []
        if is_sbom_asset(asset.get("name") or "")
    ]
    if not names:
        return []
    findings: list[Finding] = []
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        for name in names:
            path = _download(tag, name, folder)
            findings.extend(scan_product(json.loads(path.read_text())))
    findings = sort_findings(findings)
    title = f"CRA vulnerabilities in {tag}"
    body = render_body(findings)
    marker = fingerprint(findings)
    existing = _issue_with_title(issues, title)
    match = FINGERPRINT_RE.search((existing or {}).get("body") or "") if existing else None
    if match and match.group(1) == marker:
        return findings
    if not findings and existing is None:
        return findings
    number = _write_issue(title, body, existing, reopen=bool(findings), close=not findings)
    logins = _notify_logins()
    if findings and logins:
        _comment(number, notification_body(tag, findings, logins))
    return findings


def main() -> None:
    _ensure_label()
    issues = _issues()
    scanned: list[tuple[str, list[Finding]]] = []
    for release in list_releases():
        scanned.append((release["tag_name"], sync_release(release, issues)))
        issues = _issues()
    publish_run_summary(render_run_summary(scanned))


if __name__ == "__main__":
    main()
