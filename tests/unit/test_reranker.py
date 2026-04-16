from types import SimpleNamespace

from retrieval.parser import ParsedQuery
from retrieval.reranker import score_listing


def make_listing(**overrides):
    base = {
        "id": 1,
        "name": "Test Listing",
        "neighbourhood_cleansed": "Sydney",
        "room_type": "Entire home/apt",
        "property_type": "Apartment",
        "price": 120.0,
        "review_scores_rating": 95.0,
        "number_of_reviews": 80,
        "accommodates": 2,
        "cancellation_policy": "flexible",
        "instant_bookable": "t",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_score_listing_returns_non_null_score():
    parsed = ParsedQuery(
        wants_cheap=True,
        accommodates=2,
        neighbourhood="Sydney",
        property_type="Apartment",
        prefers_entire_home=True,
    )
    listing = make_listing()
    score, explanations = score_listing(listing, parsed, text_similarity=0.2)

    assert isinstance(score, float)
    assert score > 0
    assert len(explanations) > 0


def test_score_listing_rewards_property_type_match():
    parsed = ParsedQuery(property_type="Apartment")

    matching_listing = make_listing(property_type="Apartment")
    non_matching_listing = make_listing(property_type="House")

    matching_score, _ = score_listing(matching_listing, parsed, text_similarity=0.0)
    non_matching_score, _ = score_listing(non_matching_listing, parsed, text_similarity=0.0)

    assert matching_score > non_matching_score


def test_score_listing_rewards_location_match():
    parsed = ParsedQuery(neighbourhood="Sydney")

    matching_listing = make_listing(neighbourhood_cleansed="Sydney")
    non_matching_listing = make_listing(neighbourhood_cleansed="Manly")

    matching_score, _ = score_listing(matching_listing, parsed, text_similarity=0.0)
    non_matching_score, _ = score_listing(non_matching_listing, parsed, text_similarity=0.0)

    assert matching_score > non_matching_score


def test_score_listing_rewards_room_type_match():
    parsed = ParsedQuery(room_type="Private room")

    matching_listing = make_listing(room_type="Private room")
    non_matching_listing = make_listing(room_type="Entire home/apt")

    matching_score, _ = score_listing(matching_listing, parsed, text_similarity=0.0)
    non_matching_score, _ = score_listing(non_matching_listing, parsed, text_similarity=0.0)

    assert matching_score > non_matching_score


def test_score_listing_handles_missing_values():
    parsed = ParsedQuery(wants_cheap=True, accommodates=2)
    listing = make_listing(
        review_scores_rating=None,
        number_of_reviews=None,
        price=None,
        accommodates=None,
    )
    score, explanations = score_listing(listing, parsed, text_similarity=0.0)

    assert isinstance(score, float)
    assert score >= 0
    assert explanations is not None


def test_score_listing_rewards_text_similarity():
    parsed = ParsedQuery()
    listing = make_listing()
    low_score, _ = score_listing(listing, parsed, text_similarity=0.0)
    high_score, _ = score_listing(listing, parsed, text_similarity=0.4)

    assert high_score > low_score