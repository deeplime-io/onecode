"""Match dependency constraints and exact versions to OSV advisories."""

from __future__ import annotations

import json
import math
import re
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable

from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.version import InvalidVersion, Version

OSV_QUERY = "https://api.osv.dev/v1/query"
OSV_QUERYBATCH = "https://api.osv.dev/v1/querybatch"
OSV_VULN = "https://api.osv.dev/v1/vulns"
SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "moderate": 2, "low": 3, "unknown": 4}
_CVSS_V3_AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
_CVSS_V3_AC = {"L": 0.77, "H": 0.44}
_CVSS_V3_UI = {"N": 0.85, "R": 0.62}
_CVSS_V3_CIA = {"H": 0.56, "L": 0.22, "N": 0.0}
_CVSS_V3_PR = {
    "U": {"N": 0.85, "L": 0.62, "H": 0.27},
    "C": {"N": 0.85, "L": 0.68, "H": 0.5},
}


@dataclass(frozen=True)
class Finding:
    vuln_id: str
    package: str
    version: str
    summary: str
    severity: str
    known_exploited: bool
    ecosystem: str

    def key(self) -> tuple[str, str, str]:
        return (self.vuln_id, self.package, self.version)


def is_constraint(version: str) -> bool:
    return bool(re.search(r"[<>=!~^*]|\s|,", version))


def _normalize(constraint: str) -> str:
    return ",".join("".join(part.split()) for part in constraint.split(",") if part.strip())


def _bounds(constraint: str) -> tuple[Version | None, bool, Version | None, bool] | None:
    """Return an inclusive/exclusive interval, or None when the constraint matches nothing."""
    normalized = _normalize(constraint)
    if not normalized or normalized == "*":
        return None, True, None, False
    try:
        spec = SpecifierSet(normalized)
    except (InvalidSpecifier, InvalidVersion):
        return None
    equals = [Version(item.version) for item in spec if item.operator == "=="]
    if equals:
        point = equals[0]
        rest = ",".join(str(item) for item in spec if item.operator != "==")
        if rest and not SpecifierSet(rest).contains(str(point), prereleases=True):
            return None
        return point, True, point, True

    lower: Version | None = None
    lower_inclusive = True
    upper: Version | None = None
    upper_inclusive = False
    for item in spec:
        if item.operator == "!=":
            continue
        version = Version(item.version)
        if item.operator == ">=":
            if lower is None or version > lower:
                lower, lower_inclusive = version, True
        elif item.operator == ">":
            if lower is None or version > lower or (version == lower and lower_inclusive):
                lower, lower_inclusive = version, False
        elif item.operator == "<":
            if upper is None or version < upper:
                upper, upper_inclusive = version, False
        elif item.operator == "<=":
            if upper is None or version < upper or (version == upper and not upper_inclusive):
                upper, upper_inclusive = version, True
        elif item.operator == "~=":
            if lower is None or version > lower:
                lower, lower_inclusive = version, True
            release = version.release
            if len(release) >= 2:
                prefix = list(release[:-1])
                prefix[-1] += 1
                cap = Version(".".join(str(part) for part in prefix))
                if upper is None or cap < upper:
                    upper, upper_inclusive = cap, False
    if lower is not None and upper is not None and (
        lower > upper or (lower == upper and not (lower_inclusive and upper_inclusive))
    ):
        return None
    return lower, lower_inclusive, upper, upper_inclusive


def _parse_version(raw: str) -> Version | None:
    if raw in {"0", "0.0.0"}:
        return Version("0")
    try:
        return Version(raw)
    except InvalidVersion:
        return None


def _ends_before(
    end: Version | None,
    end_inclusive: bool,
    start: Version | None,
    start_inclusive: bool,
) -> bool:
    if end is None or start is None:
        return False
    if end < start:
        return True
    if end > start:
        return False
    return not (end_inclusive and start_inclusive)


def _intervals_overlap(
    left: tuple[Version | None, bool, Version | None, bool],
    right: tuple[Version | None, bool, Version | None, bool],
) -> bool:
    left_start, left_start_inc, left_end, left_end_inc = left
    right_start, right_start_inc, right_end, right_end_inc = right
    if _ends_before(left_end, left_end_inc, right_start, right_start_inc):
        return False
    if _ends_before(right_end, right_end_inc, left_start, left_start_inc):
        return False
    return True


