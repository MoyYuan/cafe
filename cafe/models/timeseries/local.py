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
        try:
            import numpy as np
            from statsmodels.tsa.arima.model import ARIMA
        except ImportError:
            return {"error": "Required package 'statsmodels' not installed."}

        series = parameters.get("series")
        order = parameters.get("order", (1, 1, 1))
        steps = parameters.get("steps", 1)

        if not isinstance(series, list) or not all(
            isinstance(x, (int, float)) for x in series
        ):
            return {"error": "Parameter 'series' must be a list of numbers."}
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
            return {"forecast": forecast.tolist()}
        except Exception as e:
            return {"error": str(e)}
