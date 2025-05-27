import json
import logging
from typing import Any, Protocol, Union


class LLMPostprocessor(Protocol):
    def extract_answer(self, raw_output: Any) -> Union[dict, str, None]: ...


class GeminiPostprocessor:
    def extract_answer(self, raw_output: Any) -> Union[dict, str, None]:
        """
        Try to extract a structured answer from Gemini's raw output.
        - If output is JSON, parse and return as dict.
        - Else, return as string.
        """
        # Gemini API may return a response object or dict with 'text' or similar
        text = getattr(raw_output, "text", None)
        if text is None and isinstance(raw_output, dict):
            text = raw_output.get("text")
        if not isinstance(text, str) or not text:
            return None
        try:
            return json.loads(text)
        except Exception:
            return text.strip()


# Example for vLLM (fill in as needed)
class VLLMPostprocessor:
    def extract_answer(self, raw_output: Any) -> Union[dict, str, None]:
        text = (
            raw_output.get("text") if isinstance(raw_output, dict) else str(raw_output)
        )
        if not isinstance(text, str) or not text:
            return None
        try:
            return json.loads(text)
        except Exception:
            return text.strip()
