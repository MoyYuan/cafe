from datetime import datetime
from typing import Any, List, Optional


class MetaculusForecastQuestion:
    def __init__(
        self,
        id: str,
        title: str,
        description: Optional[str] = None,
        resolution_criteria: Optional[str] = None,
        created_at: Optional[datetime] = None,
        deadline: Optional[datetime] = None,
        resolved_at: Optional[datetime] = None,
        status: Optional[str] = None,
        community_prediction: Optional[Any] = None,
        url: Optional[str] = None,
        tags: Optional[List[str]] = None,
        raw: Optional[dict] = None,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.resolution_criteria = resolution_criteria
        self.created_at = created_at
        self.deadline = deadline
        self.resolved_at = resolved_at
        self.status = status
        self.community_prediction = community_prediction
        self.url = url
        self.tags = tags or []
        self.raw = raw or {}

    def __repr__(self):
        """Represents a forecast question from the Metaculus API (MetaculusForecastQuestion)."""
        return f"<MetaculusForecastQuestion id={self.id} title={self.title!r}>"
