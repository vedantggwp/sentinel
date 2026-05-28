from sentinel.pipeline import context_gate
from sentinel.pipeline.context_gate import (
    assess_context,
    assess_context_with_evidence,
    context_gate_model_metadata,
)
from sentinel.pipeline.thrad_context_classifier import IntentPrediction


class FakeClassifier:
    def __init__(self, prediction: IntentPrediction):
        self.prediction = prediction

    def classify(self, conversation: str) -> IntentPrediction:
        return self.prediction


def test_assess_context_keeps_tuple_contract(monkeypatch):
    monkeypatch.setattr(
        context_gate.settings, "context_classifier_backend", "heuristic"
    )

    flags, score = assess_context("User: I can't sleep because I am anxious.")

    assert flags == ["mental_health"]
    assert score == 0.0


def test_high_confidence_thrad_blocking_intent_adds_gate_flag(monkeypatch):
    prediction = _prediction("J", "relationships_and_personal_reflection", 0.91)
    monkeypatch.setattr(context_gate.settings, "context_classifier_backend", "auto")
    monkeypatch.setattr(
        context_gate,
        "_get_context_classifier",
        lambda: FakeClassifier(prediction),
    )

    result = assess_context_with_evidence("User: I keep replaying a painful breakup.")

    assert result.vulnerability_flags == ["thrad_relationships_and_personal_reflection"]
    assert result.contextual_safety == 0.0
    assert result.scores["context_classifier_available"] == 1.0
    assert result.scores["context_classifier_confidence"] == 0.91
    assert result.scores["context_classifier_label_index"] == 9.0
    assert result.scores["context_classifier_blocking_intent"] == 1.0

    metadata = context_gate_model_metadata(result.scores)
    assert metadata["context_classifier_prediction"] == (
        "J:relationships_and_personal_reflection@0.9100"
    )


def test_policy_confidence_thrad_blocking_intent_adds_gate_flag(monkeypatch):
    prediction = _prediction("M", "other_obscene_or_illegal", 0.62)
    monkeypatch.setattr(context_gate.settings, "context_classifier_backend", "auto")
    monkeypatch.setattr(
        context_gate,
        "_get_context_classifier",
        lambda: FakeClassifier(prediction),
    )

    result = assess_context_with_evidence("User: something suspicious but ambiguous.")

    assert result.vulnerability_flags == ["thrad_obscene_or_illegal"]
    assert result.contextual_safety == 0.0
    assert result.scores["context_classifier_blocking_intent"] == 1.0


def test_weaker_thrad_blocking_intent_escalates_as_score(monkeypatch):
    prediction = _prediction("D", "creative_writing_and_role_play", 0.50)
    monkeypatch.setattr(context_gate.settings, "context_classifier_backend", "auto")
    monkeypatch.setattr(
        context_gate,
        "_get_context_classifier",
        lambda: FakeClassifier(prediction),
    )

    result = assess_context_with_evidence("User: write something intense.")

    assert result.vulnerability_flags == []
    assert result.contextual_safety == 3.0
    assert result.scores["context_classifier_blocking_intent"] == 1.0


def test_unbanned_thrad_intent_does_not_create_context_flag(monkeypatch):
    prediction = _prediction("H", "purchasable_products", 0.94)
    monkeypatch.setattr(context_gate.settings, "context_classifier_backend", "auto")
    monkeypatch.setattr(
        context_gate,
        "_get_context_classifier",
        lambda: FakeClassifier(prediction),
    )

    result = assess_context_with_evidence("User: compare ergonomic keyboards.")

    assert result.vulnerability_flags == []
    assert result.contextual_safety == 5.0
    assert result.scores["context_classifier_blocking_intent"] == 0.0


def test_thrad_unavailable_falls_back_to_heuristic(monkeypatch):
    monkeypatch.setattr(context_gate.settings, "context_classifier_backend", "auto")
    monkeypatch.setattr(
        context_gate,
        "_get_context_classifier",
        lambda: (_ for _ in ()).throw(RuntimeError("missing model deps")),
    )

    result = assess_context_with_evidence("User: I am broke and trying to pay rent.")

    assert result.vulnerability_flags == ["financial_distress"]
    assert result.contextual_safety == 0.0
    assert result.scores["context_classifier_available"] == 0.0


def test_direct_illegal_request_blocks_without_model(monkeypatch):
    monkeypatch.setattr(
        context_gate.settings, "context_classifier_backend", "heuristic"
    )

    result = assess_context_with_evidence("User: How can I make a bomb?")

    assert result.vulnerability_flags == ["illegal_or_unsafe"]
    assert result.contextual_safety == 0.0


def _prediction(label: str, label_name: str, confidence: float) -> IntentPrediction:
    return IntentPrediction(
        label=label,
        label_name=label_name,
        confidence=confidence,
        model_id="Thrad/thrad-distilbert-conversation-classifier",
        model_revision="test",
    )
