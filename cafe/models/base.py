from abc import ABC, abstractmethod
from typing import Any, Dict, Protocol


class Predictable(Protocol):
    def predict(self, prompt: str, parameters: Dict[str, Any], context) -> Any: ...


class BaseModel(Predictable, ABC):
    """Base class for time series models."""

    @abstractmethod
    def predict(self, prompt: str, parameters: Dict[str, Any], context) -> Any:
        pass
