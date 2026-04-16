DROP TABLE IF EXISTS listings;

CREATE TABLE listings (
    id BIGINT PRIMARY KEY,
    name TEXT,
    summary TEXT,
    description TEXT,
    neighbourhood_cleansed TEXT,
    property_type TEXT,
    room_type TEXT,
    amenities TEXT,
    accommodates INT,
    bathrooms FLOAT,
    bedrooms FLOAT,
    beds FLOAT,
    price FLOAT,
    minimum_nights INT,
    availability_365 INT,
    number_of_reviews INT,
    review_scores_rating FLOAT,
    reviews_per_month FLOAT,
    cancellation_policy TEXT,
    instant_bookable TEXT,
    latitude FLOAT,
    longitude FLOAT
);

ALTER TABLE listings
ADD COLUMN IF NOT EXISTS listing_text TEXT;