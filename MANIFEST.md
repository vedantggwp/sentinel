# Manifest

## Key Files
- `PLAN.md` — Execution plan: research deltas, dependency DAG, parallel partition, build order, done-criteria.
- `AGENTS.md` — Shared agent contract (Karpathy rules + deterministic-gate hard rule). Source of truth.
- `CLAUDE.md` — Claude-specific notes; imports AGENTS.md.
- `README.md` — Public pitch + architecture diagram + quickstart.
- `sentinel/contracts.py` — Frozen interface: `AdRequest`, `Claim`, `PipelineResult`, `Attestation`, `Verdict`. Import; don't edit without a sync.
- `sentinel/config.py` — Env-backed settings (pydantic-settings). All secrets via `.env`.
- `sentinel/main.py` — FastAPI app; `/health` + `/v1/analyze` wired to the offline deterministic pipeline.
- `sentinel/mcp_server.py` — FastMCP `verify` tool over streamable HTTP; wraps the same deterministic pipeline.
- `sentinel/pipeline/` — Offline context gate, claim extraction, fixture verification, safety scoring, and deterministic `decide_placement`.
- `sentinel/attest/` — ed25519 attestation sign/verify helpers; signs when `ATTESTATION_PRIVATE_KEY_PATH` exists.
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
