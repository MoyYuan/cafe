from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_forecast_vllm():
    response = client.post("/forecast", json={"model": "vllm", "prompt": "Test prompt"})
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "vllm"
    assert "vLLM local model integration pending" in str(data["result"])


def test_forecast_gemini_no_key(monkeypatch):
    # Remove API key for this test
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.post(
        "/forecast", json={"model": "gemini", "prompt": "Test prompt"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "gemini"
    assert data["error"] is not None
