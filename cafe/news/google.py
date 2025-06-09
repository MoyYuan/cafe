import os
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
import httpx
from bs4 import BeautifulSoup
from cafe.config.config import get_settings  # Assumed config pattern
from cafe.utils.logging import get_logger   # Assumed logging util

GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

class GoogleNewsFetcher:
    """
    Fetches news results from Google Custom Search API and extracts article summaries.
    Designed for modular use in pipelines or API endpoints.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        search_engine_id: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.GOOGLE_SEARCH_API_KEY
        self.search_engine_id = search_engine_id or settings.GOOGLE_SEARCH_CX
        self.logger = logger or get_logger(__name__)

    def generate_query_params(self, query: str, start_date: str, end_date: str, start: int = 1) -> Dict[str, Any]:
        encoded_query = quote_plus(query)
        sort_param = f"date:r:{end_date.replace('-', '')}:{start_date.replace('-', '')}"
        return {
            "q": encoded_query,
            "cx": self.search_engine_id,
            "key": self.api_key,
            "sort": sort_param,
            "num": 10,
            "start": start
        }

    def fetch_news(self, query: str, start_date: str, end_date: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Fetches news results for a query and date range.
        Returns a list of news items (dicts with at least 'link', 'title', 'snippet').
        """
        all_results = []
        with httpx.Client(timeout=10.0) as client:
            for start in range(1, max_results + 1, 10):
                params = self.generate_query_params(query, start_date, end_date, start)
                try:
                    resp = client.get(GOOGLE_SEARCH_URL, params=params)
                    resp.raise_for_status()
                    data = resp.json()
                    items = data.get("items", [])
                    all_results.extend(items)
                    if not items:
                        break  # No more results
                except httpx.HTTPStatusError as e:
                    self.logger.error(f"Google API error: {e.response.status_code} - {e.response.text}")
                    if e.response.status_code == 429:
                        self.logger.warning("Rate limit hit. Consider retry/backoff in pipeline.")
                    break
                except Exception as e:
                    self.logger.error(f"Unexpected error during news fetch: {e}")
                    break
        return all_results

    def get_full_summary(self, link: str, fallback_summary: str = "") -> str:
        """
        Fetches the full title and meta description from a news article link.
        Returns a summary string or the fallback if extraction fails.
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(link)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                full_title = soup.title.string.strip() if soup.title and soup.title.string else ""
                meta_desc = soup.find("meta", attrs={"name": "description"})
                full_snippet = meta_desc["content"].strip() if meta_desc and meta_desc.has_attr("content") else fallback_summary
                summary = f"{full_title} - {full_snippet}".strip(" -")
                return summary or fallback_summary
        except Exception as e:
            self.logger.error(f"Error fetching summary for {link}: {e}")
            return fallback_summary
