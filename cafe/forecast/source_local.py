import json
from datetime import datetime
from typing import List

from .comment import (MetaculusChangedMyMind, MetaculusComment,
                      MetaculusCommentAuthor, MetaculusMentionedUser)
from .question import MetaculusForecastQuestion
from .source_base import ForecastSourceBase


class LocalForecastCommentSource:
    def __init__(self, path: str):
        self.path = path

    def list_comments_for_question(self, question_id: str) -> List[MetaculusComment]:
        with open(self.path, "r") as f:
            data = json.load(f)
        return [
            self._parse_comment(item)
            for item in data
            if str(item.get("on_post")) == str(question_id)
        ]

    def get_comment(self, comment_id: int) -> MetaculusComment:
        with open(self.path, "r") as f:
            data = json.load(f)
        for item in data:
            if int(item.get("id")) == int(comment_id):
                return self._parse_comment(item)
        raise ValueError(f"Comment with id {comment_id} not found.")

    def _parse_comment(self, item: dict) -> MetaculusComment:
        author = item.get("author", {})
        if not author:
            author = {"id": -1, "username": "unknown"}
        mentioned_users = (
            [MetaculusMentionedUser(**u) for u in item.get("mentioned_users", [])]
            if item.get("mentioned_users")
            else None
        )
        changed_my_mind = (
            MetaculusChangedMyMind(**item["changed_my_mind"])
            if item.get("changed_my_mind")
            else None
        )
        created_at = (
            datetime.fromisoformat(item["created_at"])
            if item.get("created_at")
            else datetime(1970, 1, 1)
        )
        on_post = int(item["on_post"]) if item.get("on_post") is not None else -1
        return MetaculusComment(
            id=int(item["id"]),
            author=MetaculusCommentAuthor(**author),
            parent_id=item.get("parent_id"),
            root_id=item.get("root_id"),
            created_at=created_at,
            text=item.get("text", ""),
            on_post=on_post,
            included_forecast=item.get("included_forecast"),
            is_private=item.get("is_private"),
            vote_score=item.get("vote_score"),
            changed_my_mind=changed_my_mind,
            mentioned_users=mentioned_users,
            user_vote=item.get("user_vote"),
            raw=item,
        )


class LocalForecastSource(ForecastSourceBase):
    def __init__(self, path: str):
        self.path = path

    def list_questions(self) -> List[MetaculusForecastQuestion]:
        with open(self.path, "r") as f:
            data = json.load(f)
        return [self._parse_question(item) for item in data]

    def get_question(self, id: str) -> MetaculusForecastQuestion:
        with open(self.path, "r") as f:
            data = json.load(f)
        for item in data:
            if str(item.get("id")) == str(id):
                return self._parse_question(item)
        raise ValueError(f"Question with id {id} not found.")

    def _parse_question(self, item: dict) -> MetaculusForecastQuestion:
        return MetaculusForecastQuestion(
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
