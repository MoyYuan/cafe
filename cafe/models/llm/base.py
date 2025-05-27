from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseModel(ABC):
    """
    Abstract base class for all LLM models.
    All models must implement the predict method.
    """

    @abstractmethod
    def predict(self, prompt: str, parameters: Dict[str, Any], context: Any) -> Any:
        """
        Generate a prediction or completion from the model.
        Args:
            prompt: The input prompt string.
            parameters: Model-specific parameters (temperature, max_tokens, etc.).
            context: Context object for stateful or multi-turn models.
        Returns:
            The raw model output (string, dict, etc.).
        """
        pass
