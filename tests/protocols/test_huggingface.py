import pytest

from cafe.context.memory import InMemoryContext
from cafe.models.llm.huggingface import HuggingFaceModel


def test_huggingface_predict_default():
    try:
        model = HuggingFaceModel(model_path="gpt2")
    except ImportError:
        pytest.skip("transformers not installed")
    context = InMemoryContext()
    result = model.predict("Hello world!", {}, context)
    assert isinstance(result, dict)
    assert "text" in result
    assert isinstance(result["text"], str)
    assert len(result["text"]) > 0


def test_huggingface_parameters():
    try:
        model = HuggingFaceModel(model_path="gpt2")
    except ImportError:
        pytest.skip("transformers not installed")
    context = InMemoryContext()
    params = {"max_new_tokens": 5}
    result = model.predict("Say hi", params, context)
    assert isinstance(result, dict)
    assert "text" in result


def test_huggingface_cache():
    try:
        model = HuggingFaceModel(model_path="gpt2")
    except ImportError:
        pytest.skip("transformers not installed")
    context = InMemoryContext()
    prompt = "cache test"
    result1 = model.predict(prompt, {}, context)
    result2 = model.predict(prompt, {}, context)
    assert result1 == result2
