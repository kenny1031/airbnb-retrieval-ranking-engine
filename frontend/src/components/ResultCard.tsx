import type { SearchResultItem } from "../types";

type ResultCardProps = {
  item: SearchResultItem;
};

export default function ResultCard({ item }: ResultCardProps) {
  return (
    <article
      style={{
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: 16,
        padding: 20,
        boxShadow: "0 8px 24px rgba(0,0,0,0.04)",
      }}
    >
      <h3
        style={{
          margin: "0 0 10px",
          fontSize: 22,
          lineHeight: 1.2,
          textAlign: "center",
        }}
      >
        {item.name ?? "Untitled listing"}
      </h3>

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 8,
          marginBottom: 12,
          color: "#4b5563",
          fontSize: 14,
        }}
      >
        <span>{item.neighbourhood_cleansed ?? "Unknown area"}</span>
        <span>•</span>
        <span>{item.room_type ?? "Unknown room type"}</span>
        <span>•</span>
        <span>{item.property_type ?? "Unknown property type"}</span>
      </div>

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 16,
          marginBottom: 14,
          fontSize: 15,
        }}
      >
        <span>
          <strong>Price:</strong> {item.price !== null ? `$${item.price}` : "N/A"}
        </span>
        <span>
          <strong>Rating:</strong> {item.review_scores_rating ?? "N/A"}
        </span>
        <span>
          <strong>Reviews:</strong> {item.number_of_reviews ?? "N/A"}
        </span>
        <span>
          <strong>Relevance:</strong> {item.ranking_score.toFixed(4)}
        </span>
      </div>

      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 8,
        }}
      >
        {item.explanations.map((exp) => (
          <span
            key={exp}
            style={{
              background: "#eef2ff",
              color: "#3730a3",
              borderRadius: 999,
              padding: "6px 10px",
              fontSize: 13,
              fontWeight: 600,
            }}
          >
            {exp}
          </span>
        ))}
      </div>
    </article>
  );
}