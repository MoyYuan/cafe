import bisect
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .metadata import get_metadata


def load_questions(path: Union[str, Path]) -> List[dict]:
    path = Path(path)
    with path.open("r") as f:
        obj = json.load(f)
        if isinstance(obj, dict) and "data" in obj:
            return obj["data"]
        return obj


def load_comments(path: Union[str, Path]) -> Dict[str, Any]:
    path = Path(path)
    if path.is_file():
        with path.open("r") as f:
            obj = json.load(f)
            if isinstance(obj, dict) and "comments_by_question" in obj:
                return obj["comments_by_question"]
            return obj
    elif path.is_dir():
        result: Dict[str, Any] = {}
        for file in path.glob("*.json"):
            with file.open("r") as f:
                obj = json.load(f)
                if isinstance(obj, dict) and "data" in obj:
                    result[file.stem] = obj["data"]
                elif isinstance(obj, dict) and "comments_by_question" in obj:
                    result[file.stem] = obj["comments_by_question"]
                else:
                    result[file.stem] = obj
        return result
    else:
        raise FileNotFoundError(f"No such file or directory: {path}")


from .helpers import filter_questions_by_metadata


def filter_questions(
    questions: list,
    status: Optional[str] = None,
    tag: Optional[str] = None,
    min_forecasters: Optional[int] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    has_resolution_criteria: Optional[bool] = None,
    min_comments: Optional[int] = None,
    custom_predicate: Optional[Callable[[dict], bool]] = None,
) -> list:
    """
    Filter questions by status, tag, min_forecasters, and metadata fields.
    Dates should be in ISO format (YYYY-MM-DD).
    """
    from datetime import datetime

    # Parse date strings if provided
    created_after_dt = datetime.fromisoformat(created_after) if created_after else None
    created_before_dt = (
        datetime.fromisoformat(created_before) if created_before else None
    )
    # Filter by direct fields first, then metadata
    filtered = []
    for q in questions:
        if status and q.get("status") != status:
            continue
        if tag and tag not in (q.get("tags") or []):
            continue
        if min_forecasters:
            fc = q.get("community_prediction", {}).get("num_forecasters")
            if fc is None or fc < min_forecasters:
                continue
        filtered.append(q)
    # Now apply metadata-based filtering
    filtered = filter_questions_by_metadata(
        filtered,
        created_after=created_after_dt,
        created_before=created_before_dt,
        has_resolution_criteria=has_resolution_criteria,
        min_comments=min_comments,
        tag=tag,
        custom_predicate=custom_predicate,
    )
    return filtered


def parse_time(s: str) -> float:
    # Handles both ISO and float timestamps
    try:
        return float(s)
    except Exception:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def link_comments_to_forecasts(
    questions: List[dict], comments_by_qid: Dict[str, List[dict]]
) -> Dict[str, List[dict]]:
    """
    For each question, create a time series where each entry is:
      {
        'timestamp': ...,
        'forecast': ...,
        'comments': [ ... ]
      }
    Comments are attached to the nearest (not after) forecast snapshot.
    """
    result = {}
    for q in questions:
        qid = str(q.get("id"))
        # Extract forecast time series (support both legacy and real Metaculus schema)
        forecasts = q.get("community_prediction", {}).get("history")
        if forecasts is None:
            # Try real Metaculus export structure
            forecasts = (
                q.get("question", {})
                .get("aggregations", {})
                .get("recency_weighted", {})
                .get("history", [])
            )
        # Defensive: ensure forecasts is a list
        if not isinstance(forecasts, list):
            forecasts = []
        # Build list of (timestamp, forecast_dict), filter out null end_time
        forecast_times = [
            f["end_time"]
            for f in forecasts
            if "end_time" in f and f["end_time"] is not None
        ]
        time_series = [
            {"timestamp": f.get("end_time"), "forecast": f, "comments": []}
            for f in forecasts
            if "end_time" in f and f["end_time"] is not None
        ]
        # Attach comments
        comments = comments_by_qid.get(qid, [])
        for c in comments:
            ctime = parse_time(c["created_at"])
            # Find the right forecast snapshot (not after comment)
            idx = bisect.bisect_right(forecast_times, ctime) - 1
            if idx >= 0:
                time_series[idx]["comments"].append(c)
        result[qid] = time_series
    return result


def extract_question_metadata(q: dict) -> dict:
    # Try to get metadata from both legacy and real Metaculus schema
    qdata = q.get("question", q)
    return {
        "id": qdata.get("id"),
        "title": qdata.get("title"),
        "description": qdata.get("description"),
        "created_at": qdata.get("created_at") or qdata.get("created_time"),
        "open_time": qdata.get("open_time"),
        "cp_reveal_time": qdata.get("cp_reveal_time"),
        "scheduled_resolve_time": qdata.get("scheduled_resolve_time"),
        "actual_resolve_time": qdata.get("actual_resolve_time"),
        "scheduled_close_time": qdata.get("scheduled_close_time"),
        "actual_close_time": qdata.get("actual_close_time"),
        "type": qdata.get("type"),
        "status": qdata.get("status"),
        "tags": qdata.get("tags"),
        "url": qdata.get("url"),
        "resolution_criteria": qdata.get("resolution_criteria"),
        "fine_print": qdata.get("fine_print"),
        "unit": qdata.get("unit"),
        "possibilities": qdata.get("possibilities"),
        "options": qdata.get("options"),
        "group_variable": qdata.get("group_variable"),
        "include_bots_in_aggregates": qdata.get("include_bots_in_aggregates"),
        "question_weight": qdata.get("question_weight"),
        "default_project": qdata.get("default_project"),
    }


def export_time_series_with_comments(
    series_by_qid: Dict[str, List[dict]],
    out_file: str,
    params: Optional[dict] = None,
    questions: Optional[List[Any]] = None,
):
    script = sys.argv[0]
    meta = get_metadata(
        script=script,
        params=params or {},
        record_count=sum(len(v) for v in series_by_qid.values()),
    )
    # Build mapping from qid to question for metadata extraction
    qid_to_question = {str(q.get("id")): q for q in (questions or [])}
    output = {}
    for qid, series in series_by_qid.items():
        qmeta = extract_question_metadata(qid_to_question.get(qid, {}))
        output[qid] = {"metadata": qmeta, "series": series}
    with open(out_file, "w") as f:
        json.dump(
            {"metadata": meta, "questions": output}, f, indent=2
        )  # indent=2 for readability