def _osv_intervals(
    ranges: list[dict[str, Any]],
) -> list[tuple[Version | None, bool, Version | None, bool]]:
    intervals = []
    for item in ranges:
        if item.get("type") == "GIT":
            continue
        start: Version | None = None
        started = False
        for event in item.get("events") or []:
            if "introduced" in event:
                start = _parse_version(str(event["introduced"]))
                started = start is not None or str(event["introduced"]) in {"0", "0.0.0"}
                if str(event["introduced"]) in {"0", "0.0.0"}:
                    start = Version("0")
            elif started and "fixed" in event:
                fixed = _parse_version(str(event["fixed"]))
                if fixed is not None:
                    intervals.append((start, True, fixed, False))
                started = False
            elif started and "last_affected" in event:
                last = _parse_version(str(event["last_affected"]))
                if last is not None:
                    intervals.append((start, True, last, True))
                started = False
        if started:
            intervals.append((start, True, None, False))
    return intervals


def _affected_package(entry: dict[str, Any], package: str, ecosystem: str) -> bool:
    info = entry.get("package") or {}
    if ecosystem and info.get("ecosystem") and info["ecosystem"].lower() != ecosystem.lower():
        return False
    return str(info.get("name", "")).lower().replace("_", "-") == package.lower().replace("_", "-")


def constraint_overlaps(
    constraint: str,
    vuln: dict[str, Any],
    package: str,
    ecosystem: str,
) -> bool:
    open_ended = constraint.strip() in {"", "*"}
    bounds = _bounds(constraint)
    if bounds is None and not open_ended:
        return False
    interval = bounds if bounds is not None else (None, True, None, False)
    for entry in vuln.get("affected") or []:
        if not _affected_package(entry, package, ecosystem):
            continue
        versions = entry.get("versions") or []
        if versions and bounds is not None:
            try:
                spec = SpecifierSet(_normalize(constraint))
            except (InvalidSpecifier, InvalidVersion):
                spec = None
            for version in versions if spec is not None else []:
                try:
                    if spec.contains(str(version), prereleases=True):
                        return True
                except InvalidVersion:
                    continue
        ranges = entry.get("ranges") or []
        if not ranges and not versions:
            return True
        for osv_interval in _osv_intervals(ranges):
            if _intervals_overlap(interval, osv_interval):
                return True
    return False


def known_exploited(vuln: dict[str, Any]) -> bool:
    specific = vuln.get("database_specific") or {}
    if isinstance(specific, dict) and (
        specific.get("known_exploited") or specific.get("cisa_known_exploited")
    ):
        return True
    for ref in vuln.get("references") or []:
        url = str(ref.get("url") or "").lower()
        if "known_exploited" in url or ("cisa.gov" in url and "kev" in url):
            return True
    return False


def advisory_url(vuln_id: str) -> str:
    if vuln_id.startswith("GHSA-"):
        return f"https://github.com/advisories/{vuln_id}"
    if vuln_id.startswith("CVE-"):
        return f"https://nvd.nist.gov/vuln/detail/{vuln_id}"
    return f"https://osv.dev/vulnerability/{vuln_id}"


def advisory_link(vuln_id: str) -> str:
    return f"[{vuln_id}]({advisory_url(vuln_id)})"


def _cvss_roundup(score: float) -> float:
    """CVSS v3 Roundup: smallest one-decimal value greater than or equal to score."""
    scaled = round(score * 100000)
    if scaled % 10000 == 0:
        return scaled / 100000.0
    return (math.floor(scaled / 10000) + 1) / 10.0


