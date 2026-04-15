from app.models import Listing
from retrieval.parser import ParsedQuery


def _safe_norm(value: float | None, max_value: float) -> float:
    if value is None or max_value <= 0:
        return 0.0
    return min(max(value / max_value, 0.0), 1.0)


def score_listing(listing: Listing, parsed:ParsedQuery) -> tuple[float, list[str]]:
    score = 0.0
    explanations: list[str] = []

    rating = listing.review_scores_rating or 0.0
    review_count = listing.number_of_reviews or 0
    price = listing.price or 9999.0

    rating_score = _safe_norm(rating, 100.0)
    popularity_score = _safe_norm(float(review_count), 200.0)

    score += 0.35 * rating_score
    if rating_score > 0.8:
        explanations.append("high review rating")

    score += 0.20 * popularity_score
    if popularity_score > 0.2:
        explanations.append("well reviewed")

    if parsed.wants_cheap:
        price_score = max(0.0, 1.0 - price / 300.0)
        score += 0.25 * price_score
        if price_score > 0.3:
            explanations.append("fits budget preference")

    if parsed.accommodates is not None and listing.accommodates is not None:
        if listing.accommodates >= parsed.accommodates:
            score += 0.10
            explanations.append(f"fits {parsed.accommodates} guests")

    if parsed.room_type is not None and listing.room_type == parsed.room_type:
        score += 0.10
        explanations.append("matches room type preference")

    return round(score, 4), explanations