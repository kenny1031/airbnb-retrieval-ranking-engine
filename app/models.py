from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Float, Integer, BigInteger, Text


class Base(DeclarativeBase):
    pass


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    neighbourhood_cleansed: Mapped[str | None] = mapped_column(Text, nullable=True)

    property_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    room_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    amenities: Mapped[str | None] = mapped_column(Text, nullable=True)

    accommodates: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bathrooms: Mapped[float | None] = mapped_column(Float, nullable=True)
    bedrooms: Mapped[float | None] = mapped_column(Float, nullable=True)
    beds: Mapped[float | None] = mapped_column(Float, nullable=True)

    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    minimum_nights: Mapped[int | None] = mapped_column(Integer, nullable=True)
    availability_365: Mapped[int | None] = mapped_column(Integer, nullable=True)
    number_of_reviews: Mapped[int | None] = mapped_column(Integer, nullable=True)
    review_scores_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    reviews_per_month: Mapped[float | None] = mapped_column(Float, nullable=True)

    cancellation_policy: Mapped[str | None] = mapped_column(Text, nullable=True)
    instant_bookable: Mapped[str | None] = mapped_column(Text, nullable=True)

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)