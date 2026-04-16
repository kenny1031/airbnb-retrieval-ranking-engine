from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Listing
from retrieval.parser import ParsedQuery


def generate_candidates(
    db: Session,
    parsed: ParsedQuery,
    limit: int = 200
) -> list[Listing]:
    stmt = select(Listing)

    if parsed.max_price is not None:
        stmt = stmt.where(Listing.price <= parsed.max_price)

    if parsed.min_price is not None:
        stmt = stmt.where(Listing.price >= parsed.min_price)

    if parsed.accommodates is not None:
        stmt = stmt.where(Listing.accommodates >= parsed.accommodates)

    if parsed.room_type is not None:
        stmt = stmt.where(Listing.room_type == parsed.room_type)

    if parsed.property_type is not None:
        stmt = stmt.where(Listing.property_type.ilike(f"%{parsed.property_type}%"))

    if parsed.neighbourhood is not None:
        stmt = stmt.where(Listing.neighbourhood_cleansed.ilike(f"%{parsed.neighbourhood}%"))

    stmt = stmt.limit(limit)

    return list(db.scalars(stmt).all())