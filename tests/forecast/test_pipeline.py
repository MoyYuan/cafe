import pytest

from cafe.forecast.pipelines.base import ForecastPipeline, PipelineComponent
from cafe.forecast.pipelines.llm_component import LLMForecastComponent
from cafe.forecast.pipelines.news_component import NewsSearchComponent
from cafe.sources.question import MetaculusForecastQuestion


class DummyLLM:
    def predict(self, prompt):
        return f"LLM answer to: {prompt[:20]}..."


class DummyNewsAPI:
    def search(self, query):
        return [f"News about {query}"]


def test_llm_and_news_pipeline():
    llm = DummyLLM()
    news_api = DummyNewsAPI()
    pipeline = ForecastPipeline(
        [
            NewsSearchComponent(news_api),
            LLMForecastComponent(llm),
        ]
    )
    question = MetaculusForecastQuestion(id="1", title="Test Q", description="Desc")
    context = {"question": question}
    result = pipeline.run(context)
    assert "llm_response" in result
    assert "news" in result
    assert result["news"] == ["News about Test Q"]
    assert result["llm_response"].startswith("LLM answer to: ")
