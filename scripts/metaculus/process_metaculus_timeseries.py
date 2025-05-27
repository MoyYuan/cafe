import argparse

from cafe.forecast.processing import metaculus as mproc


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
    args = parser.parse_args()

    questions = mproc.load_questions(args.questions)
    comments = mproc.load_comments(args.comments)
    filtered = mproc.filter_questions(
        questions,
        status=args.status,
        tag=args.tag,
        min_forecasters=args.min_forecasters,
    )
    print(f"Loaded {len(questions)} questions, {len(filtered)} after filtering.")
    series = mproc.link_comments_to_forecasts(filtered, comments)
    mproc.export_time_series_with_comments(
        series,
        args.output,
        params={
            "questions": args.questions,
            "comments": args.comments,
            "status": args.status,
            "tag": args.tag,
            "min_forecasters": args.min_forecasters,
        },
        questions=filtered,
    )
    print(f"Exported time series with comments (with metadata) to {args.output}")


if __name__ == "__main__":
    main()
