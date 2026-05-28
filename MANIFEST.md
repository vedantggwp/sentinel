# Manifest

## Key Files
- `PLAN.md` — Execution plan: research deltas, dependency DAG, parallel partition, build order, done-criteria.
- `AGENTS.md` — Shared agent contract (Karpathy rules + deterministic-gate hard rule). Source of truth.
- `CLAUDE.md` — Claude-specific notes; imports AGENTS.md.
- `README.md` — Public pitch + architecture diagram + quickstart.
- `DEMO.md` — Local demo runbook, click path, API/MCP checks, and Alpic handoff.
- `sentinel/contracts.py` — Frozen interface: `AdRequest`, `Claim`, `PipelineResult`, `Attestation`, `Verdict`. Import; don't edit without a sync.
- `sentinel/config.py` — Env-backed settings (pydantic-settings). All secrets via `.env`.
- `sentinel/main.py` — FastAPI app; `/health` + `/v1/analyze` wired to the offline deterministic pipeline.
- `sentinel/mcp_server.py` — FastMCP `verify` tool over streamable HTTP; wraps the same deterministic pipeline.
- `sentinel/tracing.py` — Local audit JSONL persistence plus optional Overmind span emission.
- `sentinel/integrations/thrad_client.py` — Thrad staging adapter with deterministic mock fallback.
- `sentinel/pipeline/` — Offline context gate, claim extractor, fixture fact verifier, safety judge, and deterministic `decide_placement`.
- `sentinel/attest/` — ed25519 attestation sign/verify helpers; signs from a PEM file (`ATTESTATION_PRIVATE_KEY_PATH`) or PEM env secret (`ATTESTATION_PRIVATE_KEY_PEM`, for hosted deploys).
- `alpic.json` — Alpic deploy manifest (install/start commands) for hosting the MCP `verify` tool (#12).
- `ui/` — Vanilla split-screen demo UI served by FastAPI at `/demo/`.
- `data/overmind_seed_cases.json` — 25 `{input, expected_output}` cases for optimizer/demo seeding.
- `data/policy.json` — Ineligible contexts, score dimensions, block/escalate thresholds.
- `data/scenarios.json` — 4 seed scenarios = the acceptance test for the demo.
- `tests/test_smoke.py` — Health, API scenario, attestation, and MCP wrapper smoke tests.
- `tests/test_gate.py` — Exhaustive deterministic-gate branch tests; proves no LLM verdict override input exists.

## Recent Changes
- 2026-05-28: Created `PLAN.md` — reviewed plan + research findings (Tavily/Overmind/MCP/Alpic/adtech-standards) + parallel partition.
- 2026-05-28: Created `MANIFEST.md` — per CLAUDE.md file-manifest rule.
- 2026-05-28: Updated `sentinel/config.py` — added `overmind_service_name`/`overmind_environment` (real SDK vars); marked `overmind_project_id` console-only.
- 2026-05-28: Updated `requirements.txt` — added `mcp[cli]` for the MCP server (#8).
- 2026-05-28: Wired `/v1/analyze` to the deterministic offline MVP pipeline; all seed scenarios now return expected verdicts.
- 2026-05-28: Added attestation sign/verify helpers and tests proving valid signatures pass while tampering fails.
- 2026-05-28: Added local FastMCP `verify` tool using `streamable-http` for the Alpic deployment path.
- 2026-05-28: Aligned `decide_placement` with the policy-backed gate contract and exhaustive branch tests.
- 2026-05-28: Made attestation deploy-ready — signing key loads from `ATTESTATION_PRIVATE_KEY_PEM` env when no key file exists; added `alpic.json`. Deployed `verify()` now returns signed (not silently unsigned) receipts.
- 2026-05-28: Added local audit tracing, seeded optimizer cases, Thrad mock fallback, and `/demo/` UI with escalation actions.
- 2026-05-28: Added `DEMO.md` runbook for the presentation path and hosted deploy handoff.
