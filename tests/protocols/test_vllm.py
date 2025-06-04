import pytest

from cafe.context.memory import InMemoryContext

pytestmark = pytest.mark.skipif(
    pytest.importorskip("vllm", reason="vllm not installed; skipping vLLM tests."),
    reason="vllm not installed; skipping vLLM tests.",
)

from cafe.models.llm.vllm import VLLMModel


def test_vllm_predict_default():
    model = VLLMModel(model_path="facebook/opt-125m")
    context = InMemoryContext()
    result = model.predict("Hello vLLM!", {}, context)
    assert isinstance(result, (dict, str))


def test_vllm_parameters():
    model = VLLMModel(model_path="facebook/opt-125m")
    context = InMemoryContext()
    params = {"max_tokens": 5}
    result = model.predict("Say hi", params, context)
    assert isinstance(result, (dict, str))


def test_vllm_cache():
    model = VLLMModel(model_path="facebook/opt-125m")
    context = InMemoryContext()
    prompt = "cache test"
    result1 = model.predict(prompt, {}, context)
    result2 = model.predict(prompt, {}, context)
    assert result1 == result2
