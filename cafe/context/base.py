from abc import ABC, abstractmethod
from typing import Any


class BaseContext(ABC):
    @abstractmethod
    def get_data(self, key: str) -> Any:
        pass

    @abstractmethod
    def set_data(self, key: str, value: Any) -> None:
        pass
