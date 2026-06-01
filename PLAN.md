# Sentinel — Execution Plan

> Reviewed + researched 2026-05-28. Source of scope = the 12 GitHub issues.
> This doc adds: research-verified API truth, a parallel partition, the build order, and the positioning that makes us credible to adtech judges.

## The one-sentence pitch

An independent safety layer for ads inside AI conversations: it reads the moment, checks rating claims against live Tavily evidence when configured or fixture fallback otherwise, and emits a **signed, replayable APPROVE/BLOCK receipt** — where **the LLM only scores and deterministic code decides.**

## Hard rule (non-negotiable)

`decide_placement()` is deterministic code. LLM stages emit **scores + evidence only**. Every verdict persists inputs → claims → evidence(+source hashes) → scores → the rule that fired. No routing around the gate.

---

## Research deltas (what changed after the team reported back)

| # | Finding | Action | Source |
|---|---------|--------|--------|
| 12 | **Skybridge = TypeScript/React framework, not our deploy target.** | Deploy the Python MCP server on **Alpic** (GitHub-connect + `alpic.json`). Keep `mcp.run(transport="streamable-http")` — Alpic greps for it; absence defaults to stdio (wrong for remote). For `requirements.txt`, use `uv venv && uv pip install -r requirements.txt`; start with `uv run python -m sentinel.mcp_server`. Bind `0.0.0.0`, read `PORT`. | github.com/alpic-ai/skybridge · docs.alpic.ai/build-deploy/builds |
| 7 | **Overmind optimizer is not a Python call.** It runs via Cursor/Claude-Code slash-commands over a `{input, expected_output}` dataset (10–50 cases). Tracing = OTel spans (`init`/`get_tracer`/`start_as_current_span`). `OVERMIND_PROJECT_ID` is **not** an SDK var. | `tracing.py` = **our own** wrapper that owns audit persistence; Overmind span is optional decoration, errors swallowed. Seed 25 cases as `{input, expected_output}` JSON. Config now exposes `overmind_service_name`/`overmind_environment`. | pypi.org/project/overmind · docs.overmindlab.ai |
| 4 | Tavily: use `AsyncTavilyClient`, `search(query, search_depth="advanced", include_answer="advanced", max_results=5)`. `score` = relevance, **not** truth — don't feed it to the gate as confidence. | Async client in FastAPI; **cache fixtures** so the demo never dies on latency. | docs.tavily.com · github.com/tavily-ai/tavily-python |
| 8 | MCP: `pip install "mcp[cli]"`; `from mcp.server.fastmcp import FastMCP`; `@mcp.tool()`; return the `Attestation` Pydantic model directly for a rich output schema. | Added `mcp[cli]` to requirements. Expose `verify(...) -> Attestation`. | github.com/modelcontextprotocol/python-sdk |
| 2 | **Thrad ships the DistilBERT classifier we wanted.** `Thrad/thrad-distilbert-conversation-classifier` is Apache-2.0, exposes `model.onnx`, and classifies conversation intent into A-M labels. Thrad treats `D`, `J`, `M` as banned for ad serving. | Context gate now lazy-loads the pinned ONNX model when available, records label/confidence as signed evidence, maps policy-threshold `D/J/M` into deterministic ineligible context flags, and falls back to heuristics when unavailable. | github.com/Thrads/Conversation-Classifiers · huggingface.co/Thrad/thrad-distilbert-conversation-classifier |
| — | **Credibility**: GARM Floor + IAB taxonomy + FTC substantiation + ASA vulnerable-consumer rules are real standards we map onto. Our context flags = the *consumer-vulnerability axis* GARM omits. | README/demo: say we implement the vulnerability axis deliberately (not the full GARM content floor). Cite ASA payday/gambling rules for the auto-block rule; FTC for claim types. | WFA/GARM · IAB Tech Lab · FTC · ASA/CAP |

---

## Dependency DAG

```
contracts.py (#1, DONE, frozen) ── everyone imports this
        │
        ├─ context_gate     (#2)  ─┐
        ├─ claim_extractor  (#3)  ─┤
        ├─ fact_verifier    (#4)  ─┼─→ safety_judge + decide_placement (#5) ─→ attestation (#6) ─→ mcp_server (#8) ─→ Alpic deploy (#12)
        ├─ tracing.py       (#7)  ─┘                                                                    │
        └─ Layne ─ thrad_client (#9) ─ UI (#10) ─ escalation (#11) ────────────────────────────────────┘
```

