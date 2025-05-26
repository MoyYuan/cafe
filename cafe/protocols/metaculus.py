import os
import json
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from cafe.forecast.source_metaculus import MetaculusForecastSource
from cafe.forecast.comment import MetaculusComment
from cafe.forecast.question import MetaculusForecastQuestion

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
def get_metaculus_questions(force_refresh: bool = False):
    """
    Returns Metaculus questions. If force_refresh is True, fetch from API and overwrite local cache.
    Otherwise, load from local if available, else fetch from API and save.
    """
    local_path = MetaculusForecastSource.DATA_FILE
    if not force_refresh and os.path.exists(local_path):
        src = LocalForecastSource(local_path)
        questions = src.list_questions()
    else:
        src = MetaculusForecastSource()
        questions = src.list_questions()
        # Save to cache
        MetaculusForecastSource.save_questions_to_json(questions, filepath=local_path)
    return [MetaculusQuestionOut(
        id=q.id,
        title=q.title,
        description=q.description,
        url=q.url,
        tags=q.tags,
    ) for q in questions]

@router.get("/metaculus/questions/{question_id}/comments", response_model=List[MetaculusCommentOut])
def get_metaculus_comments_for_question(question_id: str, force_refresh: bool = False):
    """
    Returns comments for a Metaculus question. If force_refresh is True, fetch from API and overwrite local cache.
    Otherwise, load from local if available, else fetch from API and save.
    """
    from cafe.forecast.source_local import LocalForecastCommentSource
    comment_cache_dir = MetaculusForecastSource.DATA_DIR
    os.makedirs(comment_cache_dir, exist_ok=True)
    local_path = os.path.join(comment_cache_dir, f"metaculus_comments_{question_id}.json")
    if not force_refresh and os.path.exists(local_path):
        src = LocalForecastCommentSource(local_path)
        comments = src.list_comments_for_question(question_id)
    else:
        src = MetaculusForecastSource()
        comments = src.list_metaculus_comments_for_question(question_id)
        if comments is None:
            raise HTTPException(status_code=404, detail=f"No comments found for question {question_id}")
        # Save to cache as list of dicts
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump([c.raw for c in comments], f, ensure_ascii=False, indent=2)
    return [MetaculusCommentOut(
        id=c.id,
        text=c.text,
        author=c.author.username if c.author else None,
        created_at=c.created_at.isoformat() if c.created_at else None,
        vote_score=c.vote_score,
    ) for c in comments]
