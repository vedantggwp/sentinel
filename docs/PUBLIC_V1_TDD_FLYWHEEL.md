# Sentinel Public v1 TDD Flywheel

This is the executable plan for turning Sentinel from hackathon MVP into the
first public-facing version. It is written for future agents as much as for
humans: each loop starts from ground truth, writes failing tests first, ships the
smallest implementation, verifies it, and records the maintenance signal.

## North Star

Public v1 is a trustworthy safety runtime for sponsored AI placements.

It must do three things well:

1. Accept a candidate ad plus conversation context.
2. Return an auditable `APPROVE`, `BLOCK`, or `ESCALATE` verdict.
3. Prove what happened with evidence, hashes, traces, and a signed receipt.

The hard rule does not move: `decide_placement()` is deterministic code. Model
or integration stages may produce scores, claims, and evidence only. They never
decide final pass/fail.

## Current Ground Truth

Verified from the repo, not from the public pitch:

- The deterministic pipeline is real and lives behind `/v1/analyze` and MCP
  `verify`.
- Seed regression has 25 cases and is the current pass/fail gate.
- Held-out adversarial data is measurement only; it intentionally exposes
  brittle heuristic behavior.
- Attestations sign when an ed25519 key is configured; unsigned local receipts
  are allowed only when no secret exists.
- Thrad live ad fetch is env-gated and falls back to fixtures.
- Thrad DistilBERT context classification is optional; heuristic context checks
  are always available.
- Overmind is optional span emission; local audit JSONL is the source of truth.
- Tavily can enter the backend verification path for rating claims when
  `TAVILY_API_KEY` is configured; CI, no-key runs, unsupported claims, and
  provider failures use deterministic fixture fallback.
- OpenAI and Anthropic are dependency/config scaffolding only; no pipeline stage
  calls them today.

Any public copy, demo script, README, or pitch must respect this split.

## Public v1 Contract

Public v1 is ready when all of these are true:

- **Truthful surface:** README, demo, docs, and UI never imply an integration is
  live unless tests prove the live path or clearly label it as optional.
- **Stable API:** `/health`, `/v1/analyze`, `/v1/policy`, `/v1/audit/latest`,
  `/v1/scenarios`, `/v1/escalations`, and MCP `verify` have tests.
- **Live claim verification:** Tavily can verify at least one factual claim when
  configured, with deterministic fixture fallback when not configured.
- **Trace clarity:** Every analysis writes local audit JSONL with input hash, ad
  hash, verdict, rule, scores, claims, source hashes, models used, and
  attestation hash.
- **Optional external traces:** Overmind emission is observable in tests via a
  mocked SDK path, while failures never break the safety gate.
- **Thrad pathway:** Thrad bid fetch has a tested live-normalization path and a
  tested deterministic fallback path.
- **Receipt integrity:** Signed receipts verify, tampered receipts fail, and the
  hosted MCP smoke test proves signed output.
- **Eval discipline:** Seed regression is green; adversarial measurement is
  reported; calibration remains explicitly non-gating until the gold set is
  large enough.
- **Maintenance loop:** Any policy threshold or `data/policy.json` change runs
  the 25-case eval regression first.

## TDD Loop

Use this exact loop for every public-v1 change.

1. **Frame the claim.**
   Write one sentence: "After this change, Sentinel can..."

2. **Classify the lane.**
   Pick exactly one lane: gate, evidence, integration, receipt, trace, API,
   UI/demo, docs, eval, release.

3. **Write the failing test first.**
   The test must fail for the specific missing behavior. Do not bundle multiple
   behaviors into one red test.

4. **Run the narrow command.**
   Use `.venv/bin/python -m pytest path/to/test.py -q`.

5. **Implement the minimum code.**
   Keep changes surgical. Do not refactor adjacent modules unless the test
   cannot pass without it.

6. **Run the narrow command again.**
   The original red test must pass.

7. **Run the lane gate.**
   Use the commands below for the lane.

