# AGENTS.md — Sentinel

Shared contract for all AI coding agents (Codex, Cursor) and humans. Claude Code imports this via `CLAUDE.md`.

## Agent behavior — the "Karpathy rules"

*Four LLM-agent failure modes observed by Andrej Karpathy (Jan 2026), codified by Forrest Chang (`forrestchang/andrej-karpathy-skills`). Bias toward caution over speed; use judgment on trivial tasks.*

1. **Think before coding.** State assumptions explicitly; if uncertain, ask. If multiple interpretations exist, present them — don't pick silently. If a simpler approach exists, say so. If something's unclear, stop and name it.
2. **Simplicity first.** Minimum code that solves the problem. No features beyond what was asked, no speculative abstractions, no error handling for impossible cases. If 200 lines could be 50, rewrite it.
3. **Surgical changes.** Touch only what the task requires — every changed line traces to the request. Don't refactor or reformat adjacent code. Remove orphans *your* change created; mention (don't delete) pre-existing dead code.
4. **Goal-driven execution.** Turn each task into a verifiable success criterion and loop until it passes ("add validation" → "write tests for invalid inputs, then make them pass").

## Sentinel hard rule

The final pass/fail (`decide_placement`) is **deterministic code**. LLM stages output **scores + evidence only** — they never decide. Every verdict is auditable & replayable: persist inputs, claims, evidence (+ source hashes), scores, and the rule that fired. Do not route around the gate.

## Build & run

- Python 3.12 + FastAPI. UI: plain HTML/JS — no framework, no build step.
- Install: `uv pip install -r requirements.txt` · **No npm/pnpm/yarn installs (supply-chain freeze).**
- API: `uvicorn sentinel.main:app --reload --port 8000`
- Test: `pytest -q` · Format (if installed): `ruff format . && ruff check .`

## Layout & ownership

- **Ved:** `sentinel/pipeline/` (4 layers), `sentinel/contracts.py`, `sentinel/attest/`, `sentinel/tracing.py`, `sentinel/mcp_server.py`, `sentinel/main.py`
- **Layne:** `sentinel/integrations/` (Thrad), `ui/`
- `contracts.py` is the interface (`AdRequest`, `PipelineResult`, `Attestation`). Import it; don't edit unless you own it — changing it needs a 30-second sync.

## Conventions

- Immutable data (return copies, never mutate). Files < 400 lines, functions < 50, nesting < 4.
- Validate all external input at the boundary. API responses use `{success, data, error}`; routes under `/v1/`.
- Tests: don't mock the logic under test (gate, parsers) — test real logic; DO mock external I/O (Tavily/LLM/Thrad). The gate + attestation sign/verify MUST have tests.

## Secrets

All keys (Thrad/Tavily/Overmind/OpenAI/Anthropic + the attestation signing key) live in `.env` only — never commit, print, or log them.
