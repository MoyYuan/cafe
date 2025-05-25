from typing import Callable, Dict, Sequence

from .metrics import accuracy, brier_score, log_loss


class Evaluator:
    def __init__(self, metrics: Dict[str, Callable]):
        self.metrics = metrics

    def evaluate(
        self,
        y_true: Sequence[float],
        y_prob: Sequence[float],
        y_pred: Optional[Sequence[float]] = None,
    ) -> Dict[str, float]:
        results = {}
        if "brier" in self.metrics:
            results["brier"] = self.metrics["brier"](y_true, y_prob)
        if "log_loss" in self.metrics:
            results["log_loss"] = self.metrics["log_loss"](y_true, y_prob)
        if "accuracy" in self.metrics and y_pred is not None:
            results["accuracy"] = self.metrics["accuracy"](y_true, y_pred)
        return results


# Default evaluator with all metrics
DefaultEvaluator = Evaluator(
    {"brier": brier_score, "log_loss": log_loss, "accuracy": accuracy}
)
