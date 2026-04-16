from sqlalchemy import create_engine, text
from app.config import settings


def clean_part(value: str | None) -> str:
    if value is None:
        return ""
    value = str(value).strip()
    return value if value else ""


def build_listing_text(row: dict) -> str:
    parts = [
        clean_part(row.get("name")),
        clean_part(row.get("summary")),
        clean_part(row.get("description")),
        f"Location: {clean_part(row.get('neighbourhood_cleansed'))}",
        f"Property type: {clean_part(row.get('property_type'))}",
        f"Room type: {clean_part(row.get('room_type'))}",
        f"Amenities: {clean_part(row.get('amenities'))}"
    ]
    return " ".join(part for part in parts if part).strip()


def main():
    engine = create_engine(settings.db_url, echo=False)
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT id, name, summary, description,
                   neighbourhood_cleansed, property_type,
                   room_type, amenities
            FROM listings 
        """)).mappings().all()

        updates = []
        for row in rows:
            listing_text = build_listing_text(dict(row))
            updates.append({
                "id": row["id"],
                "listing_text": listing_text
            })

        conn.execute(
            text("""
                UPDATE listings
                SET listing_text = :listing_text
                WHERE id = :id
            """),
            updates
        )
    print(f"Updated listing_text for {len(updates)} listings.")


if __name__ == "__main__":
    main()