from abc import ABC, abstractmethod
from typing import Any, Dict, List


class PipelineComponent(ABC):
    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input context and return the updated context.
        """
        pass

    def describe(self) -> str:
        return self.__class__.__name__


class ForecastPipeline:
    def __init__(self, components: List[PipelineComponent]):
        self.components = components

    def run(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        context = initial_context
        for component in self.components:
            context = component.run(context)
        return context

    def describe(self) -> str:
        return " -> ".join([c.describe() for c in self.components])
