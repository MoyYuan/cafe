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

from .metaculus import router as metaculus_router

# Context instance (in-memory)
context = InMemoryContext()

# Lazy model getter


def get_model(name: str) -> Predictable:
    if name == "vllm":
        return VLLMModel()
    if name == "gemini":
        return GeminiModel(api_key=os.getenv("GEMINI_API_KEY"))
    if name == "timeseries_local":
        return TimeSeriesLocalModel()
    if name == "timeseries_api":
        return TimeSeriesAPIModel()
    raise ValueError(f"Unknown model: {name}")


@router.post("/forecast", response_model=ForecastResponse)
def forecast(request: ForecastRequest):
    try:
        model = get_model(request.model)
    except ValueError as e:
        valid_models = ["vllm", "gemini", "timeseries_local", "timeseries_api"]
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model: {request.model}. Valid models: {', '.join(valid_models)}",
        )
    try:
        result = model.predict(request.prompt, request.parameters or {}, context)
        return ForecastResponse(result=result, model=request.model)
    except Exception as e:
        # Always return error in response, even for missing API key
        return ForecastResponse(result=None, model=request.model, error=str(e))


# Mount Metaculus endpoints
router.include_router(metaculus_router, prefix="")
