from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from sentinel.config import settings
from sentinel.pipeline.thrad_context_classifier import (
    CLASS_ORDER,
    INTENT_BY_CODE,
    IntentPrediction,
    ThradConversationClassifier,
)


CONTEXT_PATTERNS: dict[str, tuple[str, ...]] = {
    "mental_health": ("anxious", "anxiety", "depressed", "can't sleep", "panic"),
    "self_harm": ("self harm", "suicide", "kill myself"),
    "medical_emergency": ("chest pain", "overdose", "emergency room"),
    "financial_distress": ("money lately", "pay rent", "debt", "broke", "payday"),
    "bereavement": ("grieving", "bereavement", "funeral"),
    "addiction": ("addicted", "relapse", "gambling problem"),
    "minor": ("i am 13", "i'm 13", "under 18", "my child"),
    "illegal_or_unsafe": ("make a bomb", "hack into", "steal someone's"),
}

THRAD_BLOCKING_INTENTS: dict[str, str] = {
    "D": "thrad_creative_writing_and_role_play",
    "J": "thrad_relationships_and_personal_reflection",
    "M": "thrad_obscene_or_illegal",
}


@dataclass(frozen=True)
class ContextGateResult:
    vulnerability_flags: list[str]
    contextual_safety: float
    scores: dict[str, float]


def assess_context(conversation: str) -> tuple[list[str], float]:
    result = assess_context_with_evidence(conversation)
    return result.vulnerability_flags, result.contextual_safety


def assess_context_with_evidence(conversation: str) -> ContextGateResult:
    text = conversation.lower()
    flags = [
        flag
        for flag, patterns in CONTEXT_PATTERNS.items()
        if any(pattern in text for pattern in patterns)
    ]
    scores: dict[str, float] = {}
    prediction = _classify_with_thrad(conversation)

    if prediction is not None:
        scores.update(_prediction_scores(prediction))
        _apply_prediction(flags, prediction)
    elif settings.context_classifier_backend != "heuristic":
        scores["context_classifier_available"] = 0.0

    contextual_safety = _contextual_safety(flags, prediction)
    return ContextGateResult(
        vulnerability_flags=_unique(flags),
        contextual_safety=contextual_safety,
        scores=scores,
    )


def context_gate_model_metadata(scores: dict[str, float]) -> dict[str, str]:
    models = {"context_gate": "keyword-heuristic-v0"}
    if scores.get("context_classifier_available") == 1.0:
        models["context_classifier"] = (
            f"{settings.thrad_context_model_id}@"
            f"{settings.thrad_context_model_revision} (onnx)"
        )
        prediction = _prediction_metadata(scores)
        if prediction:
            models["context_classifier_prediction"] = prediction
    elif "context_classifier_available" in scores:
        models["context_classifier"] = (
            "thrad-distilbert-unavailable; heuristic fallback"
        )
    return models


def _classify_with_thrad(conversation: str) -> IntentPrediction | None:
    if settings.context_classifier_backend == "heuristic":
        return None

    try:
        return _get_context_classifier().classify(conversation)
    except Exception:
        return None


def _get_context_classifier() -> ThradConversationClassifier:
    return _build_context_classifier(
        settings.thrad_context_model_id,
        settings.thrad_context_model_revision,
        settings.thrad_context_tokenizer_id,
        settings.context_classifier_local_files_only,
    )


@lru_cache(maxsize=4)
def _build_context_classifier(
    model_id: str,
    model_revision: str,
    tokenizer_id: str,
    local_files_only: bool,
) -> ThradConversationClassifier:
    return ThradConversationClassifier(
        model_id=model_id,
        model_revision=model_revision,
        tokenizer_id=tokenizer_id,
        local_files_only=local_files_only,
    )


def _prediction_scores(prediction: IntentPrediction) -> dict[str, float]:
    return {
        "context_classifier_available": 1.0,
        "context_classifier_confidence": round(prediction.confidence, 4),
        "context_classifier_label_index": float(CLASS_ORDER.index(prediction.label)),
        "context_classifier_blocking_intent": (
            1.0 if prediction.label in THRAD_BLOCKING_INTENTS else 0.0
        ),
    }


def _apply_prediction(flags: list[str], prediction: IntentPrediction) -> None:
    if prediction.label not in THRAD_BLOCKING_INTENTS:
        return
    if prediction.confidence < settings.context_classifier_block_confidence:
        return
    flags.append(THRAD_BLOCKING_INTENTS[prediction.label])


def _contextual_safety(
    flags: list[str],
    prediction: IntentPrediction | None,
) -> float:
    if flags:
        return 0.0
    if prediction is None or prediction.label not in THRAD_BLOCKING_INTENTS:
        return 5.0
    if prediction.confidence >= settings.context_classifier_review_confidence:
        return 3.0
    return 5.0


def _unique(flags: list[str]) -> list[str]:
    return list(dict.fromkeys(flags))


def _prediction_metadata(scores: dict[str, float]) -> str:
    label_index = scores.get("context_classifier_label_index")
    confidence = scores.get("context_classifier_confidence")
    if label_index is None or confidence is None:
        return ""

    index = int(label_index)
    if index < 0 or index >= len(CLASS_ORDER):
        return ""

    label = CLASS_ORDER[index]
    category = INTENT_BY_CODE[label]
    return f"{label}:{category.name}@{confidence:.4f}"
