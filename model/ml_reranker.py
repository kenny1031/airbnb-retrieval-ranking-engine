import json
from pathlib import Path
import joblib
import pandas as pd

from app.models import Listing
from model.feature_builder import build_feature_row
from retrieval.parser import ParsedQuery


MODEL_PATH = Path("model/artifacts/xgb_reranker.joblib")
FEATURES_PATH = Path("model/artifacts/xgb_feature_columns.json")

_model = None
_feature_columns = None


def load_reranker():
    global _model, _feature_columns

    if _model is None:
        _model = joblib.load(MODEL_PATH)

    if _feature_columns is None:
        with open(FEATURES_PATH, "r", encoding="utf-8") as f:
            _feature_columns = json.load(f)

    return _model, _feature_columns


def score_listing_ml(
    query: str,
    listing: Listing,
    parsed: ParsedQuery,
    text_similarity: float,
) -> float:
    model, feature_columns = load_reranker()
    row = build_feature_row(
        query=query,
        listing=listing,
        parsed=parsed,
        text_similarity=text_similarity,
    )

    feature_dict = {col: row[col] for col in feature_columns}
    X = pd.DataFrame([feature_dict], columns=feature_columns)

    prob = model.predict_proba(X)[0, 1]
    return float(prob)