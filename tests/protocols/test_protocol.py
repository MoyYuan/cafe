from fastapi.testclient import TestClient

from cafe.main import app

client = TestClient(app)


import pytest


def test_forecast_vllm():
    pytest.importorskip("vllm", reason="vllm not installed; skipping vLLM test.")
    response = client.post("/forecast", json={"model": "vllm", "prompt": "Test prompt"})
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "vllm"
    # Accept real output: result should be non-empty string or dict
    assert data["result"] is not None
    assert isinstance(data["result"], (str, dict))
    if isinstance(data["result"], str):
        assert len(data["result"].strip()) > 0


def test_forecast_gemini_no_key(monkeypatch):
    # Remove API key for this test
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr("cafe.config.config.Config.GEMINI_API_KEY", None)
    response = client.post(
        "/forecast", json={"model": "gemini", "prompt": "Test prompt"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "gemini"
    assert data["error"] is not None
