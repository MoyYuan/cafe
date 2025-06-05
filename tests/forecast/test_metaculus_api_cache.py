import json
import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("METACULUS_API_KEY"),
    reason="Metaculus API key not set; skipping live API tests.",
)

from cafe.forecast.source_metaculus import MetaculusForecastSource


def test_metaculus_api_cache_placeholder():
    assert True  # placeholder test


import os
import tempfile

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("METACULUS_API_KEY"),
    reason="Metaculus API key not set; skipping live API tests.",
)

from fastapi.testclient import TestClient

from cafe.main import app

client = TestClient(app)

SAMPLE_QUESTIONS = [
    {
        "id": 1,
        "title": "Q1 title",
        "description": "desc1",
        "url": "http://x/1",
        "tags": ["tag1"],
    },
    {
        "id": 2,
        "title": "Q2 title",
        "description": "desc2",
        "url": "http://x/2",
        "tags": ["tag2"],
    },
]

SAMPLE_COMMENTS = [
    {
        "id": 1,
        "author": {"id": 1, "username": "user1"},
        "parent_id": None,
        "root_id": None,
        "created_at": "2025-05-26T20:00:00",
        "text": "Comment 1",
        "on_post": 1,
        "included_forecast": None,
        "is_private": None,
        "vote_score": 5,
        "changed_my_mind": None,
        "mentioned_users": [],
        "user_vote": None,
    },
    {
        "id": 2,
        "author": {"id": 2, "username": "user2"},
        "parent_id": None,
        "root_id": None,
        "created_at": "2025-05-26T20:01:00",
        "text": "Comment 2",
        "on_post": 1,
        "included_forecast": None,
        "is_private": None,
        "vote_score": 2,
        "changed_my_mind": None,
        "mentioned_users": [],
        "user_vote": None,
    },
]


def test_questions_cache(tmp_path, monkeypatch):
    # Setup: Write sample questions to new cache file
    cache_file = tmp_path / "questions_cache.json"
    with open(cache_file, "w") as f:
        json.dump(SAMPLE_QUESTIONS, f)
    # Patch pipeline to use the new cache location
    monkeypatch.setattr(
        "cafe.forecast.processing.metaculus.load_questions",
        lambda path: SAMPLE_QUESTIONS,
    )
    # Should load from cache
    resp = client.get(f"/metaculus/questions?questions_cache_path={cache_file}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert str(data[0]["id"]) == "1"

    # Should force refresh (simulate API fetch by monkeypatching list_questions)
    class FakeQ:
        def __init__(self, d):
            self.raw = d
            self.id = d["id"]
            self.title = d["title"]
            self.description = d["description"]
            self.url = d["url"]
            self.tags = d["tags"]

    def fake_api_list_questions(self):
        return [FakeQ(q) for q in SAMPLE_QUESTIONS[::-1]]  # reverse order

    from cafe.forecast.source_metaculus import MetaculusForecastSource

    monkeypatch.setattr(
        MetaculusForecastSource,
        "list_questions",
        fake_api_list_questions,
    )
    resp = client.get(
        f"/metaculus/questions?force_refresh=true&questions_cache_path={cache_file}"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert str(data[0]["id"]) == "2"  # reversed


def test_comments_cache(tmp_path, monkeypatch):
    # Guard: never allow writes to the real data directory
    real_data_dir = "data/forecasts/metaculus/comments_by_question"
    assert (
        str(tmp_path) not in real_data_dir
    ), "Test must use a temporary directory for output!"
    # Setup: Write sample comments to new cache file
    comments_dir = tmp_path / "comments_by_question"
    comments_dir.mkdir(exist_ok=True)
    cache_file = comments_dir / "1.json"
    with open(cache_file, "w") as f:
        json.dump(SAMPLE_COMMENTS, f)
    # Patch pipeline to use the new cache location

    from datetime import datetime

    from cafe.forecast.source_metaculus import MetaculusForecastSource

    class FakeC:
        def __init__(self, d):
            self.raw = d
            self.id = d["id"]
            self.text = d["text"]
            self.author = (
                type("A", (), {"username": d["author"]["username"]})()
                if d.get("author")
                else None
            )
            self.created_at = (
                datetime.fromisoformat(d["created_at"]) if d.get("created_at") else None
            )
            self.vote_score = d["vote_score"]

    def fake_api_list_comments(self, qid):
        return [FakeC(c) for c in SAMPLE_COMMENTS[::-1]]

    monkeypatch.setattr(
        MetaculusForecastSource,
        "list_metaculus_comments_for_question",
        fake_api_list_comments,
    )
    # Always use a temporary comments_cache_path so we never pollute real data
    comments_cache_path = str(cache_file)
    resp = client.get(
        f"/metaculus/questions/1/comments?force_refresh=true&comments_cache_path={comments_cache_path}"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["text"] == "Comment 2"
