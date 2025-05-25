from cafe.config.config import Config

def test_config_keys():
    assert hasattr(Config, 'GEMINI_API_KEY')
    assert hasattr(Config, 'METACULUS_API_URL')
    assert hasattr(Config, 'GOOGLE_SEARCH_API_KEY')
    assert hasattr(Config, 'GOOGLE_SEARCH_CX')
    assert hasattr(Config, 'VLLM_MODEL_PATH')
