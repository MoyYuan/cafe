from typing import Any, Dict
from cafe.forecast.pipelines.base import PipelineComponent
from cafe.sources.question import MetaculusForecastQuestion

class LLMForecastComponent(PipelineComponent):
    def __init__(self, llm):
        self.llm = llm

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        question: MetaculusForecastQuestion = context["question"]
        prompt = self.build_prompt(question)
        context["llm_response"] = self.llm.predict(prompt)
        return context

    def build_prompt(self, question: MetaculusForecastQuestion) -> str:
        return f"Forecast the following question:\n\n{question.title}\n\n{question.description or ''}"
