from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas import SearchRequest, SearchResponse, SearchResultItem

from retrieval.parser import parse_query
from retrieval.candidate_generator import generate_candidates
from retrieval.reranker import score_listing
from retrieval.text_retriever import retrieve_by_text, fetch_listings_by_ids
router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search_listings(
    payload: SearchRequest,
    db: Session = Depends(get_db)
) -> SearchResponse:
    parsed = parse_query(payload.query)

    text_hits = retrieve_by_text(db, payload.query, top_k=100)
    text_ids = [hit.listing_id for hit in text_hits]
    similarity_map = {hit.listing_id: hit.similarity for hit in text_hits}

    structured_candidates = generate_candidates(db, parsed, limit=100)
    structured_ids = [listing.id for listing in structured_candidates]

    merged_ids = []
    seen = set()
    for listing_id in text_ids + structured_ids:
        if listing_id not in seen:
            seen.add(listing_id)
            merged_ids.append(listing_id)

    candidates = fetch_listings_by_ids(db, merged_ids)

    ranked = []
    for listing in candidates:
        score, explanations = score_listing(
            listing,
            parsed,
            text_similarity=similarity_map.get(listing.id, 0.0)
        )
        ranked.append(
            SearchResultItem(
                listing_id=listing.id,
                name=listing.name,
                neighbourhood_cleansed=listing.neighbourhood_cleansed,
                room_type=listing.room_type,
                property_type=listing.property_type,
                price=listing.price,
                review_scores_rating=listing.review_scores_rating,
                number_of_reviews=listing.number_of_reviews,
                ranking_score=score,
                explanations=explanations,
            )
        )

    ranked.sort(key=lambda x: x.ranking_score, reverse=True)
    return SearchResponse(query=payload.query, results=ranked[:payload.top_k])