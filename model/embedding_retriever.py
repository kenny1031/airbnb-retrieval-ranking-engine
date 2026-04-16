import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from app.models import Listing
from config.runtime_config import get_embedding_config


emb_cfg = get_embedding_config()

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_NAME = emb_cfg["model_name"]
DEFAULT_TOP_K = emb_cfg["top_k"]
EMBEDDINGS_PATH = BASE_DIR / "model" / "artifacts" / "listing_embeddings.npy"
IDS_PATH = BASE_DIR / "model" / "artifacts" / "listing_embedding_ids.json"

_model = SentenceTransformer(MODEL_NAME)
_listing_embeddings = np.load(EMBEDDINGS_PATH)
with open(IDS_PATH, "r", encoding="utf-8") as f:
    _listing_ids = json.load(f)


def retrieve_by_embedding(query: str, top_k: int | None=None) -> list[tuple[int, float]]:
    query_embedding = _model.encode(
        [query],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]
    if top_k is None:
        top_k = DEFAULT_TOP_K

    similarities = _listing_embeddings @ query_embedding
    ranked_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in ranked_indices:
        score = float(similarities[idx])
        if score > 0:
            results.append((int(_listing_ids[idx]), score))

    return results


def fetch_listings_by_ids(db: Session, listing_ids: list[int]) -> list[Listing]:
    if not listing_ids:
        return []

    rows = db.query(Listing).filter(Listing.id.in_(listing_ids)).all()
    row_map = {row.id: row for row in rows}

    ordered = []
    for listing_id in listing_ids:
        if listing_id in row_map:
            ordered.append(row_map[listing_id])
    return ordered