import { useState } from "react";
import SearchBar from "./components/SearchBar";
import ResultCard from "./components/ResultCard";
import type { SearchResponse, SearchResultItem } from "./types";

const exampleQueries = [
  "cheap apartment for two in Sydney with good reviews",
  "private room near Bondi beach",
  "entire home in Manly with wifi",
];

export default function App() {
  const [query, setQuery] = useState(exampleQueries[0]);
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query,
          top_k: 5,
        }),
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`HTTP ${response.status}: ${text}`);
      }

      const data: SearchResponse = await response.json();
      setResults(data.results);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Unknown error");
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f7f7fb",
        color: "#1f2937",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
      }}
    >
      <div
        style={{
          maxWidth: 1200,
          margin: "0 auto",
          padding: "48px 20px 64px",
        }}
      >
        <header style={{ marginBottom: 32, textAlign: "center" }}>
          <h1
            style={{
              fontSize: 40,
              lineHeight: 1.1,
              margin: "0 0 12px",
              fontWeight: 800,
            }}
          >
            Airbnb Retrieval Ranking Engine
          </h1>
          <p
            style={{
              margin: 0,
              fontSize: 18,
              color: "#4b5563",
            }}
          >
            Natural-language retrieval and ranking for Airbnb listings.
          </p>
        </header>

        <SearchBar
          query={query}
          setQuery={setQuery}
          onSearch={handleSearch}
          loading={loading}
          exampleQueries={exampleQueries}
        />

        {error && (
          <div
            style={{
              marginBottom: 20,
              background: "#fef2f2",
              color: "#991b1b",
              border: "1px solid #fecaca",
              padding: 14,
              borderRadius: 12,
              textAlign: "center",
            }}
          >
            {error}
          </div>
        )}

        <section>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 16,
            }}
          >
            <h2 style={{ margin: 0, fontSize: 24 }}>Results</h2>
            <span style={{ color: "#6b7280", fontSize: 14 }}>
              {results.length} found
            </span>
          </div>

          {results.length === 0 && !loading && !error && (
            <div
              style={{
                background: "#ffffff",
                border: "1px dashed #d1d5db",
                borderRadius: 16,
                padding: 24,
                color: "#6b7280",
              }}
            >
              Run a search to view ranked listings.
            </div>
          )}

          <div
            style={{
              display: "grid",
              gap: 16,
            }}
          >
            {results.map((item) => (
              <ResultCard key={item.listing_id} item={item} />
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}