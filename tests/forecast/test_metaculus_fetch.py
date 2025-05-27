import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("METACULUS_API_KEY"),
    reason="Metaculus API key not set; skipping live API tests.",
)

from cafe.forecast.source_metaculus import MetaculusForecastSource


def test_metaculus_fetch_placeholder():
    assert True  # placeholder test


import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.getenv("METACULUS_API_KEY"),
    reason="Metaculus API key not set; skipping live API tests.",
)

from cafe.forecast.source_metaculus import MetaculusForecastSource


def test_fetch_and_save_metaculus_questions():
    # Fetch questions from Metaculus
    src = MetaculusForecastSource()
    questions = src.list_questions()
    assert questions, "No questions fetched from Metaculus!"

    # Save questions to JSON
    test_file = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "forecasts",
        "test_metaculus_questions.json",
    )
    with open(test_file, "w") as f:
        json.dump([q.raw if hasattr(q, "raw") else q for q in questions], f, indent=2)

    assert os.path.exists(test_file), "Questions JSON file was not created!"

    # Load questions back from JSON
    with open(test_file, "r") as f:
        loaded = json.load(f)
    assert loaded, "No questions loaded from JSON!"
    assert loaded[0]["title"] == (
        questions[0].title if hasattr(questions[0], "title") else questions[0]["title"]
    ), "Mismatch between fetched and loaded question titles!"

    # Fetch comments for the first question
    question_id = questions[0].id
    comments = src.list_metaculus_comments_for_question(question_id)
    assert comments is not None, f"No comments returned for question {question_id}!"
    assert isinstance(comments, list), "Comments should be a list!"
    if comments:
        comment = comments[0]
        assert hasattr(comment, "id"), "Comment object missing 'id' field!"
        assert hasattr(comment, "text"), "Comment object missing 'text' field!"

    # Cleanup
    os.remove(test_file)
