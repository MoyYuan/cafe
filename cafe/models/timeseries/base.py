from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseModel(ABC):
    """Abstract base class for time series models."""

    @abstractmethod
    def predict(self, prompt: str, parameters: Dict[str, Any], context: Any) -> Any:
        """
        Generate a prediction from the time series model.
        Args:
            prompt: Input string or description of the forecasting task.
            parameters: Model-specific parameters (e.g., window size, forecast horizon).
            context: Optional context object for state or data passing.
        Returns:
            Model output (forecast, dict, etc.).
        """
        pass