def _cvss_v3_severity(vector: str) -> str | None:
    if not vector.startswith(("CVSS:3.0/", "CVSS:3.1/")):
        return None
    metrics = {}
    for part in vector.split("/")[1:]:
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        metrics[key] = value
    try:
        scope = metrics["S"]
        iss = 1 - (
            (1 - _CVSS_V3_CIA[metrics["C"]])
            * (1 - _CVSS_V3_CIA[metrics["I"]])
            * (1 - _CVSS_V3_CIA[metrics["A"]])
        )
        exploitability = (
            8.22
            * _CVSS_V3_AV[metrics["AV"]]
            * _CVSS_V3_AC[metrics["AC"]]
            * _CVSS_V3_PR[scope][metrics["PR"]]
            * _CVSS_V3_UI[metrics["UI"]]
        )
    except KeyError:
        return None
    if scope == "U":
        impact = 6.42 * iss
        raw = impact + exploitability if impact > 0 else 0
    elif scope == "C":
        impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15
        raw = 1.08 * (impact + exploitability) if impact > 0 else 0
    else:
        return None
    score = _cvss_roundup(min(raw, 10))
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "moderate"
    if score > 0:
        return "low"
    return "low"


def osv_severity(vuln: dict[str, Any]) -> str:
    specific = vuln.get("database_specific") or {}
    if isinstance(specific, dict) and specific.get("severity"):
        return str(specific["severity"]).lower()
    for item in vuln.get("severity") or []:
        if not isinstance(item, dict):
            continue
        mapped = _cvss_v3_severity(str(item.get("score") or ""))
        if mapped:
            return mapped
    return "unknown"


def _fetch_vuln(vuln_id: str) -> dict[str, Any] | None:
    request = urllib.request.Request(
        f"{OSV_VULN}/{vuln_id}",
        headers={"User-Agent": "onecode-cra"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except (OSError, json.JSONDecodeError, TimeoutError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _severity_from_aliases(vuln: dict[str, Any], known: dict[str, str]) -> str:
    for alias in vuln.get("aliases") or []:
        alias_id = str(alias)
        inherited = known.get(alias_id, "unknown")
        if inherited != "unknown":
            return inherited
        fetched = _fetch_vuln(alias_id)
        if fetched is None:
            continue
        inherited = osv_severity(fetched)
        if inherited == "unknown":
            continue
        known[alias_id] = inherited
        return inherited
    return "unknown"


def _post(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def query_package(name: str, ecosystem: str) -> dict[str, Any]:
    return _post(OSV_QUERY, {"package": {"name": name, "ecosystem": ecosystem}})


def query_exact(name: str, ecosystem: str, version: str) -> dict[str, Any]:
    return _post(
        OSV_QUERY,
        {"package": {"name": name, "ecosystem": ecosystem}, "version": version},
    )


def query_batch(queries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for start in range(0, len(queries), 500):
        chunk = queries[start : start + 500]
        payload = _post(OSV_QUERYBATCH, {"queries": chunk})
        results.extend(payload.get("results") or [])
    return results


def findings_for_vulns(
    package: str,
    version: str,
    ecosystem: str,
    vulns: list[dict[str, Any]],
    overlaps: Callable[[dict[str, Any]], bool] | None = None,
) -> list[Finding]:
    found: list[Finding] = []
    seen: set[tuple[str, str, str]] = set()
    known_severity = {
        str(vuln.get("id")): osv_severity(vuln)
        for vuln in vulns
        if vuln.get("id")
    }
    for vuln in vulns:
        if overlaps is not None and not overlaps(vuln):
            continue
        vuln_id = str(vuln.get("id"))
        severity = known_severity.get(vuln_id) or osv_severity(vuln)
        if severity == "unknown":
            severity = _severity_from_aliases(vuln, known_severity)
            known_severity[vuln_id] = severity
        finding = Finding(
            vuln_id=vuln_id,
            package=package,
            version=version,
            summary=str(vuln.get("summary") or vuln.get("details") or "").replace("\n", " "),
            severity=severity,
            known_exploited=known_exploited(vuln),
            ecosystem=ecosystem,
        )
        if finding.key() not in seen:
            seen.add(finding.key())
            found.append(finding)
    return found


def match_constraint(
    package: str,
    constraint: str,
    ecosystem: str,
    query: dict[str, Any],
) -> list[Finding]:
    vulns = query.get("vulns") or []
    return findings_for_vulns(
        package,
        constraint,
        ecosystem,
        vulns,
        overlaps=lambda vuln: constraint_overlaps(constraint, vuln, package, ecosystem),
    )


def sort_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(
        findings,
        key=lambda item: (
            not item.known_exploited,
            SEVERITY_RANK.get(item.severity.lower(), 4),
            item.vuln_id,
            item.package,
            item.version,
        ),
    )
