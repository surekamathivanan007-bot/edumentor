"""
Tests for the Flask API endpoint in app.py

Run with: pytest tests/
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_index_loads(client):
    response = client.get("/")
    assert response.status_code == 200


def test_plan_endpoint_valid_request(client):
    payload = {
        "total_minutes": 120,
        "subjects": [
            {"name": "Maths", "marks_percent": 40, "difficulty": 4, "days_to_exam": 3, "is_weak_topic": True},
            {"name": "English", "marks_percent": 85, "difficulty": 2, "days_to_exam": 20},
        ],
    }
    response = client.post("/api/plan", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "plan" in data
    assert len(data["plan"]) == 2


def test_plan_endpoint_rejects_missing_body(client):
    response = client.post("/api/plan")
    assert response.status_code == 400


def test_plan_endpoint_rejects_empty_subjects(client):
    response = client.post("/api/plan", json={"total_minutes": 60, "subjects": []})
    assert response.status_code == 400


def test_plan_endpoint_rejects_negative_minutes(client):
    payload = {"total_minutes": -10, "subjects": [{"name": "Maths", "marks_percent": 50, "difficulty": 2, "days_to_exam": 5}]}
    response = client.post("/api/plan", json=payload)
    assert response.status_code == 400


def test_plan_endpoint_rejects_too_many_subjects(client):
    subjects = [
        {"name": f"Subject{i}", "marks_percent": 50, "difficulty": 2, "days_to_exam": 5}
        for i in range(20)
    ]
    response = client.post("/api/plan", json={"total_minutes": 60, "subjects": subjects})
    assert response.status_code == 400


def test_plan_endpoint_rejects_invalid_difficulty(client):
    payload = {"total_minutes": 60, "subjects": [{"name": "Maths", "marks_percent": 50, "difficulty": 99, "days_to_exam": 5}]}
    response = client.post("/api/plan", json=payload)
    assert response.status_code == 400
