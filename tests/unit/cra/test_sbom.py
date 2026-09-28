import tempfile
import unittest
from pathlib import Path

from cra.cyclonedx import SPEC_VERSION
from cra.findings import (
    Finding,
    advisory_link,
    constraint_overlaps,
    findings_for_vulns,
    osv_severity,
)
from cra.make_release_sbom import build
from cra.monitor_releases import (
    fingerprint,
    notification_body,
    release_has_sbom,
    render_body,
    render_run_summary,
)
from cra.python_deps import is_sbom_asset, python_sbom, runtime_dependencies


def _vuln(ranges, versions=None, name="numpy"):
    entry = {"package": {"ecosystem": "PyPI", "name": name}}
    if ranges is not None:
        entry["ranges"] = [{"type": "ECOSYSTEM", "events": ranges}]
    if versions is not None:
        entry["versions"] = versions
    return {"id": "GHSA-test", "affected": [entry]}


class RangeOverlapTest(unittest.TestCase):
    def test_lower_bound_inside_fixed_range(self):
        vuln = _vuln([{"introduced": "0"}, {"fixed": "1.26"}])
        self.assertTrue(constraint_overlaps(">= 1.25, < 2", vuln, "numpy", "PyPI"))

    def test_lower_bound_at_fix_is_clear(self):
        vuln = _vuln([{"introduced": "0"}, {"fixed": "1.26"}])
        self.assertFalse(constraint_overlaps(">= 1.26, < 2", vuln, "numpy", "PyPI"))

    def test_range_above_fix_is_clear(self):
        vuln = _vuln([{"introduced": "0"}, {"fixed": "1.5"}])
        self.assertFalse(constraint_overlaps(">= 2.3.3, < 3", vuln, "numpy", "PyPI"))

    def test_explicit_version_list(self):
        vuln = _vuln(None, versions=["1.2.3"])
        self.assertTrue(constraint_overlaps("==1.2.3", vuln, "numpy", "PyPI"))

    def test_last_affected_is_inclusive(self):
        vuln = _vuln([{"introduced": "0"}, {"last_affected": "1.5"}])
        self.assertTrue(constraint_overlaps(">= 1.5, < 2", vuln, "numpy", "PyPI"))

    def test_other_package_is_ignored(self):
        vuln = _vuln([{"introduced": "0"}, {"fixed": "9"}])
        self.assertFalse(constraint_overlaps(">= 1, < 2", vuln, "pandas", "PyPI"))


