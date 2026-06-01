from sentinel.pipeline.claims import extract_claims


def test_limited_availability_claim_is_extracted_without_tail_copy():
    claims = extract_claims("LAST CHANCE - only 2 policies left at this price!!!")

    assert ("only 2 policies left", "availability") in [
        (claim.text, claim.type) for claim in claims
    ]


def test_limited_availability_extraction_uses_bounded_window():
    creative = "only 1 " + (" " * 10_000) + "left"

    assert extract_claims(creative) == []


def test_limited_availability_requires_only_as_a_word():
    claims = extract_claims("This lonely 2 policies left phrase is not scarcity.")

    assert claims == []
