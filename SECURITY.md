# Security

OneCode is open source under the MIT license and is maintained by DeepLime, not as a community project. Security fixes are published for the maintained `1.x` line.

## Reporting a vulnerability

Report a vulnerability in OneCode through [GitHub private vulnerability reporting](https://github.com/deeplime-io/onecode/security/advisories/new).

Do not open a public issue, and do not file the report in the GitHub Advisory Database. A public report discloses the problem before a fix is available.

DeepLime acknowledges the report, prepares a fix on the maintained line, and releases it. After that release, DeepLime publishes a GitHub Security Advisory. That publication is what enters the public advisory database and OSV.

If the vulnerability is actively exploited, DeepLime also reports it through the CRA single reporting platform operated with ENISA. That duty applies from 11 September 2026. An early warning is due within 24 hours of learning that exploitation is underway, followed by the fuller notification the platform requires.

## Dependency monitor

Issues labeled [`cra-vulnerability`](https://github.com/deeplime-io/onecode/issues?q=is%3Aissue+is%3Aopen+label%3Acra-vulnerability) are opened by the scheduled scan of release SBOMs. They record published advisories that intersect a released dependency range. They are not the channel for reporting a new vulnerability in OneCode.

Each published GitHub release carries a CycloneDX file named `onecode-<version>.cdx.json`.
