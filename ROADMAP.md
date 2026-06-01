# Roadmap

Sentinel is an early public OSS project. The current release is a working
hackathon-origin safety runtime with deterministic policy gates, API/MCP
surfaces, signed receipts, tests, and eval reporting. The roadmap below keeps
the public claims tied to maintainable code rather than adoption theater.

## Current Public Baseline

- Public MIT-licensed repository maintained by [@vedantggwp](https://github.com/vedantggwp).
- FastAPI `/v1/analyze` route and MCP `verify` tool share the same placement
  pipeline.
- Final `APPROVE`, `BLOCK`, or `ESCALATE` verdict comes from deterministic
  policy code.
- Rating claims can use live Tavily evidence when `TAVILY_API_KEY` is
  configured, with deterministic fixture fallback for CI, no-key runs, and
  provider failures. Price, availability, endorsement, and statistic claims
  have explicit fixture-backed or non-verifiable fallback outcomes with source
  hashes.
- Receipts can be signed and verified when a local ed25519 key is configured.
- Seed eval regression is the maintainer gate; adversarial cases are reported
  as measurement and known-limit evidence.
- Security policy, contributing guide, maintainer file, and public-v1 operating
  docs are in the repository.

## Public v1 Priorities

1. **Live claim verification with safe fallback**
   - Issue: [#13](https://github.com/vedantggwp/sentinel/issues/13)
   - Status: implemented for live rating claims plus explicit fallback behavior
     for price, availability, endorsement, and statistic claims.
   - Keep deterministic fixture fallback for CI and local development.
   - Preserve the rule that external evidence can inform the gate but cannot
     decide the final verdict.

2. **Optional trace export**
   - Issue: [#14](https://github.com/vedantggwp/sentinel/issues/14)
   - Status: implemented with local-audit authority and failure-safe tests.
   - Emit Overmind spans when configured.
   - Keep local audit JSONL authoritative.
   - Prove tracing failures do not affect API/MCP verdicts.

3. **Ad bid normalization**
   - Issue: [#15](https://github.com/vedantggwp/sentinel/issues/15)
   - Status: implemented with live-shaped payload and fallback tests.
   - Normalize Thrad-style bid payloads into Sentinel request contracts.
   - Test live-shaped success, timeout, server error, and malformed payload
     fallback paths.

4. **API, MCP, and receipt hardening**
   - Issue: [#16](https://github.com/vedantggwp/sentinel/issues/16)
   - Status: implemented with public contract and release-check coverage.
   - Stabilize public response envelopes.
   - Expand signing, verification, and tamper-detection tests.
   - Document hosted MCP smoke checks once a public endpoint is active.

## Active Hardening Backlog

The initial public-v1 lane is implemented, with follow-up issues kept open for
the next maintainer wave:

- [#23](https://github.com/vedantggwp/sentinel/issues/23) broaden Tavily claim
  verification beyond rating claims while keeping no-network fallback tests.
  Status: implemented as scoped fallback behavior for price, availability,
  endorsement, and statistic claims; only rating claims are live-backed by
  Tavily in this release.
- [#24](https://github.com/vedantggwp/sentinel/issues/24) remediate known
  adversarial held-out eval gaps without hiding remaining measurement-only
  failures. Status: urgency-evasion class improved; held-out score is now
  `7/10`; remaining context/minor-detection limits are documented in
  `docs/ADVERSARIAL_TRIAGE.md`.
- [#25](https://github.com/vedantggwp/sentinel/issues/25) harden hosted MCP
  smoke and deployment controls without making hosted services a CI dependency.
  Status: implemented with manual hosted smoke workflow, redacted smoke output,
  and configurable production CORS origins.

## Where Codex and API Credits Help

Codex for OSS support would be used for maintainer work, not for replacing the
deterministic gate:

- PR review for policy, API, MCP, receipt, and integration changes.
- Test generation around edge cases, malformed payloads, and security-sensitive
  receipt behavior.
- Eval-regression summaries after policy or threshold changes.
- Release workflow assistance for changelogs, issue triage, and verification
  checklists.
- Optional LLM-assisted evidence extraction only after tests prove suggested
  verdicts are ignored by `decide_placement()`.

## Non-Goals

- No model or external integration decides final ad placement.
- No live service is required for CI.
- No public claim should imply broad adoption before it exists.
- No secrets, signing keys, or raw private audit data belong in the repository.
