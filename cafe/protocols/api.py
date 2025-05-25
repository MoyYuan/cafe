import os

from fastapi import APIRouter, Depends, HTTPException, status

from cafe.context.memory import InMemoryContext
from cafe.models.base import Predictable
from cafe.models.llm.gemini import GeminiModel
from cafe.models.llm.vllm import VLLMModel
from cafe.models.timeseries.api import TimeSeriesAPIModel
from cafe.models.timeseries.local import TimeSeriesLocalModel

from .schemas import ForecastRequest, ForecastResponse

router = APIRouter()

# Context instance (in-memory)
context = InMemoryContext()

# Model registry
models: dict[str, Predictable] = {
    "vllm": VLLMModel(),
    "gemini": GeminiModel(api_key=os.getenv("GEMINI_API_KEY")),
    "timeseries_local": TimeSeriesLocalModel(),
    "timeseries_api": TimeSeriesAPIModel(),
}


@router.post("/forecast", response_model=ForecastResponse)
def forecast(request: ForecastRequest):
    model = models.get(request.model)
    if not model:
        valid_models = ", ".join(models.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model: {request.model}. Valid models: {valid_models}",
        )
    try:
        result = model.predict(request.prompt, request.parameters or {}, context)
        return ForecastResponse(result=result, model=request.model)
    except Exception as e:
        return ForecastResponse(result=None, model=request.model, error=str(e))
