import json
import os
import tempfile

from cafe.forecast.comment import MetaculusComment
from cafe.forecast.source_local import LocalForecastCommentSource


def sample_comment(comment_id=1, question_id="101"):
    return {
        "id": comment_id,
        "author": {"id": 1, "username": "testuser"},
        "parent_id": None,
        "root_id": None,
        "created_at": "2025-05-26T20:00:00",
        "text": "Sample comment text.",
        "on_post": question_id,
        "included_forecast": None,
        "is_private": None,
        "vote_score": 5,
        "changed_my_mind": None,
        "mentioned_users": [],
        "user_vote": None,
    }


def test_local_comment_source():
    # Create a temp file with sample comments
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        comments = [
            sample_comment(1, "101"),
            sample_comment(2, "101"),
            sample_comment(3, "102"),
        ]
        json.dump(comments, f)
        f.flush()
        path = f.name

    src = LocalForecastCommentSource(path)
    # Test list_comments_for_question
    comments_101 = src.list_comments_for_question("101")
    assert len(comments_101) == 2
    assert all(isinstance(c, MetaculusComment) for c in comments_101)
    assert comments_101[0].text == "Sample comment text."
    # Test get_comment
    c = src.get_comment(2)
    assert c.id == 2
    assert c.author.username == "testuser"
    # Cleanup
    os.remove(path)