The four pipeline layers (#2–#5) build **in parallel against the frozen contract** — none blocks another. The gate just needs the agreed score keys (`data/policy.json`) + flag names, which already exist.

---

## Parallel partition — "the army"

Everyone builds against `contracts.py`. Each task ships with its own `pytest` check (goal-driven rule).

### 🔵 Opus 4.8 (Ved's seat) — the auditable core, highest correctness stakes
- **#1 contracts** — finalize (done; flag any change for a 30-sec sync, never silent).
- **#5 safety_judge + `decide_placement()`** — the gate. Exhaustive unit tests; the LLM `verdict` field is never read. *This is the heart — it gets the deepest model.*
- **#6 attestation** — ed25519 sign/verify; tamper test must fail.
- **#8 mcp_server** — wrap pipeline as `verify(...) -> Attestation`.

### 🟢 Composer 2.5 — fast, well-specified codegen
- **#2 context_gate** — Thrad DistilBERT intent classifier with keyword fallback, **no LLM**. Test: blocks `anxiety_block`, passes `laptop_clean`, and never emits a verdict.
- **#3 claim_extractor** — small fast model → structured `Claim[]`. Test: extracts "4.9 stars" from the headphones scenario.

### 🟠 Codex 5.5 — integration-heavy, uses the research findings
- **#4 fact_verifier** — `AsyncTavilyClient` + **cached fixtures**. Tests: mocked live Tavily catches 4.9-vs-3.2; no-key and failure paths fall back with no network in CI.
- **#7 tracing.py** — our wrapper (audit persistence + optional Overmind span). Seed 25 `{input, expected_output}` cases.

### 🟣 Layne — integrations + surface + deploy (parallel from minute one)
- **#9 thrad_client** — staging bid-request → normalize to `AdRequest`; mock fallback matching real schema.
- **#10 UI** — split-screen (chat sim | trace + receipt), vanilla HTML/JS.
- **#11 escalation** — grey-zone (overall 2.5–3.5 → ESCALATE) panel with Approve/Block.
- **#12 Alpic deploy** — **not Skybridge** (see deltas). `alpic.json` + GitHub connect.

---

## Build order (critical path to a working demo)

1. **Gate-first vertical slice (done 2026-05-28):** `context_gate` (#2) + safety scoring + `decide_placement` (#5) wired through `/v1/analyze`. All 4 seed scenarios return expected verdicts with deterministic `rule_fired`; Thrad DistilBERT is now an optional pinned classifier signal with heuristic fallback.
2. **Truth layer (Tavily rating adapter + fixture fallback done):** `claim_extractor` (#3) + `fact_verifier` (#4) make the false-rating BLOCK evidence-backed without requiring network.
3. **Receipt (sign/verify helper done; runtime key setup next):** `attestation` (#6) signs when `ATTESTATION_PRIVATE_KEY_PATH` exists; tests prove verify passes and tamper fails.
4. **Reach (done — deployed + live-verified):** `mcp_server` (#8) exposes `verify` over `streamable-http`; deployed on Alpic (#12), live at `https://sentinel-74667ec0.alpic.live/mcp`.
5. **Observability + polish (local trace/UI done; hosted Overmind next):** `tracing.py` (#7) persists local audit JSONL and ships 25 seed cases; UI (#10/#11) consumes the trace and receipt.

**Reliability rule:** every external call (Tavily, Thrad, LLM) has a cached/mock fallback. The live demo must run with the network unplugged.

## Definition of done (demo)

- `uv run --python 3.12 --with-requirements requirements.txt pytest -q` green, gate unit tests cover hard rules.
- All 4 seed scenarios return the `expected` verdict via `/v1/analyze`. **Done.**
- One BLOCK shows: vulnerability flag OR a fact-checked false claim with `actual_value` + `source_url`. **Done.**
- Response carries an `Attestation`; verify passes and tamper fails when the local ed25519 key is configured. **Done.**
- Demo UI runs at `/demo/` and covers APPROVE/BLOCK/ESCALATE with receipt + trace. **Done locally.**
- `verify` reachable as a deployed MCP tool. **Done — live at `https://sentinel-74667ec0.alpic.live/mcp`; remote `verify()` returns BLOCK · `false_claim` with a signature that verifies.**
