import argparse
import json
import sys
from pathlib import Path

from cafe.sources.processing.metadata import get_metadata
from cafe.sources.source_metaculus import MetaculusForecastSource


def save_questions_and_comments(
    questions, comments_by_qid, out_dir, comments_mode="all-in-one", params=None
):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Prepare metadata
    script = sys.argv[0]
    q_metadata = get_metadata(
        script=script,
        params=params or {},
        api_endpoint="https://www.metaculus.com/api/posts/",
        record_count=len(questions),
    )
    # Choose a date string for the filename if present
    date_str = None
    for key in ["published_at__gt", "open_time__gt", "created_time__gt"]:
        if params and key in params:
            date_str = params[key]
            break
    if date_str is None:
        date_str = "latest"
    qfile = out_dir / f"questions_{date_str}.json"
    with qfile.open("w") as f:
        json.dump(
            {
                "metadata": q_metadata,
                "data": [q.raw if hasattr(q, "raw") else q for q in questions],
            },
            f,
            indent=2,
        )
    if comments_mode == "all-in-one":
        c_metadata = get_metadata(
            script=script,
            params=params or {},
            api_endpoint="https://www.metaculus.com/api2/comments/",
            record_count=sum(len(clist) for clist in comments_by_qid.values()),
        )
        cfile = out_dir / f"comments_{date_str}.json"
        with cfile.open("w") as f:
            json.dump(
                {
                    "metadata": c_metadata,
                    "data": comments_by_qid,
                },
                f,
                indent=2,
            )
    elif comments_mode == "per-question":
        comments_dir = out_dir / "comments_by_question"
        comments_dir.mkdir(exist_ok=True)
        for qid, clist in comments_by_qid.items():
            c_metadata = get_metadata(
                script=script,
                params={"question_id": qid, **(params or {})},
                api_endpoint=f"https://www.metaculus.com/api/comments/{qid}/",
                record_count=len(clist),
            )
            cfile = comments_dir / f"{qid}.json"
            with cfile.open("w") as f:
                json.dump(
                    {
                        "metadata": c_metadata,
                        "data": [c.raw if hasattr(c, "raw") else c for c in clist],
                    },
                    f,
                    indent=2,
                )  # Ensure indent=2 for readability
    else:
        raise ValueError(f"Unknown comments_mode: {comments_mode}")


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Metaculus questions and their comments with flexible filtering."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/forecasts/metaculus",
        help="Directory to save output files",
    )
    parser.add_argument(
        "--comments-mode",
        type=str,
        choices=["all-in-one", "per-question"],
        default="all-in-one",
        help="How to save comments: all-in-one file or per-question files",
    )
    parser.add_argument(
        "--filter",
        action="append",
        default=[],
        help="Add a filter as key=value (can be repeated)",
    )
    parser.add_argument(
        "--status",
        action="append",
        default=None,
        help="Question status to include (can be repeated or comma-separated, default: all statuses)",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print raw JSON for inspection"
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force re-fetch all data, ignore cache (global shortcut).",
    )
    parser.add_argument(
        "--refresh-questions",
        action="store_true",
        help="Force re-fetch questions, ignore questions cache.",
    )
    parser.add_argument(
        "--refresh-comments",
        action="store_true",
        help="Force re-fetch comments, ignore comments cache.",
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="Do not use or write cache at all."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of questions to fetch/process.",
    )

    args = parser.parse_args()

    # Parse filters from --filter key=value
    filters = {}
    for f in args.filter:
        if "=" not in f:
            print(f"Invalid filter: {f}")
            continue
        k, v = f.split("=", 1)
        filters[k] = v
    # Parse statuses from --status (support repeated and comma-separated)
    statuses = []
    if args.status:
        for s in args.status:
            statuses.extend([item.strip() for item in s.split(",") if item.strip()])
    if not statuses:
        statuses = ["upcoming", "closed", "resolved", "open"]
    filters["statuses"] = statuses

    src = MetaculusForecastSource()
    src.verbose = args.verbose  # Ensure deep verbose logging
    all_questions, comments_by_qid = src.fetch_and_cache_questions_and_comments(
        filters=filters,
        output_dir=args.output_dir,
        comments_mode=args.comments_mode,
        verbose=args.verbose,
        limit=args.limit,
        refresh_comments=args.refresh_comments,
        no_cache=args.no_cache,
    )

    # Hydrate with full forecast/aggregation fields from /api2/questions/{id}/
    print(
        "Hydrating questions with full forecast history from /api2/questions/{id}/ ..."
    )
    for q in all_questions:
        qid = getattr(q, "id", None) or q.get("id")
        if not qid:
            continue
        full = src.get_full_question_details_api2(qid)
        if full:
            # Merge in forecast/aggregation fields (community_prediction, metaculus_prediction, etc.)
            for key in [
                "community_prediction",
                "metaculus_prediction",
                "aggregations",
                "forecasts",
                "forecast_count",
            ]:
                if key in full:
                    (
                        setattr(q, key, full[key])
                        if hasattr(q, key)
                        else q.update({key: full[key]})
                    )

    # Always save after fetch (even if fetch_and_cache... already saves, this guarantees output)
    # All endpoints now use /api/posts/ and /api/comments/
    save_questions_and_comments(
        all_questions,
        comments_by_qid,
        args.output_dir,
        comments_mode=args.comments_mode,
    )

    print(
        f"Saved {len(all_questions)} questions and {sum(len(v) for v in comments_by_qid.values())} comments to {args.output_dir} (mode: {args.comments_mode})"
    )


if __name__ == "__main__":
    main()
