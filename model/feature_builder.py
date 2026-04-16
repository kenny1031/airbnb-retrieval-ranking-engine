import math
from app.models import Listing
from retrieval.parser import ParsedQuery
from retrieval.reranker import score_listing


# Feature value criterions
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


def _price_fit(price: float | None, wants_cheap: bool) -> float:
    price = _clean_float(price, 9999.0)
    if not wants_cheap:
        return 0.5
    return max(0.0, 1.0 - price/300.0)

def _accommodates_fit(listing: Listing, target: int | None) -> float:
    if target is None:
        return 0.5
    accommodates = _clean_float(getattr(listing, "accommodates", None), 0.0)
    return 1.0 if accommodates >= target else 0.0

def _location_match(listing: Listing, neighbourhood: str | None) -> float:
    if neighbourhood is None:
        return 0.5
    value = getattr(listing, "neighbourhood_cleansed", None)
    if value and neighbourhood.lower() in value.lower():
        return 1.0
    return 0.0


def _property_type_match(listing: Listing, property_type: str | None) -> float:
    if property_type is None:
        return 0.5
    value = getattr(listing, "property_type", None)
    if value and property_type.lower() in value.lower():
        return 1.0
    return 0.0

def _room_type_match(listing: Listing, room_type: str | None) -> float:
    if room_type is None:
        return 0.5
    value = getattr(listing, "room_type", None)
    return 1.0 if value == room_type else 0.0


def _flexible_cancellation_match(listing: Listing, wants_flexible: bool) -> float:
    if not wants_flexible:
        return 0.5
    value = getattr(listing, "cancellation_policy", None)
    if value and "flexible" in value.lower():
        return 1.0
    return 0.0


def _instant_bookable_match(listing: Listing, wants_instant: bool) -> float:
    if not wants_instant:
        return 0.5
    value = getattr(listing, "instant_bookable", None)
    if value and value.lower() == "t":
        return 1.0
    return 0.0


def _preferred_entire_home_match(listing: Listing, prefers_entire_home: bool) -> float:
    if not prefers_entire_home:
        return 0.5
    value = getattr(listing, "room_type", None)
    return 1.0 if value == "Entire home/apt" else 0.0


def _wifi_match(listing: Listing, wants_wifi: bool) -> float:
    if not wants_wifi:
        return 0.5
    amenities = getattr(listing, "amenities", None)
    if amenities and "wifi" in amenities.lower():
        return 1.0
    return 0.0


def _family_home_match(listing: Listing, wants_family_friendly: bool) -> float:
    if not wants_family_friendly:
        return 0.5

    room_type = getattr(listing, "room_type", None) or ""
    property_type = getattr(listing, "property_type", None) or ""
    accommodates = _clean_float(getattr(listing, "accommodates", None), 0.0)

    score = 0.0
    if room_type == "Entire home/apt":
        score += 0.4
    if property_type in {"House", "Apartment", "Townhouse", "Villa"}:
        score += 0.3
    if accommodates >= 4:
        score += 0.3

    return min(score, 1.0)


# Building function
def build_feature_row(
    query: str,
    listing: Listing,
    parsed: ParsedQuery,
    text_similarity: float,
) -> dict:
    rule_score, _ = score_listing(
        listing=listing,
        parsed=parsed,
        text_similarity=text_similarity,
    )

    rating = _clean_float(getattr(listing, "review_scores_rating", None), 0.0)
    review_count = _clean_float(getattr(listing, "number_of_reviews", None), 0.0)
    price = _clean_float(getattr(listing, "price", None), 9999.0)
    reviews_per_month = _clean_float(getattr(listing, "reviews_per_month", None), 0.0)
    availability_365 = _clean_float(getattr(listing, "availability_365", None), 0.0)

    return {
        "query": query,
        "listing_id": getattr(listing, "id"),
        "text_similarity": float(text_similarity),
        "rating": rating,
        "rating_norm": _safe_norm(rating, 100.0),
        "review_count": review_count,
        "review_count_norm": _safe_norm(review_count, 500.0),
        "reviews_per_month": reviews_per_month,
        "reviews_per_month_norm": _safe_norm(reviews_per_month, 10.0),
        "availability_365": availability_365,
        "availability_365_norm": _safe_norm(availability_365, 365.0),
        "price": price,
        "price_norm": min(price / 1000.0, 1.0),
        "price_fit": _price_fit(price, parsed.wants_cheap),
        "accommodates_fit": _accommodates_fit(listing, parsed.accommodates),
        "location_match": _location_match(listing, parsed.neighbourhood),
        "property_type_match": _property_type_match(listing, parsed.property_type),
        "room_type_match": _room_type_match(listing, parsed.room_type),
        "flexible_cancellation_match": _flexible_cancellation_match(
            listing, parsed.wants_flexible_cancellation
        ),
        "instant_bookable_match": _instant_bookable_match(
            listing, parsed.wants_instant_bookable
        ),
        "wifi_match": _wifi_match(listing, parsed.wants_wifi),
        "family_home_match": _family_home_match(
            listing, parsed.wants_family_friendly
        ),
        "query_wants_wifi": int(parsed.wants_wifi),
        "query_wants_family_friendly": int(parsed.wants_family_friendly),
        "preferred_entire_home_match": _preferred_entire_home_match(
            listing, parsed.prefers_entire_home
        ),
        "query_wants_cheap": int(parsed.wants_cheap),
        "query_wants_good_reviews": int(parsed.wants_good_reviews),
        "query_wants_flexible_cancellation": int(parsed.wants_flexible_cancellation),
        "query_wants_instant_bookable": int(parsed.wants_instant_bookable),
        "query_prefers_entire_home": int(parsed.prefers_entire_home),
        "rule_score": rule_score,
    }