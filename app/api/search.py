from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas import SearchRequest, SearchResponse, SearchResultItem
from retrieval.parser import parse_query
from retrieval.candidate_generator import generate_candidates
from retrieval.reranker import score_listing

router = APIRouter()

@router.post("/search", response_model=SearchResponse)
def search_listings(payload: SearchRequest,
                    db: Session = Depends(get_db)) -> SearchResponse:
    parsed = parse_query(payload.query)
    candidates = generate_candidates(db, parsed, limit=200)

    ranked = []
    for listing in candidates:
        score, explanations = score_listing(listing, parsed)
        ranked.append(
            SearchResultItem(
                listing_id=listing.id,
                name=listing.name,
                neighbourhood_cleased=listing.neighbourhood_cleansed,
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