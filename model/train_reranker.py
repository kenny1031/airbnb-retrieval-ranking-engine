from pathlib import Path
import json
import joblib
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import (
    classification_report,
    average_precision_score,
    roc_auc_score
)
from sklearn.model_selection import train_test_split


DATA_PATH = "model/artifacts/training_data.csv"
MODEL_PATH = "model/artifacts/xgb_reranker.joblib"
METRICS_PATH = "model/artifacts/xgb_reranker_metrics.json"
FEATURES_PATH = "model/artifacts/xgb_feature_columns.json"

DROP_COLUMNS = ["query", "listing_id", "rule_score", "label"]


def main():
    df = pd.read_csv(DATA_PATH)

    feature_cols = [col for col in df.columns if col not in DROP_COLUMNS]
    X = df[feature_cols]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pos_count = int((y_train == 1).sum())
    neg_count = int((y_train == 0).sum())
    scale_pos_weight = neg_count / max(pos_count, 1)

    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42,
        scale_pos_weight=scale_pos_weight,
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    report = classification_report(y_test, y_pred, output_dict=True)
    pr_auc = average_precision_score(y_test, y_prob)
    roc_auc = roc_auc_score(y_test, y_prob)

    metrics = {
        "num_rows": int(len(df)),
        "num_features": int(len(feature_cols)),
        "positive_rate": float(y.mean()),
        "train_positive_count": pos_count,
        "train_negative_count": neg_count,
        "scale_pos_weight": float(scale_pos_weight),
        "average_precision": float(pr_auc),
        "roc_auc": float(roc_auc),
        "classification_report": report,
    }

    Path(MODEL_PATH).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    with open(FEATURES_PATH, "w", encoding="utf-8") as f:
        json.dump(feature_cols, f, indent=2)

    print("Saved model to", MODEL_PATH)
    print("Saved metrics to", METRICS_PATH)
    print("Saved feature columns to", FEATURES_PATH)
    print("\nAverage Precision:", pr_auc)
    print("ROC AUC:", roc_auc)
    print()
    print(classification_report(y_test, y_pred))

if __name__ == "__main__":
    main()