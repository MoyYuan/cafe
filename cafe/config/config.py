import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    METACULUS_API_URL = os.getenv(
        "METACULUS_API_URL", "https://www.metaculus.com/api2/questions/"
    )
    GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX", "")
    VLLM_MODEL_PATH = os.getenv("VLLM_MODEL_PATH", "")
    # Add more config as needed
