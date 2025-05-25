from abc import ABC, abstractmethod
from typing import List
from .forecast_question import ForecastQuestion

class ForecastSourceBase(ABC):
    @abstractmethod
    def list_questions(self) -> List[ForecastQuestion]:
        pass

    @abstractmethod
    def get_question(self, id: str) -> ForecastQuestion:
        pass
