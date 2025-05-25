import httpx
from typing import List
from .forecast_question import ForecastQuestion
from .source_base import ForecastSourceBase
from datetime import datetime

class MetaculusForecastSource(ForecastSourceBase):
    BASE_URL = "https://www.metaculus.com/api2/questions/"

    def list_questions(self) -> List[ForecastQuestion]:
        response = httpx.get(self.BASE_URL)
        response.raise_for_status()
        data = response.json()
        questions = []
        for item in data.get("results", []):
            questions.append(self._parse_question(item))
        return questions

    def get_question(self, id: str) -> ForecastQuestion:
        response = httpx.get(f"{self.BASE_URL}{id}/")
        response.raise_for_status()
        return self._parse_question(response.json())

    def _parse_question(self, item: dict) -> ForecastQuestion:
        return ForecastQuestion(
            id=str(item.get("id")),
            title=item.get("title", ""),
            description=item.get("description"),
            resolution_criteria=item.get("resolution_criteria"),
            created_at=self._parse_date(item.get("created_time")),
            deadline=self._parse_date(item.get("publish_time")),
            resolved_at=self._parse_date(item.get("resolve_time")),
            status=item.get("status"),
            community_prediction=item.get("community_prediction"),
            url=f"https://www.metaculus.com/questions/{item.get('id')}/",
            tags=item.get("tags", []),
            raw=item
        )

    def _parse_date(self, s):
        if not s:
            return None
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
