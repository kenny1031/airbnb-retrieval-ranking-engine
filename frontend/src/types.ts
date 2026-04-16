export type SearchResultItem = {
  listing_id: number;
  name: string | null;
  neighbourhood_cleansed: string | null;
  room_type: string | null;
  property_type: string | null;
  price: number | null;
  review_scores_rating: number | null;
  number_of_reviews: number | null;
  ranking_score: number;
  explanations: string[];
};

export type SearchResponse = {
  query: string;
  results: SearchResultItem[];
};