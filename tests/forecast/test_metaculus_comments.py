import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("METACULUS_API_KEY"),
    reason="Metaculus API key not set; skipping live API tests.",
)

from cafe.forecast.source_metaculus import MetaculusForecastSource


def test_metaculus_comments_placeholder():
    assert True  # placeholder test


def test_list_metaculus_comments_for_question():
    src = MetaculusForecastSource.from_env()
    # Use a known question id, or fallback to a question from the API
    questions = src.list_questions()
    if not questions:
        print("No questions available.")
        assert False
    qid = questions[0].id if hasattr(questions[0], "id") else questions[0]["id"]
    comments = src.list_metaculus_comments_for_question(qid)
    if comments is None:
        print(f"No comments found for question id {qid}.")
        return
    print(f"Fetched {len(comments)} comments for question id {qid}.")
    for c in comments[:3]:
        print(f"Comment id={c.id}, author={c.author.username}, text={c.text[:40]}...")
    assert isinstance(comments, list)
