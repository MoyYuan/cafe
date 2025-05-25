from pydantic import BaseModel
from typing import Optional, Any

class ForecastRequest(BaseModel):
    model: str  # 'vllm', 'gemini', 'timeseries_local', 'timeseries_api', etc.
    prompt: str
    parameters: Optional[dict] = None

class ForecastResponse(BaseModel):
    result: Any
    model: str
    error: Optional[str] = None
