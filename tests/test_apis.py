from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_api_starts():
    response = client.get("/")

    assert response.status_code == 200


def test_invalid_login():
    response = client.post(
        "/login",
        json={
            "email": "wrong@example.com",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401


def test_get_patients_without_token():
    response = client.get("/patients/")

    assert response.status_code == 401


def test_get_appointment_without_token():
    response = client.get("/appointments/3")

    assert response.status_code == 401