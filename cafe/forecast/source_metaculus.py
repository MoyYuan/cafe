import json
import os
from datetime import datetime
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union, cast

import httpx
from dotenv import load_dotenv

from .comment import (
    MetaculusChangedMyMind,
    MetaculusComment,
    MetaculusCommentAuthor,
    MetaculusMentionedUser,
)
from .question import MetaculusForecastQuestion
from .source_base import ForecastSourceBase


class MetaculusForecastSource(ForecastSourceBase):
    @classmethod
    def from_env(cls, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """Instantiate using environment variables or provided overrides."""
        return cls(base_url=base_url, api_key=api_key)

    """
    Fetches resources from Metaculus API. Accepts base_url and api_key as arguments,
    with environment variable defaults. Provides static save/load utilities.
    Supports questions, users, predictions, comments, series, groups, and more.
    """

    def fetch_and_cache_questions_and_comments(
        self,
        after: str = "2023-10-01",
        output_dir: str = "data/forecasts/metaculus",
        comments_mode: str = "all-in-one",
        limit: Optional[int] = None,
        refresh_questions: bool = False,
        refresh_comments: bool = False,
        no_cache: bool = False,
        verbose: bool = False,
    ):
        """
        Fetch questions and comments from Metaculus, with caching and checkpointing.
        Logic refactored from scripts/metaculus/fetch_metaculus_questions.py.
        """
        import json
        import sys
        import time
        from pathlib import Path

        from cafe.forecast.processing.metadata import get_metadata

        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        cache_questions_file = out_dir / "questions_cache.json"
        comments_dir = out_dir / "comments_by_question"
        comments_dir.mkdir(exist_ok=True)
        checkpoint_file = out_dir / "fetch_checkpoint.json"
        questions = []
        fetched_qids = set()
        # Questions cache logic
        if not no_cache and cache_questions_file.exists() and not refresh_questions:
            with cache_questions_file.open() as f:
                questions = json.load(f)
            fetched_qids = set(str(q.get("id")) for q in questions)
            print(f"Loaded {len(questions)} questions from cache.")
        params: dict[str, str | int | float | bool | None] = {
            "created_time__gt": f"{after}T00:00:00Z",
            "limit": 100,
        }
        page = 0
        all_questions = questions.copy()
        next_url: Optional[str] = None
        while True:
            if next_url:
                if next_url.startswith("http://"):
                    next_url = "https://" + next_url[len("http://") :]
                resp = httpx.get(next_url, headers=self._headers())
                resp.raise_for_status()
                data = resp.json()
            else:
                base_url = self.base_url
                if base_url.startswith("http://"):
                    base_url = "https://" + base_url[len("http://") :]
                data = httpx.get(
                    base_url, headers=self._headers(), params=params
                ).json()
            items = (
                data["results"]
                if isinstance(data, dict) and "results" in data
                else data
            )
            if not items:
                break
            new_questions = [q for q in items if str(q.get("id")) not in fetched_qids]
            all_questions.extend(new_questions)
            fetched_qids.update(str(q.get("id")) for q in new_questions)
            if limit is not None and len(all_questions) >= limit:
                all_questions = all_questions[:limit]
                break
            next_url = data.get("next") if isinstance(data, dict) else None  # type: ignore
            page += 1
            if not next_url:
                break
            time.sleep(0.2)
        # Save cache
        if (refresh_questions or not cache_questions_file.exists()) and not no_cache:
            with cache_questions_file.open("w") as f:
                json.dump(all_questions, f, indent=2)
            print(f"Wrote {len(all_questions)} questions to cache.")
        # Fetch comments
        comments_by_qid = {}
        for q in all_questions:
            qid = str(q.get("id"))
            comment_file = comments_dir / f"{qid}.json"
            comments = None
            if not no_cache and comment_file.exists() and not refresh_comments:
                with comment_file.open() as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict) and "data" in loaded:
                        comments = loaded["data"]
                    else:
                        comments = loaded
            else:
                comments = [
                    c.raw if hasattr(c, "raw") else c
                    for c in self.list_metaculus_comments_for_question(int(qid)) or []
                ]
                if not no_cache or refresh_comments:
                    c_metadata = {
                        "qid": qid,
                        "comment_count": len(comments),
                    }
                    with comment_file.open("w") as f:
                        json.dump(
                            {"metadata": c_metadata, "data": comments}, f, indent=2
                        )
            comments_by_qid[qid] = comments
            if verbose and comments:
                for c in comments[:3]:
                    print("  -", c)
        return all_questions, comments_by_qid

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        load_dotenv()
        # Remove trailing slash if present, then add /questions/
        base = (
            base_url
            if base_url is not None
            else os.getenv("METACULUS_API_URL", "https://www.metaculus.com/api2/")
        )
        base = base.rstrip("/")
        self.base_url = f"{base}/questions/"
        self.api_url = base  # For generic resources
        self.api_key = api_key or os.getenv("METACULUS_API_KEY", "")

    def _headers(self):
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Token {self.api_key}"
        return headers

    def list_resource(
        self,
        resource: str,
        params: Optional[Mapping[str, Union[str, int, float, bool, None]]] = None,
    ):
        """
        Generic list for any Metaculus resource (e.g., 'users', 'predictions').
        If the response is paginated, returns the 'results' list.
        Otherwise, returns the full JSON object (may be a list or dict).
        Returns None if the endpoint is not available or returns an error.
        """
        url = f"{self.api_url}/{resource}/"
        try:
            response = httpx.get(url, headers=self._headers(), params=params or {})
            # If redirected, httpx will follow automatically. But if not, check for 301 manually.
            if response.status_code == 301 and url.startswith("http://"):
                # Retry with https
                url_https = url.replace("http://", "https://", 1)
                response = httpx.get(
                    url_https,
                    headers=self._headers(),
                    params=params or {},
                )
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
    def list_questions(
        self, params: Optional[Mapping[str, Union[str, int, float, bool, None]]] = None
    ) -> List[MetaculusForecastQuestion]:
        """List Metaculus questions as MetaculusForecastQuestion objects."""
        raw_items = self.list_resource("questions", params=params or {})
        if not raw_items:
            return []
        return [self._parse_metaculus_question(item) for item in raw_items]

    def get_question(self, id: str) -> MetaculusForecastQuestion:
        """Get a Metaculus question by id (MetaculusForecastQuestion object)."""
        raw = self.get_resource("questions", id)
        if not raw:
            raise ValueError(f"Question with id {id} not found.")
        return self._parse_metaculus_question(raw)

    def list_users(
        self, params: Optional[Mapping[str, Union[str, int, float, bool, None]]] = None
    ):
        """List Metaculus users (raw dicts or list)."""
        return self.list_resource("users", params=params or {})

    def get_user(self, id: str):
        return self.get_resource("users", id)

    def list_metaculus_comments(
        self,
        params: Optional[Mapping[str, Union[str, int, float, bool, None]]] = None,
    ) -> list:
        """Fetch all comments from the /api/comments/ endpoint, handling pagination. Returns List[MetaculusComment]."""
        import urllib.parse

        url: Optional[str] = (
            self.api_url.replace("http://", "https://").replace("/api2", "/api")
            + "/comments/"
        )
        all_items = []
        next_params: Optional[Dict[str, str | int | float | bool | None]] = (
            dict(params) if params else None
        )
        while url:
            try:
                if url.startswith("http://"):
                    url = "https://" + url[len("http://") :]
                response = httpx.get(url, headers=self._headers(), params=next_params)
                response.raise_for_status()
                data = response.json()
                items = (
                    data["results"]
                    if isinstance(data, dict) and "results" in data
                    else data
                )
                all_items.extend(
                    [self._parse_metaculus_comment(item) for item in items]
                )
                next_url: Optional[str] = data.get("next", None)
                if next_url is not None:
                    if next_url.startswith("http://"):
                        next_url = "https://" + next_url[len("http://") :]
                    parsed = urllib.parse.urlparse(next_url)
                    query: Dict[str, str] = dict(urllib.parse.parse_qsl(parsed.query))
                    if params:
                        for k, v in params.items():
                            if k not in query:
                                query[k] = str(v)
                    query_str = {}
                    for k, v in query.items():
                        if v is not None:
                            query_str[str(k)] = str(v)
                    query_str = cast(Dict[str, str], query_str)
                    url = str(
                        parsed._replace(
                            query=urllib.parse.urlencode(query_str)
                        ).geturl()
                    )
                    next_params = None
                else:
                    url = None
            except Exception as e:
                print(f"[Metaculus] Error fetching comments: {e}")
                break
        return all_items

    def list_metaculus_comments_for_question(
        self,
        question_id: int,
        params: Optional[Mapping[str, Union[str, int, float, bool, None]]] = None,
    ) -> list:
        """Fetch all comments for a given Metaculus question by id. Returns List[MetaculusComment]."""
        q = self.get_question(str(question_id))
        # Always work with a dict for 'raw'
        raw = (
            q.raw
            if hasattr(q, "raw") and isinstance(q.raw, dict)
            else q if isinstance(q, dict) else {}
        )
        post_id = (
            raw.get("post_id")
            or raw.get("post")
            or (
                raw.get("question", {}).get("post_id")
                if isinstance(raw.get("question", {}), dict)
                else None
            )
            or (
                raw.get("question", {}).get("id")
                if isinstance(raw.get("question", {}), dict)
                else None
            )
            or raw.get("id")
        )
        if not post_id:
            print(f"[Metaculus] Could not resolve post id for question {question_id}")
            return []
        params_dict: Dict[str, Union[str, int, float, bool, None]] = (
            dict(params) if params else {}
        )
        params_dict.pop("question", None)
        if not isinstance(post_id, int) and str(post_id).isdigit():
            params_dict["post"] = int(post_id)
        else:
            params_dict["post"] = post_id
        return self.list_metaculus_comments(params=params_dict)

    def list_series(self, params: Optional[dict] = None):
        return self.list_resource("series", params=params or {})

    def list_predictions(self, params: Optional[dict] = None):
        return self.list_resource("predictions", params=params or {})

    def list_groups(self, params: Optional[dict] = None):
        return self.list_resource("groups", params=params or {})

    def _parse_date(self, s):
        if not s:
            return None
        try:
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None

    def _parse_metaculus_comment(self, item: dict) -> MetaculusComment:
        def parse_author(a):
            return (
                MetaculusCommentAuthor(
                    id=a.get("id"),
                    is_staff=a.get("is_staff", False),
                    username=a.get("username"),
                    is_bot=a.get("is_bot", False),
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

    def _parse_metaculus_question(self, item: dict) -> MetaculusForecastQuestion:
        """Instance method to parse a question dict into a MetaculusForecastQuestion."""
        return self._parse_metaculus_question_static(item)
