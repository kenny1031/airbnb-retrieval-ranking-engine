import argparse
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session
from config.runtime_config import get_training_data_config
from app.db import SessionLocal
from model.feature_builder import build_feature_row
from model.embedding_retriever import (
    retrieve_by_embedding,
    fetch_listings_by_ids
)
from retrieval.candidate_generator import generate_candidates
from retrieval.parser import parse_query


training_cfg = get_training_data_config()

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_QUERIES_PATH = BASE_DIR / "model" / "queries.txt"
DEFAULT_OUTPUT_PATH = BASE_DIR / "model" / "artifacts" / "training_data.csv"


# Helpers
def load_queries(path: str) -> list[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    queries = [line.strip() for line in lines if line.strip()]
    if not queries:
        raise ValueError("No queries found in queries file")
    return queries

def merge_candidate_ids(
        text_ids: list[int],
        structured_ids: list[int]) -> list[int]:
    merged: list[int] = []
    seen: set[int] = set()

    for listing_id in text_ids + structured_ids:
        if listing_id not in seen:
            seen.add(listing_id)
            merged.append(listing_id)

    return merged

def make_label(rule_score: float) -> int:
    return 1 if rule_score >= training_cfg["positive_label_threshold"] else 0


def build_rows_for_query(db: Session, query: str) -> list[dict]:
    parsed = parse_query(query)

    embedding_hits = retrieve_by_embedding(query, top_k=100)
    embedding_ids = [listing_id for listing_id, _ in embedding_hits]
    similarity_map = {listing_id: sim for listing_id, sim in embedding_hits}

    structured_candidates = generate_candidates(db, parsed, limit=100)
    structured_ids = [listing.id for listing in structured_candidates]

    merged_ids = merge_candidate_ids(embedding_ids, structured_ids)
    listings = fetch_listings_by_ids(db, merged_ids)

    rows: list[dict] = []
    for listing in listings:
        row = build_feature_row(
            query=query,
            listing=listing,
            parsed=parsed,
            text_similarity=similarity_map.get(listing.id, 0.0),
        )
        row["label"] = make_label(row["rule_score"])
        rows.append(row)

    return rows


def main(queries_path: str, output_path: str) -> None:
    queries = load_queries(queries_path)

    all_rows: list[dict] = []
    db = SessionLocal()
    try:
        for query in queries:
            rows = build_rows_for_query(db, query)
            all_rows.extend(rows)
            print(f"Built {len(rows)} rows for query: {query}")
    finally:
        db.close()

    if len(all_rows) == 0:
        raise ValueError("No training rows were generated")

    df = pd.DataFrame(all_rows)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)

    print(f"Saved {len(df)} rows to {output}")
    print(df["label"].value_counts(dropna=False).sort_index())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", default=DEFAULT_QUERIES_PATH)
    parser.add_argument("--output", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()
    main(args.queries, args.output)