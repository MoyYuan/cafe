import argparse
import json
import sys
from pathlib import Path

import httpx

from cafe.forecast.processing.metadata import get_metadata
from cafe.forecast.source_metaculus import MetaculusForecastSource


def save_questions_and_comments(
    questions, comments_by_qid, out_dir, after, comments_mode="all-in-one", params=None
):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # Prepare metadata
    script = sys.argv[0]
    q_metadata = get_metadata(
        script=script,
        params=params or {},
        api_endpoint="https://www.metaculus.com/api2/questions/",
        record_count=len(questions),
    )
    # Save questions with metadata
    qfile = out_dir / f"questions_{after}.json"
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
        cfile = out_dir / f"comments_{after}.json"
        with cfile.open("w") as f:
            json.dump(
                {
                    "metadata": c_metadata,
                    "comments_by_question": {
                        str(qid): [c.raw if hasattr(c, "raw") else c for c in clist]
                        for qid, clist in comments_by_qid.items()
                    },
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
                api_endpoint=f"https://www.metaculus.com/api2/questions/{qid}/comments/",
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
    import time

    parser = argparse.ArgumentParser(
        description="Fetch Metaculus questions and their comments after a given date."
    )
    parser.add_argument(
        "--after",
        type=str,
        default="2023-10-01",
        help="Fetch questions created after this date (YYYY-MM-DD)",
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
        "--resume",
        action="store_true",
        help="Resume from last checkpoint if available (global shortcut).",
    )
    parser.add_argument(
        "--resume-questions",
        action="store_true",
        help="Resume questions fetching from last checkpoint.",
    )
    parser.add_argument(
        "--resume-comments",
        action="store_true",
        help="Resume comments fetching from last checkpoint.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of questions to fetch/process.",
    )
    args = parser.parse_args()

    src = MetaculusForecastSource()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_questions_file = out_dir / "questions_cache.json"
    comments_dir = out_dir / "comments_by_question"
    comments_dir.mkdir(exist_ok=True)
    checkpoint_file = out_dir / "fetch_checkpoint.json"

    questions = []
    fetched_qids = set()
    # Determine question cache/refresh/resume modes
    refresh_questions = args.refresh or args.refresh_questions
    resume_questions = args.resume or args.resume_questions
    # Load cache if allowed and available
    if not args.no_cache and cache_questions_file.exists() and not refresh_questions:
        with cache_questions_file.open() as f:
            questions = json.load(f)
        fetched_qids = set(str(q.get("id")) for q in questions)
        print(f"Loaded {len(questions)} questions from cache.")
    else:
        print("Not using questions cache (refresh or no cache mode).")

    # Resume support: load checkpoint
    resume_page = 0
    if resume_questions and checkpoint_file.exists():
        with checkpoint_file.open() as f:
            checkpoint = json.load(f)
            resume_page = checkpoint.get("page", 0)
            print(f"Resuming questions fetching from checkpoint: page {resume_page}")

    params = {
        "created_time__gt": f"{args.after}T00:00:00Z",
        "limit": 100,  # Metaculus API max page size (adjust if API changes)
    }
    page = 0
    all_questions = questions.copy()
    next_url = None
    while True:
        if page < resume_page:
            page += 1
            continue
        if next_url:
            if next_url.startswith("http://"):
                next_url = "https://" + next_url[len("http://") :]
            resp = httpx.get(next_url, headers=src._headers())
            resp.raise_for_status()
            data = resp.json()
        else:
            base_url = src.base_url
            if base_url.startswith("http://"):
                base_url = "https://" + base_url[len("http://") :]
            data = httpx.get(base_url, headers=src._headers(), params=params).json()
        items = (
            data["results"] if isinstance(data, dict) and "results" in data else data
        )
        if not items:
            break
        # Only add new questions
        new_questions = [q for q in items if str(q.get("id")) not in fetched_qids]
        all_questions.extend(new_questions)
        fetched_qids.update(str(q.get("id")) for q in new_questions)
        if args.limit is not None and len(all_questions) >= args.limit:
            all_questions = all_questions[: args.limit]
            if not args.no_cache:
                with cache_questions_file.open("w") as f:
                    json.dump(all_questions, f, indent=2)
            # Save checkpoint
            with checkpoint_file.open("w") as f:
                json.dump({"page": page}, f)
            break
        if not args.no_cache:
            with cache_questions_file.open("w") as f:
                json.dump(all_questions, f, indent=2)
        # Save checkpoint
        with checkpoint_file.open("w") as f:
            json.dump({"page": page}, f)
        # Pagination
        next_url = data.get("next") if isinstance(data, dict) else None
        page += 1
        if not next_url:
            break
        time.sleep(0.2)  # Be nice to API
    if not all_questions:
        print("No questions found.")
        return
    # Apply limit if set
    if args.limit is not None:
        all_questions = all_questions[: args.limit]

    # Determine comments cache/refresh/resume modes
    refresh_comments = args.refresh or args.refresh_comments
    resume_comments = args.resume or args.resume_comments
    # Fetch comments, using cache if available
    comments_by_qid = {}
    for q in all_questions:
        qid = str(q.get("id"))
        comment_file = comments_dir / f"{qid}.json"
        comments = None
        if not args.no_cache and comment_file.exists() and not refresh_comments:
            with comment_file.open() as f:
                loaded = json.load(f)
                if isinstance(loaded, dict) and "data" in loaded:
                    comments = loaded["data"]
                else:
                    comments = loaded
        else:
            comments = [
                c.raw if hasattr(c, "raw") else c
                for c in src.list_metaculus_comments_for_question(qid) or []
            ]
            if not args.no_cache or refresh_comments:
                c_metadata = {
                    "qid": qid,
                    "comment_count": len(comments),
                }
                with comment_file.open("w") as f:
                    json.dump({"metadata": c_metadata, "data": comments}, f, indent=2)
        comments_by_qid[qid] = comments
    if refresh_comments:
        print("Comments: forced refresh mode (ignore cache).")
    elif not args.no_cache:
        print("Comments: using cache if available.")
    else:
        print("Comments: not using cache (no-cache mode).")
        if args.verbose and comments:
            for c in comments:
                print("  -", c)
    print(
        f"\nSaving to {args.output_dir} (questions + comments, mode: {args.comments_mode})..."
    )
    save_questions_and_comments(
        all_questions,
        comments_by_qid,
        args.output_dir,
        args.after,
        args.comments_mode,
        params=params,
    )
    print("Done.")


if __name__ == "__main__":
    main()
