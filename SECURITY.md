# Security Policy

Sentinel is a safety and claim-verification layer for sponsored recommendations
inside AI conversations. Security issues are treated as product-critical because
the project signs and audits placement decisions.

## Supported Scope

Please report issues that affect:

- incorrect `APPROVE` decisions for unsafe or false sponsored claims;
- bypasses of the deterministic placement gate;
- receipt signing, verification, or tamper-detection failures;
- exposure of secrets, signing keys, audit logs, or user conversation data;
- MCP/API behavior that allows unauthorized access or unsafe input handling.

## Reporting

Do not publish exploit details in a public issue. Use GitHub's private
vulnerability reporting flow when available, or contact the maintainer through
the GitHub profile for `@vedantggwp` with a brief, non-sensitive summary.

Useful reports include:

- affected commit or version;
- route, tool, or module involved;
- minimal reproduction steps;
- expected vs actual verdict or receipt behavior;
- whether any secret, user data, or external service was involved.

## Maintainer Response

The maintainer will triage security reports before ordinary feature work. Fixes
that affect verdict logic must include regression tests for the relevant gate,
receipt, API, or MCP behavior before release.
