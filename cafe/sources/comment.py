from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class MetaculusCommentAuthor:
    """Metaculus-specific comment author."""

    id: int
    username: str
    is_bot: Optional[bool] = False
    is_staff: Optional[bool] = False


@dataclass
class MetaculusMentionedUser:
    """Metaculus-specific mentioned user in a comment."""

    id: int
    username: str


@dataclass
class MetaculusChangedMyMind:
    """Metaculus-specific 'Changed My Mind' reaction info."""

    count: int
    for_this_user: Optional[bool] = False


@dataclass
class MetaculusComment:
    """Metaculus-specific comment object."""

    """Represents a comment from the Metaculus API."""

    id: int
    author: MetaculusCommentAuthor
    parent_id: Optional[int]
    root_id: Optional[int]
    created_at: datetime
    text: str
    on_post: int
    included_forecast: Optional[bool]
    is_private: Optional[bool]
    vote_score: Optional[int]
    changed_my_mind: Optional[MetaculusChangedMyMind]
    mentioned_users: Optional[List[MetaculusMentionedUser]]
    user_vote: Optional[int]
    raw: Optional[Dict] = None
