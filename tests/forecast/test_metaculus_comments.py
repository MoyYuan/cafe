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
    # Test with a known question id that should have >20 comments
    qid = "36934"
    comments = src.list_metaculus_comments_for_question(qid)
    assert isinstance(comments, list)
    print(f"Fetched {len(comments)} comments for question id {qid}.")
    for c in comments[:3]:
        print(f"Comment id={c.id}, author={c.author.username}, text={c.text[:40]}...")
    assert len(comments) > 20, f"Expected >20 comments, got {len(comments)}"
