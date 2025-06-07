import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("METACULUS_API_KEY"),
    reason="Metaculus API key not set; skipping live API tests.",
)

from cafe.sources.source_metaculus import MetaculusForecastSource


def test_source_metaculus_placeholder():
    assert True  # placeholder test


import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("METACULUS_API_KEY"),
    reason="Metaculus API key not set; skipping live API tests.",
)

from cafe.sources.source_metaculus import MetaculusForecastSource


def test_env_instantiation():
    src = MetaculusForecastSource.from_env()
    questions = src.list_questions()
    assert questions, "Should fetch questions from Metaculus using env vars!"
    print(f"Fetched {len(questions)} questions (env)")


def test_explicit_args():
    api_key = os.getenv("METACULUS_API_KEY")
    base_url = os.getenv("METACULUS_API_URL")
    src = MetaculusForecastSource(base_url=base_url, api_key=api_key)
    questions = src.list_questions()
    assert questions, "Should fetch questions from Metaculus using explicit args!"
    print(f"Fetched {len(questions)} questions (explicit)")


def test_get_question():
    src = MetaculusForecastSource.from_env()
    questions = src.list_questions()
    if not questions:
        raise AssertionError("No questions fetched!")
    qid = questions[0].id
    q = src.get_question(qid)
    assert q.id == qid, "Fetched question by ID should match!"
    print(f"Fetched question: {q.title}")
