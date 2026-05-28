from __future__ import annotations


CONTEXT_PATTERNS: dict[str, tuple[str, ...]] = {
    "mental_health": ("anxious", "anxiety", "depressed", "can't sleep", "panic"),
    "self_harm": ("self harm", "suicide", "kill myself"),
    "medical_emergency": ("chest pain", "overdose", "emergency room"),
    "financial_distress": ("money lately", "pay rent", "debt", "broke", "payday"),
    "bereavement": ("grieving", "bereavement", "funeral"),
    "addiction": ("addicted", "relapse", "gambling problem"),
    "minor": ("i am 13", "i'm 13", "under 18", "my child"),
}


def assess_context(conversation: str) -> tuple[list[str], float]:
    text = conversation.lower()
    flags = [
        flag
        for flag, patterns in CONTEXT_PATTERNS.items()
        if any(pattern in text for pattern in patterns)
    ]
    return flags, 0.0 if flags else 5.0
