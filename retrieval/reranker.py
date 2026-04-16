import math
from app.models import Listing
from retrieval.parser import ParsedQuery


def _clean_float(value: float | None, default: float=0.0) -> float:
    if value is None:
        return default
    if isinstance(value, float) and math.isnan(value):
        return default
    return float(value)

def _safe_norm(value: float | None, max_value: float) -> float:
    value = _clean_float(value, 0.0)
    if max_value <= 0:
        return 0.0
    return min(max(value / max_value, 0.0), 1.0)


def score_listing(
    listing: Listing,
    parsed: ParsedQuery,
    text_similarity: float = 0.0
) -> tuple[float, list[str]]:
    score = 0.0
    explanations: list[str] = []

    rating = _clean_float(listing.review_scores_rating, 0.0)
    review_count = int(_clean_float(listing.number_of_reviews, 0.0))
    price = _clean_float(listing.price, 9999.0)

    rating_score = _safe_norm(rating, 100.0)
    popularity_score = _safe_norm(float(review_count), 500.0)
    semantic_score = min(max(text_similarity, 0.0), 1.0)

    score += 0.20 * rating_score
    if rating_score > 0.8:
        explanations.append("high review rating")

    score += 0.10 * popularity_score
    if popularity_score > 0.1:
        explanations.append("well reviewed")

    score += 0.20 * semantic_score
    if semantic_score > 0.05:
        explanations.append("strong text-query relevance")

    if parsed.wants_cheap:
        price_score = max(0.0, 1.0 - price / 300.0)
        score += 0.20 * price_score
        if price_score > 0.3:
            explanations.append("within budget preference")

    if parsed.accommodates is not None:
        accommodates = _clean_float(listing.accommodates, 0.0)
        if accommodates >= parsed.accommodates:
            score += 0.15
            explanations.append(f"fits {parsed.accommodates} guests")

    if parsed.neighbourhood is not None and listing.neighbourhood_cleansed:
        if parsed.neighbourhood.lower() in listing.neighbourhood_cleansed.lower():
            score += 0.10
            explanations.append("matches location preference")

    if parsed.room_type is not None and listing.room_type == parsed.room_type:
        score += 0.05
        explanations.append("matches room type preference")

    if parsed.property_type is not None and listing.property_type:
        if parsed.property_type.lower() in listing.property_type.lower():
            score += 0.05
            explanations.append("matches property type preference")

    if getattr(parsed, "prefers_entire_home", False) and listing.room_type == "Entire home/apt":
        score += 0.05
        explanations.append("preferred entire place")

    if parsed.wants_flexible_cancellation and listing.cancellation_policy:
        if "flexible" in listing.cancellation_policy.lower():
            score += 0.05
            explanations.append("flexible cancellation")

    if parsed.wants_instant_bookable and listing.instant_bookable:
        if listing.instant_bookable.lower() == "t":
            score += 0.05
            explanations.append("instant bookable")

    score = _clean_float(score, 0.0)
    return round(score, 4), explanations