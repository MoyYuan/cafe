import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    METACULUS_API_KEY = os.getenv("METACULUS_API_KEY", None)
    METACULUS_API_URL = os.getenv(
        "METACULUS_API_URL", "https://www.metaculus.com/api2/"
    )
    GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX", "")
    VLLM_MODEL_PATH = os.getenv("VLLM_MODEL_PATH", "")
    # Add more config as needed


_settings_instance = None

def get_settings():
    """
    Returns a singleton Config instance with environment variables loaded.
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Config()
    return _settings_instance
