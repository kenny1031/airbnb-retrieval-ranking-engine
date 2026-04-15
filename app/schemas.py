from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)


class SearchResultItem(BaseModel):
    listing_id: int
    name: str | None
    neighbourhood_cleased: str | None
    room_type: str | None
    property_type: str | None
    price: float | None
    review_scores_rating: float | None
    number_of_reviews: int | None
    ranking_score: float
    explanations: list[str]


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]