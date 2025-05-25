from .base import BaseContext
from typing import Any


class InMemoryContext(BaseContext):
    def __init__(self):
        self._store = {}

    def get_data(self, key: str) -> Any:
        return self._store.get(key)

    def set_data(self, key: str, value: Any) -> None:
        self._store[key] = value
