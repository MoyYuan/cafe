from datetime import datetime
from typing import Any, Callable, List, Optional


def filter_questions_by_metadata(
    questions: List[dict],
    filters: Optional[dict] = None,
    has_resolution_criteria: Optional[bool] = None,
    min_comments: Optional[int] = None,
    tag: Optional[str] = None,
    custom_predicate: Optional[Callable[[dict], bool]] = None,
) -> List[dict]:
    """
    Filter a list of MetaculusForecastQuestion objects by various metadata fields.
    Args:
        questions: List of questions to filter.
        filters: Optional dict of filters (e.g., {'published_at__gt': ..., 'status': ...}).
        has_resolution_criteria: If set, include only questions with (or without) resolution criteria.
        min_comments: If set, include only questions with at least this many comments (if comments attribute exists).
        tag: If set, include only questions with this tag.
        custom_predicate: If set, include only questions for which this function returns True.
    Returns:
        Filtered list of questions.
    """
    filtered = []
    for q in questions:
        # Example: apply published_at__gt filter if present
        if filters:
            if "published_at__gt" in filters:
                published_at = q.get("published_at")
                if published_at and published_at < filters["published_at__gt"]:
                    continue
            if "published_at__lt" in filters:
                published_at = q.get("published_at")
                if published_at and published_at > filters["published_at__lt"]:
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
