from typing import Any, Dict, Optional

import httpx

from .base import BaseModel


class GeminiModel(BaseModel):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def predict(self, prompt: str, parameters: Dict[str, Any], context) -> Any:
        if not self.api_key:
            raise ValueError("Gemini API key not set.")
        # Example Gemini API call (stub)
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        params = {"key": self.api_key}
        try:
            response = httpx.post(
                url, headers=headers, json=payload, params=params, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise RuntimeError(f"Gemini API call failed: {e}")
