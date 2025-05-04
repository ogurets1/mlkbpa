import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_process_file():
    test_file = "test_image.jpg"
    
    with open(test_file, "rb") as f:
        response = client.post(
            "/api/v1/process",
            files={"file": (test_file, f, "image/jpeg")}
        )
    
    assert response.status_code == 200
    json_data = response.json()
    assert "result_url" in json_data
    assert "detections" in json_data