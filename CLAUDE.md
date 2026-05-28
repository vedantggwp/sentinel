@./AGENTS.md

# Claude Code — Sentinel

`AGENTS.md` (imported above) is the source of truth — including the Karpathy behavior rules and the deterministic-gate hard rule. Claude-specific notes only below.

## Model routing in the pipeline (not the build)

- Layer 1 Context Gate: a classifier/heuristic, **not** an LLM (must be ~20ms).
- Layer 2 Claim Extraction: a small, fast model.
- Layer 4 Safety Judge: a mid model — emits **scores only**; the gate decides in code.
- Reserve the strongest model for the gate/attestation design and offline eval, not the request hot path.

## Workflow

- Plan mode for multi-file work (pipeline wiring, attestation, MCP). Direct edits for one-liners.
- Give every task a check it can run — `pytest` closes the loop on the gate.
- `/clear` between unrelated tasks. If you can't verify it, don't ship it.
