import os
import pytest
from cafe.news.google import GoogleNewsFetcher
from datetime import datetime, timedelta

@pytest.mark.integration
@pytest.mark.skipif(
    not (os.getenv("GOOGLE_SEARCH_API_KEY") and os.getenv("GOOGLE_SEARCH_CX")),
    reason="Google Search API credentials not set in environment."
)
def test_google_news_fetcher_basic():
    fetcher = GoogleNewsFetcher()
    today = datetime.now().date()
    year_ago = today - timedelta(days=365)
    results = fetcher.fetch_news(
        query="OpenAI",
        start_date=str(year_ago),
        end_date=str(today),
        max_results=5
    )
    assert isinstance(results, list)
    assert len(results) > 0, "Should return at least one news result."
    # Check structure of at least the first result
    first = results[0]
    assert "link" in first
    assert "title" in first
    assert "snippet" in first
