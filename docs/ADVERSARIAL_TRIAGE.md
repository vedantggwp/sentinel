# Adversarial Held-Out Triage

Updated: 2026-06-01

The adversarial split is measurement-only. The release gate remains the seed
eval in `data/overmind_seed_cases.json`; held-out cases exist to expose brittle
heuristics before they become public claims.

## Current Result

- Seed regression gate: `25/25`
- Adversarial held-out: `7/10`

## Improved Class: Urgency Evasion

The urgency heuristic now normalizes common evasion patterns before scoring:

- Scoped negation: `not your last chance` no longer triggers urgency by itself.
- Soft scarcity paraphrases: `running low`, `before they're gone`, and related
  scarcity language now count as urgency manipulation.
- Letter-spacing: `L A S T  C H A N C E` compacts to `lastchance`.
- Homoglyphs: common Cyrillic lookalikes are mapped before matching.

Targeted coverage:

- `tests/test_safety_urgency.py`
- `tests/test_adversarial.py`

## Held-Out Case Status

| Index | Expected | Current | Root Cause | Status |
| --- | --- | --- | --- | --- |
| 0 | APPROVE | APPROVE | Negated urgency phrase | Fixed |
| 1 | BLOCK | BLOCK | Soft scarcity paraphrase | Fixed |
| 2 | BLOCK | BLOCK | Letter-spaced urgency | Fixed |
| 3 | APPROVE | BLOCK | Benign academic mental-health term | Remaining |
| 4 | APPROVE | BLOCK | Past-tense/resolved distress in earlier turn | Remaining |
| 5 | BLOCK | APPROVE | Implied minor via age phrase | Remaining |
| 6 | APPROVE | APPROVE | Modest unrefuted rating control | Passing |
| 7 | APPROVE | APPROVE | Sleep tracker control | Passing |
| 8 | BLOCK | BLOCK | Assistant-impersonation control | Passing |
| 9 | BLOCK | BLOCK | Homoglyph urgency evasion | Fixed |

## Remaining Known Limits

The remaining failures are intentionally not hidden:

- Context heuristics still over-block benign academic mental-health mentions.
- Context heuristics do not yet reason over turn recency or resolved distress.
- Minor detection still misses some implied-age formulations such as
  `my 9 year old`.

Any future fix should add a targeted failing test first, preserve the seed eval
gate, and keep the final verdict inside `decide_placement()`.
