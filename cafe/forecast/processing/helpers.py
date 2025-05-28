from datetime import datetime
from typing import Any, Callable, List, Optional


def filter_questions_by_metadata(
    questions: List[dict],
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    has_resolution_criteria: Optional[bool] = None,
    min_comments: Optional[int] = None,
    tag: Optional[str] = None,
    custom_predicate: Optional[Callable[[dict], bool]] = None,
) -> List[dict]:
    """
    Filter a list of MetaculusForecastQuestion objects by various metadata fields.
    Args:
        questions: List of questions to filter.
        created_after: Only include questions created after this datetime.
        created_before: Only include questions created before this datetime.
        has_resolution_criteria: If set, include only questions with (or without) resolution criteria.
        min_comments: If set, include only questions with at least this many comments (if comments attribute exists).
        tag: If set, include only questions with this tag.
        custom_predicate: If set, include only questions for which this function returns True.
    Returns:
        Filtered list of questions.
    """
    filtered = []
    for q in questions:
        created_at = q.get("created_at")
        if created_after:
            if (
                created_at is None
                or not isinstance(created_at, datetime)
                or created_at < created_after
            ):
                continue
        if created_before:
            if (
                created_at is None
                or not isinstance(created_at, datetime)
                or created_at > created_before
            ):
                continue
        if (
            has_resolution_criteria is not None
            and bool(q.get("resolution_criteria")) != has_resolution_criteria
        ):
            continue
        if min_comments is not None and len(q.get("comments", [])) < min_comments:
            continue
        tags = q.get("tags")
        if tag:
            if not tags or not isinstance(tags, list) or tag not in tags:
                continue
        if custom_predicate and not custom_predicate(q):
            continue
        filtered.append(q)
    return filtered
