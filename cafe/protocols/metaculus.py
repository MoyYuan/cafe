import json
import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from cafe.forecast.comment import MetaculusComment
from cafe.forecast.question import MetaculusForecastQuestion
from cafe.forecast.source_metaculus import MetaculusForecastSource

router = APIRouter()


class MetaculusQuestionOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    url: Optional[str]
    tags: List[str] = []


class MetaculusCommentOut(BaseModel):
    id: int
    text: str
    author: Optional[str]
    created_at: Optional[str]
    vote_score: Optional[int]


from cafe.forecast.source_local import LocalForecastSource


@router.get("/metaculus/questions", response_model=List[MetaculusQuestionOut])
def get_metaculus_questions(
    force_refresh: bool = False, questions_cache_path: Optional[str] = None
):
    """
    Returns Metaculus questions. If force_refresh is True, fetch from API and overwrite local cache.
    Otherwise, load from local if available, else fetch from API and save.
    Optionally override the questions cache file path with ?questions_cache_path=...
    """
    default_path = os.path.join(
        "data", "forecasts", "metaculus", "questions_cache.json"
    )
    local_path = questions_cache_path or default_path
    if not force_refresh and os.path.exists(local_path):
        with open(local_path, "r") as f:
            questions_data = json.load(f)
        # If the cache contains dicts, convert to MetaculusForecastQuestion objects if needed
        questions = [LocalForecastSource("")._parse_question(q) for q in questions_data]
    else:
        questions = MetaculusForecastSource().list_questions()
        # Save to cache
        with open(local_path, "w") as f:
            json.dump(
                [q.raw if hasattr(q, "raw") else q for q in questions], f, indent=2
            )
    return [
        MetaculusQuestionOut(
            id=str(q.id),
            title=q.title,
            description=q.description,
            url=q.url,
            tags=q.tags,
        )
        for q in questions
    ]


@router.get(
    "/metaculus/questions/{question_id}/comments",
    response_model=List[MetaculusCommentOut],
)
def get_metaculus_comments_for_question(
    question_id: str,
    force_refresh: bool = False,
    comments_cache_path: Optional[str] = None,
):
    """
    Returns comments for a Metaculus question. If force_refresh is True, fetch from API and overwrite local cache.
    Otherwise, load from local if available, else fetch from API and save.
    Optionally override the comments cache file path with ?comments_cache_path=...
    """
    from cafe.forecast.source_local import LocalForecastCommentSource

    import os
    default_comments_dir = os.path.join(
        "data", "forecasts", "metaculus", "comments_by_question"
    )
    os.makedirs(default_comments_dir, exist_ok=True)
    local_path = comments_cache_path or os.path.join(
        default_comments_dir, f"{question_id}.json"
    )
    # PROTECT: Never allow tests to write to production comments dir
    if (
        os.environ.get("PYTEST_CURRENT_TEST")
        and default_comments_dir in local_path
        and "/tmp" not in local_path
    ):
        raise RuntimeError(
            f"Test attempted to access production comments cache: {local_path}. "
            "Patch your test to use a temporary comments_cache_path!"
        )
    if not force_refresh and os.path.exists(local_path):
        with open(local_path, "r") as f:
            comments_data = json.load(f)
        comments = [
            LocalForecastCommentSource("")._parse_comment(c) for c in comments_data
        ]
    else:
        comments = MetaculusForecastSource().list_metaculus_comments_for_question(
            int(question_id)
        )
        # Save to cache
        with open(local_path, "w") as f:
            json.dump(
                [c.raw if hasattr(c, "raw") else c for c in comments], f, indent=2
            )
    return [
        MetaculusCommentOut(
            id=c.id,
            text=c.text,
            author=c.author.username if c.author else None,
            created_at=c.created_at.isoformat() if c.created_at else None,
            vote_score=c.vote_score,
        )
        for c in comments
    ]
