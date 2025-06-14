import hashlib
from typing import Any, Dict, Optional

from .base import BaseModel
from .postprocessing import VLLMPostprocessor


class VLLMModel(BaseModel):
    """
    Local LLM model using vLLM Python API for high-performance inference.
    See: https://docs.vllm.ai/en/latest/getting_started/quickstart.html#offline-batched-inference
    """

    def __init__(
        self,
        model_path: str = "facebook/opt-125m",
        dtype: Optional[str] = None,
        **kwargs,
    ):
        self.model_path = model_path
        self.dtype = dtype
        self.llm = None
        self.postprocessor = VLLMPostprocessor()
        self._load_model(**kwargs)

    def _load_model(self, **kwargs):
        try:
            from vllm import LLM  # type: ignore

            init_kwargs = dict(model=self.model_path)
            if self.dtype:
                init_kwargs["dtype"] = self.dtype
            init_kwargs.update(kwargs)
            self.llm = LLM(**init_kwargs)
        except ImportError:
            self.llm = None
            print("[VLLMModel] vllm not installed. Model will not run.")
        except Exception as e:
            print(f"[VLLMModel] Model loading failed: {e}")
            self.llm = None

    def predict(self, prompt: str, parameters: Dict[str, Any], context: Any) -> Any:
        """
        Generate a completion from the local model using vLLM.
        Args:
            prompt: Input prompt string.
            parameters: Dict of generation parameters (e.g., max_tokens, temperature).
            context: Used for caching and stateful workflows.
        Returns:
            Postprocessed model output (str, dict, etc.).
        """
        # Generate a context cache key
        param_hash = hashlib.md5(str(sorted(parameters.items())).encode()).hexdigest()
        cache_key = f"vllm:{hashlib.md5((prompt + param_hash).encode()).hexdigest()}"
        cached = context.get_data(cache_key)
        if cached is not None:
            return cached
        if self.llm is None:
            return {
                "error": "vLLM model not loaded. Check vllm install and model path."
            }
        try:
            from vllm import SamplingParams  # type: ignore

            sampling_params = SamplingParams(
                max_tokens=parameters.get("max_tokens", 64),
                temperature=parameters.get("temperature", 1.0),
                stop=parameters.get("stop"),
            )
            outputs = self.llm.generate([prompt], sampling_params)
            # vLLM returns a list of RequestOutput, each with .outputs (list of TokenOutputs)
            if not outputs or not outputs[0].outputs:
                return None
            output_text = outputs[0].outputs[0].text
            result = self.postprocessor.extract_answer(output_text)
            context.set_data(cache_key, result)
            return result
        except Exception as e:
            return {"error": f"vLLM inference failed: {e}"}
