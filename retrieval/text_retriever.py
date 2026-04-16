from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models import Listing


@dataclass
class TextRetrievalResult:
    listing_id: int
    similarity: float


def retrieve_by_text(
    db: Session,
    query: str,
    top_k: int=100
) -> list[TextRetrievalResult]:
    rows = db.execute(
        text("""
            SELECT id, listing_text
              FROM listings
             WHERE listing_text IS NOT NULL
               AND listing_text <> ''
        """)
    ).mappings().all()

    if not rows:
        return []

    listing_ids = [row["id"] for row in rows]
    documents = [row["listing_text"] for row in rows]

    vectoriser = TfidfVectorizer(
        stop_words="english",
        max_features=10000,
        ngram_range=(1, 2)
    )

    doc_matrix = vectoriser.fit_transform(documents)
    query_vec = vectoriser.transform([query])

    similarities = cosine_similarity(query_vec, doc_matrix).flatten()
    ranked_indices = similarities.argsort()[::-1][:top_k]

    results = []
    for i in ranked_indices:
        sim = float(similarities[i])
        if sim > 0:
            results.append(TextRetrievalResult(
                listing_id=listing_ids[i],
                similarity=sim,
            ))

    return results


def fetch_listings_by_ids(
        db: Session,
        listing_ids: list[int]) -> list[Listing]:
    if not listing_ids:
        return []

    rows = db.query(Listing).filter(Listing.id.in_(listing_ids)).all()
    row_map = {row.id: row for row in rows}

    ordered = []
    for listing_id in listing_ids:
        if listing_id in row_map:
            ordered.append(row_map[listing_id])

    return ordered