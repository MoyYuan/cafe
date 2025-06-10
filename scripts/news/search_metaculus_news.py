import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from cafe.news.google import GoogleNewsFetcher

def process_all_questions_with_comments(json_path, days=7, output_path="metaculus_news_results.json", cache_path="metaculus_news_cache.json"):
    import os
    from tqdm import tqdm
    # Load cache if exists
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            cache = json.load(f)
    else:
        cache = {}

    with open(json_path, "r") as f:
        data = json.load(f)
    questions = data.get("questions")
    if isinstance(questions, dict):
        questions_iter = questions.values()
    elif isinstance(questions, list):
        questions_iter = questions
    else:
        raise ValueError("Unrecognized questions structure in JSON.")

    fetcher = GoogleNewsFetcher()
    results = []
    for question in tqdm(questions_iter, desc="Questions"):
        qid = str(question.get("id"))
        title = question.get("metadata", {}).get("title")
        series = question.get("series", [])
        for entry in series:
            comments = entry.get("comments", [])
            for comment in comments:
                comment_id = str(comment.get("id"))
                created_at = comment.get("created_at")
                if not (title and created_at):
                    continue
                cache_key = f"{qid}:{comment_id}"
                if cache_key in cache:
                    news_results = cache[cache_key]
                    print(f"[CACHE] Hit for QID {qid} | Comment {comment_id}")
                else:
                    end_date = datetime.fromisoformat(created_at.replace("Z", ""))
                    start_date = end_date - timedelta(days=days)
                    print(f"[INFO] Searching news for QID {qid} | Comment {comment_id} | Title: {title}")
                    news_results = fetcher.fetch_news(
                        query=title,
                        start_date=str(start_date.date()),
                        end_date=str(end_date.date()),
                        max_results=5,
                    )
                    cache[cache_key] = news_results
                    # Write cache after each new fetch
                    with open(cache_path, "w") as cf:
                        json.dump(cache, cf)
                    import time
                    time.sleep(0.7)  # Google API rate limit: 100 requests/minute
                results.append({
                    "question_id": qid,
                    "comment_id": comment_id,
                    "title": title,
                    "created_at": created_at,
                    "news_results": news_results,
                })
    print(f"[INFO] Saving all news results to {output_path}")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print("[INFO] Done.")

def main(json_path, days=7, output_path="metaculus_news_results.json"):
    process_all_questions_with_comments(json_path, days, output_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_metaculus_news.py <path_to_json> [days] [output_path]")
        sys.exit(1)
    json_path = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    output_path = sys.argv[3] if len(sys.argv) > 3 else "metaculus_news_results.json"
    main(json_path, days, output_path)
