import argparse
import math
import pandas as pd
from sqlalchemy import create_engine, text

from app.config import settings


CSV_PATH = "data/raw/listings_dec18.csv"

REQUIRED_COLUMNS = [
    "id",
    "name",
    "summary",
    "description",
    "neighbourhood_cleansed",
    "property_type",
    "room_type",
    "amenities",
    "accommodates",
    "bathrooms",
    "bedrooms",
    "beds",
    "price",
    "minimum_nights",
    "availability_365",
    "number_of_reviews",
    "review_scores_rating",
    "reviews_per_month",
    "cancellation_policy",
    "instant_bookable",
    "latitude",
    "longitude",
]


def clean_numeric(value):
    if pd.isna(value):
        return None
    if isinstance(value, str):
        value = (
            value.replace("$", "")
            .replace(",", "")
            .strip()
        )
        if value == "":
            return None
        return value
    try:
        value = float(value)
        if math.isnan(value):
            return None
        return value
    except (TypeError, ValueError):
        return None

def clean_int(value):
    numeric = clean_numeric(value)
    return None if numeric is None else int(numeric)

def clean_text(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    return value if value else None


def main(csv_path: str):
    df = pd.read_csv(csv_path)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[REQUIRED_COLUMNS].copy()
    df["id"] = df["id"].astype("int64")

    text_cols = [
        "name",
        "summary",
        "description",
        "neighbourhood_cleansed",
        "property_type",
        "room_type",
        "amenities",
        "cancellation_policy",
        "instant_bookable",
    ]

    for col in text_cols:
        df[col] = df[col].apply(clean_text)

    int_cols = [
        "accommodates",
        "minimum_nights",
        "availability_365",
        "number_of_reviews",
    ]

    for col in int_cols:
        df[col] = df[col].apply(clean_int)

    float_cols = [
        "bathrooms",
        "bedrooms",
        "beds",
        "price",
        "review_scores_rating",
        "reviews_per_month",
        "latitude",
        "longitude",
    ]

    for col in float_cols:
        df[col] = df[col].apply(clean_numeric)

    records = df.to_dict(orient="records")
    engine = create_engine(settings.db_url, echo=False)

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM listings"))
        insert_sql = text("""
            INSERT INTO listings (
                id, name, summary, description, neighbourhood_cleansed,
                property_type, room_type, amenities,
                accommodates, bathrooms, bedrooms, beds,
                price, minimum_nights, availability_365,
                number_of_reviews, review_scores_rating, reviews_per_month,
                cancellation_policy, instant_bookable,
                latitude, longitude
            )
            VALUES (
                :id, :name, :summary, :description, :neighbourhood_cleansed,
                :property_type, :room_type, :amenities,
                :accommodates, :bathrooms, :bedrooms, :beds,
                :price, :minimum_nights, :availability_365,
                :number_of_reviews, :review_scores_rating, :reviews_per_month,
                :cancellation_policy, :instant_bookable,
                :latitude, :longitude
            )
        """)
        conn.execute(insert_sql, records)

    print(f"Loaded {len(records)} listings into PostgreSQL.")

# Launch pgsql in terminal
# psql -h 127.0.0.1 -p 55432 -U airbnb -d airbnb
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/raw/listings_dec18.csv")
    args = parser.parse_args()
    main(args.csv)