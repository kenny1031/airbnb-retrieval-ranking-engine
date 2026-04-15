from dataclasses import dataclass


@dataclass
class ParsedQuery:
    max_price: float | None = None
    min_price: float | None = None
    accommodates: int | None = None
    neighbourhood: str | None = None
    room_type: str | None = None
    wants_good_reviews: bool = False
    wants_cheap: bool = False
    wants_entire_home: bool = False


KNOWN_LOCATIONS = {
    "sydney",
    "bondi",
    "manly",
    "newtown",
    'surry hills'
}


def parse_query(query: str) -> ParsedQuery:
    q = query.lower()
    parsed = ParsedQuery()

    if "cheap" in q or "affordable" in q or "budget" in q:
        parsed.wants_cheap = True
        parsed.max_price = 250

    if "good reviews" in q or "highly rated" in q or "well reviewed" in q:
        parsed.wants_good_reviews = True

    if "entire home" in q or "entire place" in q:
        parsed.room_type = "Entire home/apt"
        parsed.wants_entire_home = True
    elif "private room" in q:
        parsed.room_type = "Private room"
    elif "shared room" in q:
        parsed.room_type = "Shared room"

    if "for two" in q or "2 guests" in q or "two guests" in q:
        parsed.accommodates = 2
    elif "for four" in q or "4 guests" in q or "four guests" in q:
        parsed.accommodates = 4
    elif "for one" in q or "1 guest" in q or "one guest" in q:
        parsed.accommodates = 1

    for loc in KNOWN_LOCATIONS:
        if loc in q:
            parsed.neighbourhood = loc.title()
            break

    return parsed