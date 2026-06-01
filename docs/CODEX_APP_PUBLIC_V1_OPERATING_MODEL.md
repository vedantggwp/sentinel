# Codex App Operating Model for Sentinel Public v1

This document explains how to use Codex app capabilities to execute
`docs/PUBLIC_V1_TDD_FLYWHEEL.md` and turn Sentinel into production-ready public
software without losing the deterministic-gate contract.

## CTO Rule

Use Codex as an engineering organization, not a bigger chat box.

- One **orchestrator thread** owns truth, sequencing, and integration.
- Bounded **worker agents** own disjoint code slices.
- **Explorer agents** answer narrow codebase questions.
- **Automations** run recurring verification and drift checks.
- **Plugins/connectors** touch external systems only when they are the source of
  truth for that system.
- Every public claim must map to code, tests, docs, and a verification command.

## Roles

### Orchestrator

The main Codex thread is the CTO/staff engineer. It must:

- maintain the public-v1 backlog;
- select the next lane from the flywheel;
- write or approve the first failing test;
- spawn workers only for independent slices;
- integrate worker changes;
- run release gates;
- update docs and public truth tables;
- refuse to merge anything that routes around `decide_placement()`.

The orchestrator does not outsource final judgment.

### Explorer Agents

Use explorer agents for read-only questions that can run in parallel, for
example:

- "Where does claim verification actually happen?"
- "Which public docs overclaim Tavily?"
- "Which tests cover MCP receipt signing?"

Explorer output must be file/line grounded. Explorers do not edit files.

### Worker Agents

Use worker agents for concrete code changes with disjoint ownership:

- Tavily evidence worker: `sentinel/pipeline/claims.py`,
  `tests/test_fact_verifier.py`.
- Overmind trace worker: `sentinel/tracing.py`, `tests/test_tracing.py`.
- Thrad bid worker: `sentinel/integrations/thrad_client.py`,
  `tests/test_thrad_client.py`.
- API hardening worker: `sentinel/main.py`, `tests/test_api_contract.py`.
- Public docs worker: `README.md`, `DEMO.md`, docs truth table.

Workers must edit their files directly in their forked workspace and report:
files changed, tests added, commands run, public truth impact, and unresolved
risks.

### Verifier Agent

Use a verifier only after implementation has something real to check. It should
not rewrite the product. It should answer:

- Does the code deliver the claim?
- Do tests prove the right behavior?
- Did public copy overclaim?
- Did any external service become mandatory in CI?
- Can the gate still be replayed and audited?

## Feature Mapping

| Codex app feature | How Sentinel should use it | What not to use it for |
| --- | --- | --- |
| Multi-agent workers | Parallel P0 lanes with disjoint files | Multiple agents editing the same gate/policy files |
| Explorer agents | Fast repo audits and overclaim checks | Strategic decisions without code evidence |
| Automations | Nightly/weekly test, eval, docs truth, hosted MCP smoke | Replacing real CI or hiding failures |
| Browser / Chrome plugin | Local UI smoke, hosted docs/demo review, screenshot checks | Backend/API verification |
| GitHub plugin | PR creation, issue triage, CI/log review | Bypassing local tests |
| Vercel/Alpic deploy path | Hosted demo/API/MCP smoke once local gates pass | Deploy-first debugging |
| OpenAI Developers plugin | API-key setup or current OpenAI API docs when adding an LLM evidence seam | Letting an LLM decide placement |
| Notion/Linear plugins | Product backlog, owner decisions, external status board | Source of truth for code behavior |
| Slack/Hermes | Human coordination and review requests | Shipping secrets or unreviewed claims |

## Execution Pattern

For every public-v1 slice:

1. Orchestrator states the product claim.
2. Orchestrator chooses one flywheel lane.
3. Orchestrator writes or assigns the first failing test.
4. If the slice is independent, spawn one worker with:
   - objective;
   - allowed files;
   - forbidden files;
   - first failing test name;
   - exact verification command;
   - output schema.
5. Orchestrator continues non-overlapping work while workers run.
6. Orchestrator reviews worker patch, not just the summary.
7. Orchestrator runs lane gate.
8. Orchestrator updates docs/manifests/eval snapshots.
9. Orchestrator runs release gate for user-visible changes.

## Parallelization Plan

Do this in waves.

### Wave 0: Truth Freeze

Goal: stop public overclaiming before adding features.

Local orchestrator:

- create integration truth table;
- update README/DEMO wording;
- run full tests and eval.

Optional explorer:

- audit public docs for "live Tavily", "Overmind trace", "Thrad bid", "OpenAI",
  and "Anthropic" claims.

### Wave 1: Live Integrations Behind Fallbacks

Spawn at most three workers because their write sets are disjoint:

