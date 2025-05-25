from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseModel(ABC):
    @abstractmethod
    def predict(self, prompt: str, parameters: Dict[str, Any], context) -> Any:
        pass
