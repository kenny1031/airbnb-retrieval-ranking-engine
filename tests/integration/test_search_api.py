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


def test_search_endpoint_bondi_query_returns_waverley_results():
    payload = {
        "query": "private room near Bondi beach",
        "top_k": 5,
    }

    response = client.post("/search", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert len(data["results"]) > 0

    neighbourhoods = [item["neighbourhood_cleansed"] for item in data["results"]]
    assert "Waverley" in neighbourhoods


def test_search_endpoint_manly_wifi_query_returns_entire_home():
    payload = {
        "query": "entire home in Manly with wifi",
        "top_k": 5,
    }

    response = client.post("/search", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert len(data["results"]) > 0

    top_result = data["results"][0]
    assert top_result["neighbourhood_cleansed"] == "Manly"
    assert top_result["room_type"] == "Entire home/apt"


def test_search_endpoint_family_randwick_query_returns_house_results():
    payload = {
        "query": "family-friendly house in Randwick",
        "top_k": 5,
    }

    response = client.post("/search", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert len(data["results"]) > 0

    property_types = [item["property_type"] for item in data["results"]]
    neighbourhoods = [item["neighbourhood_cleansed"] for item in data["results"]]

    assert "House" in property_types
    assert "Randwick" in neighbourhoods