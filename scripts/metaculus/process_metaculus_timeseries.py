import argparse

from cafe.sources.processing import metaculus as mproc


def main():
    parser = argparse.ArgumentParser(
        description="Process Metaculus questions/comments into time series with comments attached to forecast states."
    )
    parser.add_argument(
        "--questions", type=str, required=True, help="Path to questions JSON file"
    )
    parser.add_argument(
        "--comments",
        type=str,
        required=True,
        help="Path to comments (JSON file or directory)",
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Path to output time series JSON file"
    )
    parser.add_argument(
        "--status",
        type=str,
        default=None,
        help="Filter questions by status (e.g., open, resolved)",
    )
    parser.add_argument("--tag", type=str, default=None, help="Filter questions by tag")
    parser.add_argument(
        "--min-forecasters",
        type=int,
        default=None,
        help="Filter questions by minimum number of forecasters",
    )

    parser.add_argument(
        "--has-resolution-criteria",
        action="store_true",
        help="Filter questions to only those with resolution criteria",
    )
    parser.add_argument(
        "--min-comments",
        type=int,
        default=None,
        help="Filter questions by minimum number of comments (if available)",
    )
    parser.add_argument(
        "--filter",
        action="append",
        default=[],
        help="Additional filters as key=value (e.g., published_at__gt=2023-10-01). Can be specified multiple times.",
    )
    args = parser.parse_args()

    # Parse --filter arguments into a dict
    filters_dict = {}
    for f in args.filter:
        if "=" not in f:
            raise ValueError(f"Invalid filter: {f}. Expected key=value format.")
        k, v = f.split("=", 1)
        filters_dict[k] = v

    questions = mproc.load_questions(args.questions)
    comments = mproc.load_comments(args.comments)

    # Count total comments loaded
    total_comments_loaded = sum(len(v) for v in comments.values())

    filtered = mproc.filter_questions(
        questions,
        status=args.status,
        tag=args.tag,
        min_forecasters=args.min_forecasters,
        has_resolution_criteria=(
            args.has_resolution_criteria if args.has_resolution_criteria else None
        ),
        min_comments=args.min_comments,
        filters=filters_dict if filters_dict else None,
    )
    print(
        f"Loaded {len(questions)} questions, {len(filtered)} after filtering.\nNOTE: Date filtering is now supported via --filter key=value (e.g., --filter published_at__gt=YYYY-MM-DD)"
    )
    series = mproc.link_comments_to_forecasts(filtered, comments)

    # Count total comments linked to any forecast timestamp
    total_comments_linked = 0
    for ts_list in series.values():
        for entry in ts_list:
            total_comments_linked += len(entry.get("comments", []))

    print(f"Total comments loaded: {total_comments_loaded}")
    print(f"Total comments linked to a forecast timestamp: {total_comments_linked}")

    # Debug: print a sample of linked comments
    sample_printed = False
    for qid, ts_list in series.items():
        for entry in ts_list:
            if entry.get("comments"):
                print(
                    f"Sample: QID={qid}, Forecast timestamp={entry['timestamp']}, Comments attached={len(entry['comments'])}"
                )
                print(f"First comment: {entry['comments'][0]}")
                sample_printed = True
                break
        if sample_printed:
            break
    if not sample_printed:
        print("No comments found attached to any forecast snapshot in memory.")

    mproc.export_time_series_with_comments(
        series,
        args.output,
        params={
            "questions": args.questions,
            "comments": args.comments,
            "status": args.status,
            "tag": args.tag,
            "min_forecasters": args.min_forecasters,
            "has_resolution_criteria": args.has_resolution_criteria,
            "min_comments": args.min_comments,
            "filters": filters_dict,
        },
        questions=filtered,
    )
    print(f"Exported time series with comments (with metadata) to {args.output}")


if __name__ == "__main__":
    main()