- Worker A: Tavily live verification with fixture fallback.
- Worker B: Overmind observable optional tracing.
- Worker C: Thrad live bid normalization.

Orchestrator locally owns:

- no-gate-bypass tests;
- README public truth update;
- release gate.

### Wave 2: API and Receipt Hardening

Workers:

- API contract worker;
- receipt/attestation hardening worker, if needed.

Orchestrator:

- runs end-to-end `/v1/analyze` and MCP verify;
- confirms audit schema;
- updates public API docs.

### Wave 3: LLM Evidence Seam

Only start after Waves 0-2.

Use OpenAI/Anthropic only for evidence extraction or evidence summarization. The
first test must prove a fake LLM-suggested verdict is ignored. If this seam does
not improve claim extraction or safety scoring, do not add it.

### Wave 4: Launch System

Use Browser/Chrome for UI smoke, GitHub for PR/release flow, and automation for
recurring gates. Public launch requires:

- green full test suite;
- seed eval green;
- adversarial report included as known-limit measurement;
- hosted MCP smoke green;
- signed receipts configured;
- truthful README/demo;
- security note and privacy posture reviewed.

## Automations

Recommended Codex app routines:

### Daily Sentinel Health

Schedule: weekday morning.

Prompt:

```text
In /Users/ved/Documents/Sentinel, run the public-v1 health check:
git status --short --branch, .venv/bin/python -m pytest -q, and
.venv/bin/python -m sentinel.eval. Summarize failures, changed verdicts, dirty
public docs, and whether integration truth changed. Do not inspect or print
secrets.
```

### Weekly Public Claim Audit

Schedule: weekly.

Prompt:

```text
Audit README.md, DEMO.md, MANIFEST.md, docs/, and frontend copy for claims about
Tavily, Overmind, Thrad, OpenAI, Anthropic, signed receipts, hosted MCP, and
production readiness. Compare against code paths and tests. Report overclaims
with file/line references and proposed wording. Do not edit unless explicitly
asked.
```

### Hosted MCP Smoke

Schedule: daily only when a public endpoint is active.

Prompt:

```text
Run the hosted Sentinel MCP smoke script against the configured MCP_URL. Report
tool list, verdict, rule_fired, signed status, and any transport errors. Do not
print secrets.
```

### Dependency Freeze Watch

Schedule: weekly.

Prompt:

```text
Check git diff/status for package manager lockfile or dependency changes in
Sentinel. Report any npm/pnpm/yarn/bun install/update/audit-fix evidence and
whether it violates the active freeze. Do not run package-manager installs.
```

## Plugin Use

### Browser / Chrome

Use after UI/demo changes:

- open local `/demo`;
- run approve/block/escalate scenarios;
- verify no text overlap;
- verify live/offline API indicator is truthful;
- capture screenshots only when public assets change.

Do not use browser checks as proof that backend policy is correct.

### GitHub

Use for:

- PRs per wave;
- CI failures;
- issue tracking;
- release notes.

PRs should include:

- claim delivered;
- tests added;
- eval result;
- integration truth changes;
- screenshots only for UI changes.

### OpenAI Developers

Use only when adding the LLM evidence seam or current OpenAI API behavior is
needed. The seam must output structured evidence, never verdicts.

### Notion / Linear

Use for owner-visible backlog and decision records. The repo remains the
engineering source of truth.

### Slack / Hermes

Use for review requests and stakeholder updates. Never send secrets or private
keys.

## Worker Prompt Template

```text
You are a worker agent in /Users/ved/Documents/Sentinel.

Objective:
<one public-v1 claim>

Owned files:
<explicit paths>

Forbidden files:
- sentinel/pipeline/gate.py unless asked only to add tests
- data/policy.json unless the orchestrator approved a policy change
- package files / lockfiles unless explicitly approved

Context:
- Read AGENTS.md
- Read docs/PUBLIC_V1_TDD_FLYWHEEL.md
- Read docs/CODEX_APP_PUBLIC_V1_OPERATING_MODEL.md

Hard rule:
The deterministic gate owns final verdicts. LLMs/integrations produce claims,
scores, evidence, metadata, or traces only.

TDD:
1. Write this failing test first: <test name>
2. Run: <narrow command>
3. Implement minimum code
4. Run: <narrow command>
5. Run: <lane gate>

Return:
- files changed
- tests added
- commands run and pass/fail
- public truth impact
- risks or follow-up
```

## Governance

The production-readiness bar is not "the demo looks good." It is:

- every public claim has a test or smoke command;
- every external dependency has a fallback or documented failure mode;
- every verdict is replayable;
- every gate change has eval evidence;
- every user-visible behavior has docs;
- every release can be reproduced by another Codex thread from the repo.

When in doubt, make the claim smaller and the evidence stronger.
