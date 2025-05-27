import hashlib
from typing import Any, Dict

from .base import BaseModel


class TimeSeriesLocalModel(BaseModel):
    def predict(self, prompt: str, parameters: Dict[str, Any], context: Any) -> Any:
        """
        Local time-series forecasting using ARIMA (via statsmodels).
        parameters should include:
            - series: list of floats (the time series)
            - order: tuple (p, d, q) for ARIMA (default: (1, 1, 1))
            - steps: int, forecast horizon (default: 1)
        """
        # Generate a context cache key
        param_hash = hashlib.md5(str(sorted(parameters.items())).encode()).hexdigest()
        cache_key = f"timeseries_local:{hashlib.md5((prompt + param_hash).encode()).hexdigest()}"
        cached = context.get_data(cache_key)
        if cached is not None:
            return cached
        try:
            import numpy as np
            from statsmodels.tsa.arima.model import ARIMA
        except ImportError:
            return {"error": "Required package 'statsmodels' not installed."}

        series = parameters.get("series")
        order = parameters.get("order", (1, 1, 1))
        steps = parameters.get("steps", 1)
        if not isinstance(series, (list, tuple)) or not series:
            return {
                "error": "Parameter 'series' must be a non-empty list or tuple of floats."
            }
        if not (isinstance(order, (tuple, list)) and len(order) == 3):
            return {
                "error": "Parameter 'order' must be a tuple/list of length 3 (ARIMA order)."
            }
        if not isinstance(steps, int) or steps < 1:
            return {
                "error": "Parameter 'steps' must be a positive integer (forecast horizon)."
            }

        try:
            model = ARIMA(series, order=tuple(order))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=steps)
            result = {"forecast": forecast.tolist()}
            context.set_data(cache_key, result)
            return result
        except Exception as e:
            return {"error": str(e)}