8. **Record the evidence.**
   Update the relevant doc, manifest, eval snapshot, or runbook. If nothing
   changes publicly, say why in the final handoff.

9. **Run the release gate when the slice is user-visible.**
   At minimum: `.venv/bin/python -m pytest -q` and
   `.venv/bin/python -m sentinel.eval`.

## Lane Gates

| Lane | First tests | Required commands | Notes |
| --- | --- | --- | --- |
| Gate | `tests/test_gate.py`, `tests/test_gate_robustness.py` | `.venv/bin/python -m pytest tests/test_gate.py tests/test_gate_robustness.py -q` plus `python -m sentinel.eval` | Never let LLM or integration output bypass `decide_placement()`. |
| Evidence | claim extraction, fact verification, source hashing tests | `.venv/bin/python -m pytest tests/test_smoke.py tests/test_eval.py -q` | Add fixtures before live calls. |
| Integration | mocked live success, live failure fallback, schema normalization | targeted integration test plus `tests/test_smoke.py` | Never require external network for CI. |
| Receipt | sign/verify/tamper tests | `.venv/bin/python -m pytest tests/test_smoke.py -q` | No secrets in logs, snapshots, or docs. |
| Trace | audit record shape, optional external span emission | targeted trace tests plus `tests/test_smoke.py` | Local audit remains authoritative. |
| API/MCP | FastAPI route and MCP tool tests | `.venv/bin/python -m pytest tests/test_smoke.py -q` | Keep response envelope `{success, data, error}` for API routes. |
| UI/demo | live API mapping, offline fallback, mismatch warning | frontend test if available; otherwise browser/manual runbook evidence | No npm installs without explicit approval. |
| Docs | public truth audit | docs review plus command evidence in final handoff | Docs must not outrun code. |
| Eval | seed/adversarial/calibration tests | `.venv/bin/python -m pytest tests/test_eval.py tests/test_adversarial.py tests/test_calibrate.py -q` | Seed gates; adversarial measures; calibration is non-gating for now. |
| Release | smoke, eval, hosted MCP smoke | `.venv/bin/python -m pytest -q`; `.venv/bin/python -m sentinel.eval`; `MCP_URL=... .venv/bin/python scripts/smoke_mcp_http.py` | Use hosted smoke only when network/deploy state matters. |

## What To Track

Track only signals that change product truth, safety posture, or maintenance
confidence.

- Public-v1 requirements and owner decisions.
- API and MCP contract changes.
- Deterministic gate rules and policy thresholds.
- Eval datasets, expected verdicts, expected rules, and known blind spots.
- Integration mode for each sponsor/tool: `live`, `mocked`, `fixture`,
  `optional`, or `not implemented`.
- Runtime evidence: trace schema, receipt schema, source hashes, model names,
  integration availability, and fallback reason.
- Verification commands and their pass/fail outputs.
- Known public-copy limits: what can be said, what must be caveated.
- Security-sensitive setup requirements, without secret values.

## What Not To Track

Do not create a noisy operating system around trivia.

- Do not track raw secrets, API responses containing keys, or dashboard tokens.
- Do not track every local demo click unless it changed behavior.
- Do not track generated media iterations unless the public asset changed.
- Do not track package-manager churn during the npm/TanStack freeze.
- Do not track speculative integrations without a testable acceptance criterion.
- Do not track vanity metrics as engineering readiness.
- Do not track implementation ideas that do not map to a failing test or a
  documented owner decision.

## Public v1 Backlog

### P0: Truthful Public Surface

Claim: Sentinel's public materials describe only what exists.

RED tests/checks:

- Add a docs truth-audit checklist that lists integration states.
- README wording must distinguish live, optional, and fallback paths.

Acceptance:

- README and demo script no longer imply Tavily/Overmind/Thrad are always live.
- `MANIFEST.md` points to this flywheel.

### P0: Tavily Live Verification With Fixture Fallback

Claim: Sentinel can use Tavily for factual ad claims when configured, and still
runs deterministically without network.

