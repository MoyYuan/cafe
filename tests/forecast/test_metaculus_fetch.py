import os

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
    MetaculusForecastSource.save_questions_to_json(questions, filepath=test_file)
    assert os.path.exists(test_file), "Questions JSON file was not created!"

    # Load questions back from JSON
    loaded = MetaculusForecastSource.load_questions_from_json(filepath=test_file)
    assert loaded, "No questions loaded from JSON!"
    assert (
        loaded[0].id == questions[0].id
    ), "Mismatch between fetched and loaded question IDs!"

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
