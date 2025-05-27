import pytest

from cafe.models.llm.postprocessing import GeminiPostprocessor, VLLMPostprocessor


@pytest.mark.parametrize(
    "raw_output,expected",
    [
        # Gemini: JSON string
        (
            type("Resp", (), {"text": '{"foo": 1, "bar": "baz"}'})(),
            {"foo": 1, "bar": "baz"},
        ),
        # Gemini: plain string
        (type("Resp", (), {"text": "hello world"})(), "hello world"),
        # Gemini: dict with text
        ({"text": '{"answer": 42}'}, {"answer": 42}),
        # Gemini: dict with plain text
        ({"text": "plain text"}, "plain text"),
        # Gemini: missing text
        ({}, None),
    ],
)
def test_gemini_extract_answer(raw_output, expected):
    proc = GeminiPostprocessor()
    assert proc.extract_answer(raw_output) == expected


@pytest.mark.parametrize(
    "raw_output,expected",
    [
        # vLLM: dict with JSON
        ({"text": '{"foo": 123}'}, {"foo": 123}),
        # vLLM: dict with plain text
        ({"text": "plain"}, "plain"),
        # vLLM: non-dict, JSON string
        ('{"bar": 9}', {"bar": 9}),
        # vLLM: non-dict, plain string
        ("just text", "just text"),
    ],
)
def test_vllm_extract_answer(raw_output, expected):
    proc = VLLMPostprocessor()
    assert proc.extract_answer(raw_output) == expected
