from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.runtime_config import get_ranking_config
from app.dependencies import get_db
from app.schemas import SearchRequest, SearchResponse, SearchResultItem
from model.embedding_retriever import retrieve_by_embedding, fetch_listings_by_ids
from model.ml_reranker import score_listing_ml
from retrieval.parser import parse_query
from retrieval.candidate_generator import generate_candidates
from retrieval.reranker import score_listing

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search_listings(
    payload: SearchRequest,
    db: Session = Depends(get_db)
) -> SearchResponse:
    parsed = parse_query(payload.query)

    embedding_hits = retrieve_by_embedding(payload.query, top_k=100)
    embedding_ids = [listing_id for listing_id, _ in embedding_hits]
    similarity_map = {listing_id: sim for listing_id, sim in embedding_hits}

    structured_candidates = generate_candidates(db, parsed, limit=100)
    structured_ids = [listing.id for listing in structured_candidates]

    merged_ids = []
    seen = set()
    for listing_id in embedding_ids + structured_ids:
        if listing_id not in seen:
            seen.add(listing_id)
            merged_ids.append(listing_id)

    candidates = fetch_listings_by_ids(db, merged_ids)

    ranked = []
    for listing in candidates:
        text_similarity = similarity_map.get(listing.id, 0.0)

        ml_score = score_listing_ml(
            query=payload.query,
            listing=listing,
            parsed=parsed,
            text_similarity=text_similarity,
        )

        rule_score, explanations = score_listing(
            listing=listing,
            parsed=parsed,
            text_similarity=text_similarity,
        )

        ranking_cfg = get_ranking_config()
        final_score = (
            ranking_cfg["ml_weight"] * ml_score
            + ranking_cfg["rule_weight"] * rule_score
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
                ranking_score=round(final_score, 4),
                explanations=explanations,
            )
        )

    ranked.sort(key=lambda x: x.ranking_score, reverse=True)
    return SearchResponse(query=payload.query, results=ranked[:payload.top_k])