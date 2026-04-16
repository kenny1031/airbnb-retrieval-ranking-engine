from dataclasses import dataclass


@dataclass
class ParsedQuery:
    max_price: float | None = None
    min_price: float | None = None
    accommodates: int | None = None
    neighbourhood: str | None = None

    room_type: str | None = None
    property_type: str | None = None

    wants_good_reviews: bool = False
    wants_cheap: bool = False
    wants_flexible_cancellation: bool = False
    wants_instant_bookable: bool = False
    prefers_entire_home: bool = False


LOCATION_ALIASES = {
    "bondi beach": "Waverley",
    "bondi": "Waverley",
    "coogee": "Randwick",
    "redfern": "Sydney",
    "camperdown": "Sydney",
    "surry hills": "Sydney",
    "newtown": "Sydney",
    "manly": "Manly",
    "north sydney": "North Sydney",
    "marrickville": "Marrickville",
    "woollahra": "Woollahra",
    "mosman": "Mosman",
    "leichhardt": "Leichhardt",
    "randwick": "Randwick",
    "waverley": "Waverley",
    "sydney": "Sydney",
}

PROPERTY_TYPE_KEYWORDS = {
    "apartment": "Apartment",
    "house": "House",
    "townhouse": "Townhouse",
    "loft": "Loft",
    "villa": "Villa",
    "studio": "Apartment",
}

ROOM_TYPE_KEYWORDS = {
    "entire home": "Entire home/apt",
    "entire place": "Entire home/apt",
    "private room": "Private room",
    "shared room": "Shared room",
}


def parse_query(query: str) -> ParsedQuery:
    q = query.lower()
    parsed = ParsedQuery()

    if "cheap" in q or "affordable" in q or "budget" in q:
        parsed.wants_cheap = True
        parsed.max_price = 250

    if "good reviews" in q or "highly rated" in q or "well reviewed" in q:
        parsed.wants_good_reviews = True

    if "flexible cancellation" in q or "flexible" in q:
        parsed.wants_flexible_cancellation = True

    if "instant bookable" in q or "instant booking" in q:
        parsed.wants_instant_bookable = True

    for phrase, canonical in ROOM_TYPE_KEYWORDS.items():
        if phrase in q:
            parsed.room_type = canonical
            break

    for phrase, canonical in PROPERTY_TYPE_KEYWORDS.items():
        if phrase in q:
            parsed.property_type = canonical
            if canonical == "Apartment" and parsed.room_type is None:
                parsed.prefers_entire_home = True
            break

    if "for one" in q or "1 guest" in q or "one guest" in q:
        parsed.accommodates = 1
    elif "for two" in q or "2 guests" in q or "two guests" in q:
        parsed.accommodates = 2
    elif "for three" in q or "3 guests" in q or "three guests" in q:
        parsed.accommodates = 3
    elif "for four" in q or "4 guests" in q or "four guests" in q:
        parsed.accommodates = 4

    for phrase, canonical in LOCATION_ALIASES.items():
        if phrase in q:
            parsed.neighbourhood = canonical
            break

    return parsed