from abc import ABC, abstractmethod
from typing import List

from .question import MetaculusForecastQuestion


class ForecastSourceBase(ABC):
    @abstractmethod
    def list_questions(self) -> List[MetaculusForecastQuestion]:
        pass

    @abstractmethod
    def get_question(self, id: str) -> MetaculusForecastQuestion:
        pass