RED tests:

- Given `TAVILY_API_KEY`, verifier calls a mocked `AsyncTavilyClient`.
- Given Tavily failure or no key, verifier returns existing offline fixture
  behavior.
- A false rating claim carries `source_url`, `source_hash`, and `verified=False`.

Acceptance:

- No test requires real network.
- Gate still blocks false claims through `false_claim`.
- README says "live Tavily when configured; fixture fallback otherwise."

Status 2026-06-01: implemented for rating claims in `sentinel/pipeline/claims.py`
with mocked Tavily match/mismatch, failure fallback, no-key fallback,
source-hash, and deterministic-gate tests in `tests/test_fact_verifier.py`.

### P0: Overmind Observable Optional Tracing

Claim: Sentinel can emit an Overmind span when configured, and trace failure does
not affect verdicts.

RED tests:

- Mock `overmind.init` and `get_tracer`; assert span attributes for ad id,
  verdict, and rule.
- Mock Overmind raising; assert `/v1/analyze` still succeeds and local audit is
  written.

Acceptance:

- Local audit JSONL is still authoritative.
- Public copy says Overmind is optional span export, not the only trace store.

### P0: Thrad Live Bid Normalization

Claim: Sentinel can normalize a live Thrad-style bid response into `AdRequest`.

RED tests:

- Mock `httpx.AsyncClient.post` with `{ad: {id, creative, advertiser,
  landing_url}}`.
- Mock timeout/500 and assert fixture fallback.
- Assert no malformed live payload can crash `/v1/thrad/mock`.

Acceptance:

- Endpoint naming is reviewed; public docs avoid pretending mock fallback is
  live bid delivery.

### P1: LLM Evidence Stage, If Needed

Claim: OpenAI/Anthropic may assist evidence extraction, but cannot decide.

RED tests:

- A fake LLM output with a suggested verdict is ignored by `decide_placement()`.
- LLM claim extraction returns structured claims only.
- Malformed LLM output escalates or falls back; it never approves by default.

Acceptance:

- Provider is optional and env-gated.
- No LLM stage writes `verdict`.
- `models_used` records provider/model when used.

### P1: Public API Contract Hardening

Claim: Public v1 has stable, documented response envelopes and failure modes.

RED tests:

- Invalid request returns `{success:false,data:null,error:...}`.
- `/v1/analyze` persists an audit record on success.
- `/v1/policy` returns the active policy shape.

Acceptance:

- Route behavior is documented in README or a public API doc.
- CORS comment is resolved before production deployment.

### P1: Eval and Calibration Governance

Claim: Sentinel can tell owners what changed and whether it helped.

RED tests/checks:

- Any seed case change requires expected verdict and rule.
- Any adversarial improvement updates `currently_passes`.
- Calibration doc states the gold-set floor before becoming CI-gating.

Acceptance:

- `python -m sentinel.eval` remains the owner-facing report.
- Public messaging says seed coverage is regression coverage, not global safety.

## Sub-Agent Execution Packets

Use these packets when delegating. Each agent gets one lane and must return:
files changed, tests added, commands run, pass/fail output, and public truth
impact.

### Agent A: Tavily Evidence

Objective: implement live Tavily verification behind deterministic fixtures.

Boundaries:

- May edit `sentinel/pipeline/claims.py`, add helper modules, add tests.
- May not edit `decide_placement()` except to add tests proving current behavior.
- Must not require live network in tests.

Required first test:

- `tests/test_fact_verifier.py::test_tavily_rating_mismatch_marks_claim_false`

Done when:

- Tavily success, Tavily failure fallback, and no-key fallback are all covered.

### Agent B: Overmind Trace

Objective: make optional Overmind emission testable and owner-visible.

Boundaries:

- May edit `sentinel/tracing.py`, `tests/test_smoke.py`, or add
  `tests/test_tracing.py`.
- May not make Overmind required for `/v1/analyze`.

Required first test:

- `tests/test_tracing.py::test_overmind_span_emits_when_key_configured`

