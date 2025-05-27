import logging
import os
import time
from typing import Any, Dict, Optional

from cafe.config.config import Config
from cafe.models.llm.postprocessing import GeminiPostprocessor

from .base import BaseModel

genai: Any
genai_types: Any
try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    genai = None
    genai_types = None


class GeminiModel(BaseModel):
    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_enabled: Optional[bool] = None,
        log_prompts: Optional[bool] = None,
        privacy_mode: Optional[bool] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        mock_mode: Optional[bool] = None,
    ):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.cache_enabled = (
            cache_enabled
            if cache_enabled is not None
            else os.getenv("GEMINI_CACHE_ENABLED", "1") == "1"
        )
        self.log_prompts = (
            log_prompts
            if log_prompts is not None
            else os.getenv("GEMINI_LOG_PROMPTS", "1") == "1"
        )
        self.privacy_mode = (
            privacy_mode
            if privacy_mode is not None
            else os.getenv("GEMINI_PRIVACY_MODE", "0") == "1"
        )
        self.timeout = timeout or int(os.getenv("GEMINI_TIMEOUT", "10"))
        self.max_retries = max_retries or int(os.getenv("GEMINI_MAX_RETRIES", "2"))
        self.mock_mode = (
            mock_mode
            if mock_mode is not None
            else os.getenv("GEMINI_MOCK_MODE", "0") == "1"
        )
        self.postprocessor = GeminiPostprocessor()

    def _make_cache_key(self, prompt: str, parameters: Dict[str, Any]) -> str:
        import hashlib
        import json

        key_raw = json.dumps(
            {"prompt": prompt, "parameters": parameters}, sort_keys=True
        )
        return "gemini_cache_" + hashlib.sha256(key_raw.encode()).hexdigest()

    def _validate_parameters(self, parameters: Dict[str, Any]):
        # Add more validation as Gemini API evolves
        if not isinstance(parameters, dict):
            raise ValueError("Parameters must be a dictionary.")

    def _log(self, prompt: str, response: Any):
        if self.log_prompts:
            if self.privacy_mode:
                prompt = "[REDACTED]"
                response = "[REDACTED]"
            logging.info(f"Gemini prompt: {prompt}")
            logging.info(f"Gemini response: {response}")

    def predict(self, prompt: str, parameters: Dict[str, Any], context) -> Any:
        if not self.api_key and not self.mock_mode:
            raise ValueError("Gemini API key not set.")
        self._validate_parameters(parameters)
        cache_key = self._make_cache_key(prompt, parameters)

        # Mock mode for testing
        if self.mock_mode:
            mock_resp = {"mock": True, "prompt": prompt, "parameters": parameters}
            self._log(prompt, mock_resp)
            if self.cache_enabled:
                context.set_data(cache_key, mock_resp)
            return mock_resp

        # Caching
        if self.cache_enabled:
            cached = context.get_data(cache_key)
            if cached is not None:
                self._log(prompt, cached)
                return cached

        if genai is None or genai_types is None:
            raise ImportError(
                "google-genai package is not installed. Please install it with 'uv pip install google-generativeai'."
            )

        client = genai.Client(api_key=self.api_key)
        model_name = parameters.get("model", "gemini-2.0-flash")
        contents = [prompt]

        # Extract config parameters for generation
        config_kwargs = {}
        for k in [
            "max_output_tokens",
            "temperature",
            "candidate_count",
            "top_k",
            "top_p",
            "stop_sequences",
        ]:
            if k in parameters:
                config_kwargs[k] = parameters[k]
        config = (
            genai_types.GenerateContentConfig(**config_kwargs)
            if config_kwargs
            else None
        )

        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
                # Extract text (or fallback to dict if needed)
                result = {
                    "text": getattr(response, "text", str(response)),
                    "raw": response,
                    "answer": self.postprocessor.extract_answer(response),
                }
                if self.cache_enabled:
                    context.set_data(cache_key, result)
                self._log(prompt, result)
                return result
            except Exception as e:
                last_exception = e
                wait = 2**attempt
                time.sleep(wait)
        raise RuntimeError(
            f"Gemini API call failed after {self.max_retries + 1} attempts: {last_exception}"
        )