class AdvisoryReportTest(unittest.TestCase):
    def test_pysec_links_to_osv_and_ghsa_links_to_github(self):
        self.assertEqual(
            advisory_link("PYSEC-2024-161"),
            "[PYSEC-2024-161](https://osv.dev/vulnerability/PYSEC-2024-161)",
        )
        self.assertIn(
            "https://github.com/advisories/GHSA-5wvp-7f3h-6wmm",
            advisory_link("GHSA-5wvp-7f3h-6wmm"),
        )

    def test_cvss_vector_supplies_severity_when_database_specific_is_missing(self):
        critical = {
            "severity": [
                {"type": "CVSS_V3", "score": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"},
            ],
        }
        moderate = {
            "severity": [
                {"type": "CVSS_V3", "score": "CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N"},
            ],
        }
        self.assertEqual(osv_severity(critical), "critical")
        self.assertEqual(osv_severity(moderate), "moderate")

    def test_database_specific_severity_wins(self):
        vuln = {
            "database_specific": {"severity": "HIGH"},
            "severity": [
                {"type": "CVSS_V3", "score": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"},
            ],
        }
        self.assertEqual(osv_severity(vuln), "high")

    def test_pysec_inherits_alias_severity_without_a_lookup(self):
        ghsa = {
            "id": "GHSA-aaaa-bbbb-cccc",
            "aliases": ["PYSEC-2026-1"],
            "database_specific": {"severity": "HIGH"},
            "summary": "example",
        }
        pysec = {"id": "PYSEC-2026-1", "aliases": ["GHSA-aaaa-bbbb-cccc"]}

        def fail_fetch(_vuln_id: str):
            raise AssertionError("alias lookup")

        import cra.findings as findings

        original = findings._fetch_vuln
        findings._fetch_vuln = fail_fetch
        try:
            found = findings_for_vulns("pyarrow", ">= 12", "PyPI", [ghsa, pysec])
        finally:
            findings._fetch_vuln = original
        by_id = {item.vuln_id: item.severity for item in found}
        self.assertEqual(by_id["PYSEC-2026-1"], "high")


class PythonSbomTest(unittest.TestCase):
    def test_ranges_are_kept_and_optional_deps_are_omitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "pyproject.toml"
            path.write_text(
                """
[tool.poetry]
name = "onecode"
version = "1.2.2"

[tool.poetry.dependencies]
python = ">=3.11, <3.15"
pandas = ">=2.3,<4"
datatest = { version = ">=0.11.1,<1", optional = true }
""".strip(),
            )
            _name, _version, deps = runtime_dependencies(path)
            self.assertEqual(
                deps,
                [("python", ">=3.11, <3.15"), ("pandas", ">=2.3,<4")],
            )
            document = python_sbom(path)
            self.assertEqual(document["specVersion"], SPEC_VERSION)
            root = document["metadata"]["component"]
            self.assertEqual(root["licenses"], [{"license": {"id": "MIT"}}])
            self.assertEqual(root["supplier"], {"name": "DeepLime"})
            by_name = {component["name"]: component for component in document["components"]}
            self.assertEqual(by_name["pandas"]["version"], ">=2.3,<4")
            self.assertEqual(by_name["pandas"]["purl"], "pkg:pypi/pandas")
            self.assertNotIn("datatest", by_name)
            written = build(path, Path(tmp))
            self.assertEqual(written.name, "onecode-1.2.2.cdx.json")

    def test_repository_pyproject_keeps_runtime_deps_only(self):
        root = Path(__file__).resolve().parents[3]
        _name, version, deps = runtime_dependencies(root / "pyproject.toml")
        names = {name for name, _constraint in deps}
        self.assertIn("pandas", names)
        self.assertIn("pyarrow", names)
        self.assertNotIn("pytest", names)
        self.assertNotIn("mkdocs", names)
        self.assertEqual(version, "2.0.0rc3")


class ReleaseAssetTest(unittest.TestCase):
    def test_sbom_asset_name(self):
        self.assertTrue(is_sbom_asset("onecode-1.2.2.cdx.json"))
        self.assertFalse(is_sbom_asset("onecode-1.2.2.whl"))

    def test_release_without_sbom_is_selected_for_backfill(self):
        release = {"assets": [{"name": "onecode-1.2.2.whl"}]}
        self.assertFalse(release_has_sbom(release))
        release["assets"].append({"name": "onecode-1.2.2.cdx.json"})
        self.assertTrue(release_has_sbom(release))


class IssueBodyTest(unittest.TestCase):
    def test_fingerprint_is_stable(self):
        finding = Finding("GHSA-1", "pandas", ">=2.3,<4", "summary", "high", False, "PyPI")
        body = render_body([finding])
        self.assertIn(fingerprint([finding]), body)
        self.assertTrue(body.startswith("<!-- cra-fingerprint:"))

    def test_notification_mentions_the_release(self):
        finding = Finding("GHSA-1", "pandas", ">=2.3,<4", "summary", "high", True, "PyPI")
        body = notification_body("1.2.2", [finding], ["theweaklink"])
        self.assertIn("@theweaklink", body)
        self.assertIn("`1.2.2`", body)
        self.assertIn("1 known-exploited", body)

    def test_run_summary_lists_affected_releases(self):
        finding = Finding("GHSA-1", "pandas", ">=2.3,<4", "summary", "high", True, "PyPI")
        text = render_run_summary([("1.2.2", [finding]), ("1.2.1", [])])
        self.assertIn("Scanned 2 releases. 1 has matching advisories.", text)
        self.assertIn("| 1.2.2 | 1 | 1 |", text)
        self.assertNotIn("1.2.1", text)


if __name__ == "__main__":
    unittest.main()
