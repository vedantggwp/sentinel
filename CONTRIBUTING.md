# Contributing

Sentinel welcomes focused fixes, tests, and documentation improvements that make
sponsored AI placement decisions safer, more truthful, or easier to audit.

## Core Rule

`decide_placement()` is the final authority. Model outputs, sponsor tools, and
external integrations may provide claims, scores, evidence, and traces, but they
must never decide the final `APPROVE`, `BLOCK`, or `ESCALATE` verdict.

## Development Loop

1. Open or pick one concrete issue.
2. Write the failing test first.
3. Make the smallest code change that passes the test.
4. Run the narrow test command.
5. Run the relevant release checks before opening a pull request.

For user-visible or policy changes, run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m sentinel.eval
```

## Pull Requests

Please include:

- the behavior or claim changed;
- tests added or updated;
- commands run;
- any change to public README/demo claims;
- whether external integrations are live, mocked, fixture-backed, optional, or
  not implemented.

Do not commit `.env` files, API keys, signing keys, audit logs, local browser
captures, or generated dependency directories.