Done when:

- External span success and failure paths are tested; local audit still writes.

### Agent C: Thrad Bid Path

Objective: harden live Thrad normalization and fallback behavior.

Boundaries:

- May edit `sentinel/integrations/thrad_client.py` and related tests.
- May not place live Thrad in the core gate path as a hard dependency.

Required first test:

- `tests/test_thrad_client.py::test_live_thrad_payload_normalizes_to_ad_request`

Done when:

- Live-shaped payload, malformed payload, and transport failure are covered.

### Agent D: LLM Evidence Seam

Objective: design the optional OpenAI/Anthropic evidence seam only if product
needs it.

Boundaries:

- Must start with a short design note and failing tests.
- May not add package-manager work.
- May not let LLM output set final verdict.

Required first test:

- `tests/test_llm_evidence.py::test_llm_suggested_verdict_is_ignored_by_gate`

Done when:

- Provider output is claims/scores/evidence only; malformed output is safe.

### Agent E: Public Surface

Objective: make README, demo, and API docs truthful and owner-ready.

Boundaries:

- May edit docs and public copy.
- May not claim an integration is live without a test or smoke command.

Required first check:

- Create/update an integration truth table: live, optional, fixture, not
  implemented.

Done when:

- Owner can demo without overclaiming.

## Release Checklist

Before calling something public v1:

1. `.venv/bin/python -m pytest -q`
2. `.venv/bin/python -m sentinel.eval`
3. Generate or configure an ed25519 signing key.
4. Run local MCP smoke if touching MCP:
   `PORT=8765 .venv/bin/python -m sentinel.mcp_server`
   and `.venv/bin/python scripts/smoke_mcp_http.py`.
5. Run hosted MCP smoke if deploy changed:
   `MCP_URL=<deployed /mcp URL> .venv/bin/python scripts/smoke_mcp_http.py`.
6. Review README/demo copy against current integration truth.
7. Confirm no secrets, keys, raw tokens, or private dashboard data were printed
   or committed.
8. Update `MANIFEST.md` and any runbook affected by the change.

## Maintenance Rhythm

Daily while building:

- Run the narrow tests for the active lane.
- Keep a one-line truth log of integrations touched.

Before every public demo:

- Run seed regression.
- Run one local `/v1/analyze` scenario for APPROVE, BLOCK, and ESCALATE.
- Run MCP smoke if mentioning hosted MCP.
- Read public copy for live-vs-fallback claims.

Before changing policy:

- Run `tests/test_eval.py`.
- Change policy.
- Run `tests/test_eval.py`, `tests/test_gate.py`,
  `tests/test_gate_robustness.py`, and `python -m sentinel.eval`.
- Explain every changed verdict.

Quarterly or after major model work:

- Expand `data/safety_gold.jsonl`.
- Add annotator provenance.
- Re-run `python -m sentinel.calibrate`.
- Promote calibration to a CI gate only after the gold set reaches the stated
  annotator and volume floor.

## Handoff Template

Use this when assigning a future sub-agent:

```text
You are working in /Users/ved/Documents/Sentinel.

Objective:
<one public-v1 claim>

Lane:
<gate | evidence | integration | receipt | trace | API | UI/demo | docs | eval | release>

Hard rule:
`decide_placement()` remains deterministic. LLM/integration stages produce
scores, claims, evidence, and metadata only.

Start by reading:
- AGENTS.md
- docs/PUBLIC_V1_TDD_FLYWHEEL.md
- MANIFEST.md
- files named in your lane packet

Write the failing test first:
<specific test name>

Allowed files:
<explicit paths>

Forbidden:
- npm/pnpm/yarn/bun install/update/audit-fix
- printing or inspecting secrets
- changing `data/policy.json` without running the 25-case eval regression
- making external services mandatory in CI

Verification:
<narrow command>
<release command if public/user-visible>

Final response must include:
- files changed
- tests added
- commands run with pass/fail
- whether public integration truth changed
```
