type SearchBarProps = {
  query: string;
  setQuery: (value: string) => void;
  onSearch: () => void;
  loading: boolean;
  exampleQueries: string[];
};

export default function SearchBar({
  query,
  setQuery,
  onSearch,
  loading,
  exampleQueries,
}: SearchBarProps) {
  return (
    <section
      style={{
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: 16,
        padding: 20,
        marginBottom: 24,
        boxShadow: "0 8px 24px rgba(0,0,0,0.04)",
      }}
    >
      <label
        htmlFor="query"
        style={{
          display: "block",
          fontSize: 14,
          fontWeight: 600,
          marginBottom: 10,
          textAlign: "center",
        }}
      >
        Search query
      </label>

      <div
        style={{
          display: "flex",
          gap: 12,
          flexWrap: "wrap",
        }}
      >
        <input
          id="query"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              onSearch();
            }
          }}
          style={{
            flex: 1,
            minWidth: 280,
            padding: "14px 16px",
            borderRadius: 12,
            border: "1px solid #d1d5db",
            fontSize: 16,
            outline: "none",
            background: "#fff",
          }}
        />
        <button
          onClick={onSearch}
          disabled={loading}
          style={{
            padding: "14px 18px",
            borderRadius: 12,
            border: "none",
            background: loading ? "#9ca3af" : "#111827",
            color: "#fff",
            fontSize: 15,
            fontWeight: 700,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      <div
        style={{
          marginTop: 14,
          display: "flex",
          gap: 8,
          flexWrap: "wrap",
        }}
      >
        {exampleQueries.map((example) => (
          <button
            key={example}
            onClick={() => setQuery(example)}
            style={{
              padding: "8px 12px",
              borderRadius: 999,
              border: "1px solid #d1d5db",
              background: "#f9fafb",
              cursor: "pointer",
              fontSize: 13,
            }}
          >
            {example}
          </button>
        ))}
      </div>
    </section>
  );
}