import json
import logging
import re
from typing import Any, Callable, List, Optional, Protocol, Union


class LLMPostprocessor(Protocol):
    def extract_answer(self, raw_output: Any) -> Union[dict, str, None]: ...


def extract_with_regex(text: str, patterns: List[str]) -> Optional[str]:
    """
    Try to extract an answer using a list of regex patterns.
    Returns the first match found, or None.
    """
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            # Return the first capturing group if present, else the whole match
            return match.group(1) if match.lastindex else match.group(0)
    return None


class AdvancedPostprocessor:
    """
    Base postprocessor supporting fallback extraction functions.
    """

    def __init__(
        self,
        regex_patterns: Optional[List[str]] = None,
        fallbacks: Optional[List[Callable[[str], Any]]] = None,
    ):
        self.regex_patterns = regex_patterns or []
        self.fallbacks = fallbacks or []

    def extract_answer(self, raw_output: Any) -> Union[dict, str, None]:
        text = self._get_text(raw_output)
        if not isinstance(text, str) or not text:
            return None
        # Try JSON
        try:
            return json.loads(text)
        except Exception:
            pass
        # Try regex
        if self.regex_patterns:
            result = extract_with_regex(text, self.regex_patterns)
            if result is not None:
                return result
        # Try fallbacks
        for fallback in self.fallbacks:
            try:
                result = fallback(text)
                if result is not None:
                    return result
            except Exception:
                continue
        # Default: return stripped text
        return text.strip()

    def _get_text(self, raw_output: Any) -> str:
        # Default: try to extract 'text' from dict or object, else str(raw_output)
        text = getattr(raw_output, "text", None)
        if text is None and isinstance(raw_output, dict):
            text = raw_output.get("text")
        if text is None:
            text = str(raw_output)
        return text


class GeminiPostprocessor(AdvancedPostprocessor):
    def __init__(self):
        regex_patterns = [
            r"(?:answer|probability|confidence)[^\d]*(\d+(?:\.\d+)?)",
            r"(\d{1,3}(?:\.\d+)?)%",  # percent
            r"([-+]?[0-9]*\.?[0-9]+)",  # any number
        ]

        def extract_boxed(text: str):
            patterns = [
                r"\\boxed\s*\{\s*([^{}]+?)\s*\}",  # \\boxed{...}
                r"\\boxed\s*\(([^()]+?)\)",  # \\boxed(...)
                r"\\boxed\s+([^\s.,;:!?]+)",  # \\boxed ...
                r"\[\s*boxed\s*\]\s*:?\s*([^\s.,;:!?]+)",  # [boxed]: ...
                r"boxed\s*[:=\-]?\s*([^\s.,;:!?]+)",  # boxed: ...
            ]
            for pat in patterns:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    return m.group(1).strip()
            return None

        def extract_quoted(text: str):
            m = re.search(r'"([^"]+)"', text)
            return m.group(1) if m else None

        fallbacks = [extract_boxed, extract_quoted]
        super().__init__(regex_patterns=regex_patterns, fallbacks=fallbacks)


class VLLMPostprocessor(AdvancedPostprocessor):
    def __init__(self):
        regex_patterns = [
            r"(?:answer|probability|confidence)[^\d]*(\d+(?:\.\d+)?)",
            r"(\d{1,3}(?:\.\d+)?)%",
            r"([-+]?[0-9]*\.?[0-9]+)",
        ]

        def extract_boxed(text: str):
            patterns = [
                r"\\boxed\s*\{\s*([^{}]+?)\s*\}",
                r"\\boxed\s*\(([^()]+?)\)",
                r"\\boxed\s+([^\s.,;:!?]+)",
                r"\[\s*boxed\s*\]\s*:?\s*([^\s.,;:!?]+)",
                r"boxed\s*[:=\-]?\s*([^\s.,;:!?]+)",
            ]
            for pat in patterns:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    return m.group(1).strip()
            return None

        def extract_quoted(text: str):
            m = re.search(r'"([^"]+)"', text)
            return m.group(1) if m else None

        fallbacks = [extract_boxed, extract_quoted]
        super().__init__(regex_patterns=regex_patterns, fallbacks=fallbacks)
