import json
import os
from datetime import datetime
from typing import List, Optional

import httpx
from dotenv import load_dotenv

from .comment import (MetaculusChangedMyMind, MetaculusComment,
                      MetaculusCommentAuthor, MetaculusMentionedUser)
from .question import MetaculusForecastQuestion
from .source_base import ForecastSourceBase


class MetaculusForecastSource(ForecastSourceBase):
    """
    Fetches resources from Metaculus API. Accepts base_url and api_key as arguments,
    with environment variable defaults. Provides static save/load utilities.
    Supports questions, users, predictions, comments, series, groups, and more.
    """

    DATA_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "forecasts"
    )
    DATA_FILE = os.path.join(DATA_DIR, "metaculus_questions.json")

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        load_dotenv()
        # Remove trailing slash if present, then add /questions/
        base = base_url if base_url is not None else os.getenv("METACULUS_API_URL", "https://www.metaculus.com/api2/")
        base = base.rstrip("/")
        self.base_url = f"{base}/questions/"
        self.api_url = base  # For generic resources
        self.api_key = api_key or os.getenv("METACULUS_API_KEY", "")

    def _headers(self):
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Token {self.api_key}"
        return headers

    def list_resource(self, resource: str, params: Optional[dict] = None):
        """
        Generic list for any Metaculus resource (e.g., 'users', 'predictions').
        If the response is paginated, returns the 'results' list.
        Otherwise, returns the full JSON object (may be a list or dict).
        Returns None if the endpoint is not available or returns an error.
        """
        url = f"{self.api_url}/{resource}/"
        try:
            response = httpx.get(url, headers=self._headers(), params=params)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict) and "results" in data:
                return data["results"]
            return data
        except httpx.HTTPStatusError as e:
            print(f"[Metaculus] Error fetching {url}: {e}")
            return None
        except Exception as e:
            print(f"[Metaculus] Unexpected error fetching {url}: {e}")
            return None

    def get_resource(self, resource: str, id: str):
        """Generic get for any Metaculus resource by id. Returns None if not found or error."""
        url = f"{self.api_url}/{resource}/{id}/"
        try:
            response = httpx.get(url, headers=self._headers())
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"[Metaculus] Error fetching {url}: {e}")
            return None
        except Exception as e:
            print(f"[Metaculus] Unexpected error fetching {url}: {e}")
            return None

    # Convenience wrappers
    def list_questions(self, params: Optional[dict] = None) -> List[MetaculusForecastQuestion]:
        """List Metaculus questions as MetaculusForecastQuestion objects."""
        raw_items = self.list_resource("questions", params=params or {})
        if not raw_items:
            return []
        return [self._parse_metaculus_question(item) for item in raw_items]

    def get_question(self, id: str):
        """Get a Metaculus question by id (raw dict)."""
        return self.get_resource("questions", id)

    def list_users(self, params: Optional[dict] = None):
        """List Metaculus users (raw dicts or list)."""
        return self.list_resource("users", params=params or {})

    def get_user(self, id: str):
        return self.get_resource("users", id)

    def list_predictions(self, params: Optional[dict] = None):
        """List Metaculus predictions (raw dicts or list)."""
        return self.list_resource("predictions", params=params or {})

    def get_prediction(self, id: str) -> dict:
        return self.get_resource("predictions", id)

    def list_metaculus_comments(self, params: Optional[dict] = None):
        """List Metaculus comments from /api/comments/. Returns List[MetaculusComment]."""
        url = self.api_url.replace("/api2", "/api") + "/comments/"
        try:
            response = httpx.get(url, headers=self._headers(), params=params)
            response.raise_for_status()
            data = response.json()
            items = (
                data["results"]
                if isinstance(data, dict) and "results" in data
                else data
            )
            return [self._parse_metaculus_comment(item) for item in items]
        except Exception as e:
            print(f"[Metaculus] Error fetching comments: {e}")
            return None

    def get_metaculus_comment(self, id: str) -> Optional[MetaculusComment]:
        """Get a single comment by id from /api/comments/{id}/. Returns MetaculusComment or None."""
        url = self.api_url.replace("/api2", "/api") + f"/comments/{id}/"
        try:
            response = httpx.get(url, headers=self._headers())
            response.raise_for_status()
            return self._parse_metaculus_comment(response.json())
        except Exception as e:
            print(f"[Metaculus] Error fetching comment {id}: {e}")
            return None

    def list_metaculus_comments_for_question(
        self, question_id: int, params: Optional[dict] = None
    ):
        """Fetch all comments for a given Metaculus question by id. Returns List[MetaculusComment]."""
        # According to API, filter by on_post (which is the post id, not question id). Need mapping.
        # Try using question id directly (if supported), else fetch question and use its post id.
        if params is None:
            params = {}
        params["question"] = question_id
        comments = self.list_metaculus_comments(params=params)
        if comments:
            return comments
        # If above doesn't work, fetch question, extract post id, then filter comments by on_post
        q = self.get_question(str(question_id))
        post_id = (
            q.get("post", None) if isinstance(q, dict) else getattr(q, "post", None)
        )
        if not post_id:
            print(f"[Metaculus] Could not resolve post id for question {question_id}")
            return None
        params.pop("question", None)
        params["on_post"] = post_id
        return self.list_metaculus_comments(params=params)

    def _parse_metaculus_comment(self, item: dict) -> MetaculusComment:
        def parse_author(a):
            return (
                MetaculusCommentAuthor(
                    id=a.get("id"),
                    username=a.get("username"),
                    is_bot=a.get("is_bot", False),
                    is_staff=a.get("is_staff", False),
                )
                if a
                else None
            )

        def parse_mentioned(users):
            return [
                MetaculusMentionedUser(id=u.get("id"), username=u.get("username"))
                for u in users or []
            ]

        def parse_changed(cm):
            return (
                MetaculusChangedMyMind(
                    count=cm.get("count", 0),
                    for_this_user=cm.get("for_this_user", False),
                )
                if cm
                else None
            )

        from datetime import datetime

        def parse_dt(s):
            try:
                return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None
            except Exception:
                return None

        id = item.get("id", 0)
        if id is None:
            id = 0
        return MetaculusComment(
            id=int(id),
            author=parse_author(item.get("author")),
            parent_id=item.get("parent_id"),
            root_id=item.get("root_id"),
            created_at=parse_dt(item.get("created_at")),
            text=item.get("text", ""),
            on_post=int(item.get("on_post", 0)),
            included_forecast=item.get("included_forecast"),
            is_private=item.get("is_private"),
            vote_score=item.get("vote_score"),
            changed_my_mind=parse_changed(item.get("changed_my_mind")),
            mentioned_users=parse_mentioned(item.get("mentioned_users")),
            user_vote=item.get("user_vote"),
            raw=item,
        )

    def list_series(self, params: Optional[dict] = None):
        return self.list_resource("series", params=params or {})

    def get_series(self, id: str) -> dict:
        return self.get_resource("series", id)

    def list_groups(self, params: Optional[dict] = None):
        return self.list_resource("groups", params=params or {})

    def get_group(self, id: str) -> dict:
        return self.get_resource("groups", id)

    @classmethod
    def from_env(cls):
        """Factory for instantiating from environment variables."""
        return cls()

    def _parse_metaculus_question(self, item: dict) -> MetaculusForecastQuestion:
        return MetaculusForecastQuestion(
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
            raw=item,
        )

    def _parse_date(self, s):
        if not s:
            return None
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None

    @staticmethod
    def save_questions_to_json(questions: List[MetaculusForecastQuestion], filepath: Optional[str] = None):
        if filepath is None:
            filepath = MetaculusForecastSource.DATA_FILE
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([q.raw for q in questions], f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_questions_from_json(filepath: Optional[str] = None) -> List[MetaculusForecastQuestion]:
        if filepath is None:
            filepath = MetaculusForecastSource.DATA_FILE
        if not os.path.exists(filepath):
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [MetaculusForecastSource._parse_metaculus_question_static(item) for item in data]

    @staticmethod
    def _parse_metaculus_question_static(item: dict) -> MetaculusForecastQuestion:
        # Static version for loading from JSON
        def parse_date(s):
            if not s:
                return None
            try:
                return datetime.fromisoformat(s.replace("Z", "+00:00"))
            except Exception:
                return None

        return MetaculusForecastQuestion(
            id=str(item.get("id")),
            title=item.get("title", ""),
            description=item.get("description"),
            resolution_criteria=item.get("resolution_criteria"),
            created_at=parse_date(item.get("created_time")),
            deadline=parse_date(item.get("publish_time")),
            resolved_at=parse_date(item.get("resolve_time")),
            status=item.get("status"),
            community_prediction=item.get("community_prediction"),
            url=f"https://www.metaculus.com/questions/{item.get('id')}/",
            tags=item.get("tags", []),
            raw=item,
        )
