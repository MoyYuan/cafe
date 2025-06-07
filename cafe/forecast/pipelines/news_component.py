from typing import Any, Dict
from cafe.forecast.pipelines.base import PipelineComponent

class NewsSearchComponent(PipelineComponent):
    def __init__(self, news_api):
        self.news_api = news_api

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        question = context["question"]
        news = self.news_api.search(question.title)
        context["news"] = news
        return context
