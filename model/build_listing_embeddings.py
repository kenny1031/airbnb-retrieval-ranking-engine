# Offline embedding
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from app.db import SessionLocal
from config.runtime_config import get_embedding_config


emb_cfg = get_embedding_config()

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_NAME = emb_cfg["model_name"]
EMBEDDINGS_PATH = BASE_DIR / "model" / "artifacts" / "listing_embeddings.npy"
IDS_PATH = BASE_DIR / "model" / "artifacts" / "listing_embedding_ids.json"
MODEL_INFO_PATH = BASE_DIR / "model" / "artifacts" / "listing_embedding_model.txt"


def main():
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT id, listing_text
                  FROM listings
                 WHERE listing_text IS NOT NULL
                   AND listing_text <> ''
                 ORDER BY id
            """)
        ).mappings().all()
    finally:
        db.close()

    if not rows:
        raise ValueError("No listing_text rows found.")

    listing_ids = [int(row["id"]) for row in rows]
    texts = [row["listing_text"] for row in rows]

    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(
        texts,
        batch_size=emb_cfg["batch_size"],
        show_progress_bar=True,
        normalize_embeddings=emb_cfg["normalize_embeddings"],
    )

    EMBEDDINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.save(EMBEDDINGS_PATH, embeddings)

    with open(IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(listing_ids, f)

    MODEL_INFO_PATH.write_text(MODEL_NAME, encoding="utf-8")

    print(f"Saved embeddings: {EMBEDDINGS_PATH}")
    print(f"Saved ids: {IDS_PATH}")
    print(f"Saved model info: {MODEL_INFO_PATH}")
    print(f"Embedding matrix shape: {embeddings.shape}")


if __name__ == "__main__":
    main()