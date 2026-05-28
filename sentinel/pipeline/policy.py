from __future__ import annotations

import json
from functools import cache
from pathlib import Path


@cache
def load_policy() -> dict:
    policy_path = Path(__file__).resolve().parents[2] / "data" / "policy.json"
    return json.loads(policy_path.read_text(encoding="utf-8"))
