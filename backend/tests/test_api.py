"""
Automated end-to-end API integration tests using FastAPI TestClient.
Tests:
- GET /api/health
- GET /api/crops
- GET /api/crops/{crop_id}
- POST /api/recommend (valid, missing, invalid)
- POST /api/compare
- GET /api/profiles
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_health():
    """Verify health endpoint returns 200 and healthy status."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "HEALTHY"
    assert data["total_crops_loaded"] >= 10


def test_api_list_crops_with_filter():
    """Verify crop catalog and season filtering."""
    resp = client.get("/api/crops")
    assert resp.status_code == 200
    all_crops = resp.json()
    assert len(all_crops) >= 10

    # Filter by Kharif
    kharif_resp = client.get("/api/crops?season=Kharif")
    assert kharif_resp.status_code == 200
    kharif_crops = kharif_resp.json()
    assert len(kharif_crops) > 0
    for c in kharif_crops:
        assert "Kharif" in c["growing_seasons"]


def test_api_get_single_crop():
    """Verify single crop retrieval."""
    resp = client.get("/api/crops/rice")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Rice"
    assert data["scientific_name"] == "Oryza sativa"

    # Non-existent crop
    resp_404 = client.get("/api/crops/fake_crop_xyz")
    assert resp_404.status_code == 404


def test_api_recommend_valid_submission():
    """Test full recommendation POST request."""
    payload = {
        "location": {
            "country": "India",
            "state": "Andhra Pradesh",
            "district": "Guntur",
            "season": "Kharif",
            "irrigation": "Irrigated"
        },
        "soil": {
            "soil_type": "Black Soil",
            "soil_ph": 7.2,
            "nitrogen": 80.0,
            "phosphorus": 40.0,
            "potassium": 50.0,
            "is_measured": True
        },
        "environment": {
            "temperature": 29.0,
            "rainfall": 850.0,
            "rainfall_period": "Growing Season",
            "relative_humidity": 70.0,
            "is_measured": True
        }
    }
    resp = client.post("/api/recommend", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["is_sufficient_data"] is True
    assert len(data["recommendations"]) >= 10
    # Check top recommendation properties
    top = data["recommendations"][0]
    assert "crop_name" in top
    assert top["compatibility_score"] is not None
    assert "why_this_crop" in top
    assert len(top["factor_evaluations"]) == 9


def test_api_recommend_validation_error_invalid_ph():
    """Invalid pH (18.5) should return 422 Unprocessable Entity with error detail."""
    payload = {
        "location": {
            "state": "Telangana",
            "season": "Kharif"
        },
        "soil": {
            "soil_ph": 18.5
        },
        "environment": {}
    }
    resp = client.post("/api/recommend", json=payload)
    assert resp.status_code == 422
    data = resp.json()
    assert "detail" in data
    assert any("soil_ph" in str(e) for e in data.get("errors", []))


def test_api_recommend_validation_error_invalid_humidity():
    """Invalid humidity (120%) should return 422."""
    payload = {
        "location": {
            "state": "Punjab",
            "season": "Rabi"
        },
        "soil": {},
        "environment": {
            "relative_humidity": 120.0
        }
    }
    resp = client.post("/api/recommend", json=payload)
    assert resp.status_code == 422


def test_api_compare_endpoint():
    """Test crop comparison API."""
    payload = {
        "crop_ids": ["rice", "cotton", "maize"]
    }
    resp = client.post("/api/compare", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["crop_ids"]) == 3
    assert len(data["comparison_table"]) > 5
    assert "summary_verdict" in data


def test_api_profiles_endpoint():
    """Test retrieving documented example profiles."""
    resp = client.get("/api/profiles")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 5
    profile_ids = [p["id"] for p in data]
    assert "profile_rice_delta" in profile_ids
    assert "profile_pearl_millet_arid" in profile_ids
