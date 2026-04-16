from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_endpoint_returns_valid_shape():
    payload = {
        "query": "cheap apartment for two in Sydney with good reviews",
        "top_k": 3
    }

    response = client.post("/search", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["query"] == payload["query"]
    assert "results" in data
    assert isinstance(data["results"], list)

    if data["results"]:
        first = data["results"][0]
        assert "listing_id" in first
        assert "name" in first
        assert "ranking_score" in first
        assert "explanations" in first


def test_search_endpoint_bondi_query_not_empty():
    payload = {
        "query": "private room near Bondi beach",
        "top_k": 5
    }

    response = client.post("/search", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) > 0