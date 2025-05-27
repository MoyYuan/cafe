import os

import pytest

from cafe.context.memory import InMemoryContext
from cafe.models.llm.gemini import GeminiModel


def test_gemini_predict_real(monkeypatch):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("No GEMINI_API_KEY set in environment.")
    model = GeminiModel(api_key=api_key, mock_mode=False, cache_enabled=False)
    context = InMemoryContext()
    result = model.predict("What is the capital of France?", {}, context)
    assert isinstance(result, dict)
    assert "text" in result
    assert isinstance(result["text"], str)


def test_gemini_predict_mock():
    model = GeminiModel(mock_mode=True)
    context = InMemoryContext()
    result = model.predict("mock prompt", {}, context)
    assert result["mock"] is True
    assert result["prompt"] == "mock prompt"


def test_gemini_parameters(monkeypatch):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("No GEMINI_API_KEY set in environment.")
    model = GeminiModel(api_key=api_key, mock_mode=False, cache_enabled=False)
    context = InMemoryContext()
    parameters = {"max_output_tokens": 10, "temperature": 0.1}
    result = model.predict("Say hello", parameters, context)
    assert isinstance(result, dict)
    assert "text" in result


def test_gemini_cache():
    # Only test cache in mock mode to ensure results match
    model = GeminiModel(mock_mode=True, cache_enabled=True)
    context = InMemoryContext()
    prompt = "cache test"
    # First call, should not be cached
    result1 = model.predict(prompt, {}, context)
    # Second call, should be cached
    result2 = model.predict(prompt, {}, context)
    assert result1 == result2
    # Confirm cache key is present in context
    cache_key = model._make_cache_key(prompt, {})
    assert context.get_data(cache_key) == result1
