import json
from datetime import datetime
from typing import List

from .forecast_question import ForecastQuestion
from .source_base import ForecastSourceBase


class LocalForecastSource(ForecastSourceBase):
    def __init__(self, path: str):
        self.path = path

    def list_questions(self) -> List[ForecastQuestion]:
        with open(self.path, "r") as f:
            data = json.load(f)
        return [self._parse_question(item) for item in data]

    def get_question(self, id: str) -> ForecastQuestion:
        with open(self.path, "r") as f:
            data = json.load(f)
        for item in data:
            if str(item.get("id")) == str(id):
                return self._parse_question(item)
        raise ValueError(f"Question with id {id} not found.")

    def _parse_question(self, item: dict) -> ForecastQuestion:
        return ForecastQuestion(
            id=str(item.get("id")),
            title=item.get("title", ""),
            description=item.get("description"),
            resolution_criteria=item.get("resolution_criteria"),
            created_at=self._parse_date(item.get("created_at")),
            deadline=self._parse_date(item.get("deadline")),
            resolved_at=self._parse_date(item.get("resolved_at")),
            status=item.get("status"),
            community_prediction=item.get("community_prediction"),
            url=item.get("url"),
            tags=item.get("tags", []),
            raw=item,
        )

    def _parse_date(self, s):
        if not s:
            return None
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return None
