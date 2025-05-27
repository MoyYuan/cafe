pytest

from cafe.forecast.source_metaculus os

pytestmark = pytest.mark.skipif(
    not os.getenv("METACULUS_API_KEY"),
    reason="Metaculus API key not set; skipping live API tests.",
)




test_list_metaculus_comments():
    src = MetaculusForecastSource.from_env()
    comments = src.list_metaculus_comments()
    if comments is None:
        print("No comments returned or endpoint unavailable.")
        assert False
    print(f"Fetched {len(comments)} comments.")
    for c in comments[:3]:
        print(f"Comment id={c.id}, author={c.author.username}, text={c.text[:40]}...")
    assert len(comments) > 0
    assert hasattr(comments[0], "id")
    assert hasattr(comments[0], "author")
    assert hasattr(comments[0], "text")


test_get_metaculus_comment():
    src = MetaculusForecastSource.from_env()
    comments = src.list_metaculus_comments()
    if not comments:
        print("No comments to fetch individually.")
        assert False
    comment_id = comments[0].id
    comment = src.get_metaculus_comment(comment_id)
    if comment is None:
        print(f"Comment id {comment_id} could not be fetched individually.")
        return
    print(f"Fetched comment id={comment.id}, text={comment.text[:40]}...")
    assert comment.id == comment_id
    assert hasattr(comment, "author")
    assert hasattr(comment, "text")


test_list_metaculus_comments_for_question():
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
