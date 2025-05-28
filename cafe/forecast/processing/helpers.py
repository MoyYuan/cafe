from datetime import datetime
from typing import List, Optional, Callable, Any

from cafe.forecast.question import MetaculusForecastQuestion

def filter_questions_by_metadata(
    questions: List[MetaculusForecastQuestion],
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    has_resolution_criteria: Optional[bool] = None,
    min_comments: Optional[int] = None,
    tag: Optional[str] = None,
    custom_predicate: Optional[Callable[[MetaculusForecastQuestion], bool]] = None,
) -> List[MetaculusForecastQuestion]:
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
        if created_after and (not q.created_at or q.created_at < created_after):
            continue
        if created_before and (not q.created_at or q.created_at > created_before):
            continue
        if has_resolution_criteria is not None and bool(q.resolution_criteria) != has_resolution_criteria:
            continue
        if min_comments is not None and hasattr(q, "comments") and len(getattr(q, "comments", [])) < min_comments:
            continue
        if tag and (not q.tags or tag not in q.tags):
            continue
        if custom_predicate and not custom_predicate(q):
            continue
        filtered.append(q)
    return filtered
