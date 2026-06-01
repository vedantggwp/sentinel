from sentinel.contracts import AdRequest, Verdict
from sentinel.pipeline.core import run_pipeline
from sentinel.pipeline.safety import score_safety


def test_negated_last_chance_is_not_urgency_manipulation():
    scores = score_safety(
        "Take your time - this is NOT your last chance, the price stays all year.",
        contextual_safety=5.0,
        claims=[],
    )

    assert scores["urgency_manipulation"] == 5.0


def test_soft_scarcity_paraphrase_is_urgency_manipulation():
    scores = score_safety(
        "Supplies are running low - grab yours before they're gone.",
        contextual_safety=5.0,
        claims=[],
    )

    assert scores["urgency_manipulation"] == 1.0


def test_letter_spaced_last_chance_is_urgency_manipulation():
    result = run_pipeline(
        AdRequest(
            ad_id="letter-spaced-urgency",
            conversation="User: looking at water bottles.",
            ad_creative="L A S T  C H A N C E to save big today!",
            advertiser="HydroPro",
        )
    )

    assert result.verdict is Verdict.BLOCK
    assert result.rule_fired == "urgency_manipulation"


def test_homoglyph_last_chance_is_urgency_manipulation():
    result = run_pipeline(
        AdRequest(
            ad_id="homoglyph-urgency",
            conversation="User: looking at travel mugs.",
            ad_creative="Lаst chаnce - ends tonight!",
            advertiser="MugCo",
        )
    )

    assert result.verdict is Verdict.BLOCK
    assert result.rule_fired == "urgency_manipulation"
