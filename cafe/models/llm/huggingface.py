from typing import Any, Dict, Optional

from .base import BaseModel
from .postprocessing import HuggingFacePostprocessor


class HuggingFaceModel(BaseModel):
    """
    Local LLM model using HuggingFace Transformers as backend.
    """

    def __init__(
        self, model_path: str = "gpt2", device: Optional[str] = None, **kwargs
    ):
        self.model_path = model_path
        self.device = device or "cpu"
        self.model = None
        self.tokenizer = None
        self.postprocessor = HuggingFacePostprocessor()
        self._load_model(**kwargs)

    def _load_model(self, **kwargs):
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, **kwargs)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_path, **kwargs)
            self.model.to(self.device)
        except ImportError:
            self.model = None
            self.tokenizer = None
            print("[HuggingFaceModel] transformers not installed. Model will not run.")
        except Exception as e:
            print(f"[HuggingFaceModel] Model loading failed: {e}")
            self.model = None
            self.tokenizer = None

    def predict(self, prompt: str, parameters: Dict[str, Any], context: Any) -> Any:
        if self.model is None or self.tokenizer is None:
            return {
                "error": "Local model not loaded. Check transformers install and model path."
            }
        # Normalize parameter names for compatibility
        max_tokens = parameters.get("max_tokens") or parameters.get(
            "max_new_tokens", 64
        )
        temperature = parameters.get("temperature", 1.0)
        gen_kwargs = dict(
            max_new_tokens=max_tokens,
            temperature=temperature,
        )
        gen_kwargs.update({k: v for k, v in parameters.items() if k not in gen_kwargs})
        import torch

        inputs = self.tokenizer(prompt, return_tensors="pt")
        # Move all tensors to the correct device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)
        output_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer = self.postprocessor.extract_answer(output_text)
        return {"text": output_text, "answer": answer}
