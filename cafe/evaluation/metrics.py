from typing import Sequence

import numpy as np  # type: ignore


def brier_score(y_true: Sequence[float], y_prob: Sequence[float]) -> float:
    """Compute the Brier score for probabilistic forecasts."""
    y_true_arr = np.array(y_true, dtype=float)
    y_prob_arr = np.array(y_prob, dtype=float)
    return float(np.mean((y_true_arr - y_prob_arr) ** 2))


def log_loss(
    y_true: Sequence[float], y_prob: Sequence[float], eps: float = 1e-15
) -> float:
    """Compute the log loss for probabilistic forecasts."""
    y_true_arr = np.array(y_true, dtype=float)
    y_prob_arr = np.clip(np.array(y_prob, dtype=float), eps, 1 - eps)
    return float(
        -np.mean(
            y_true_arr * np.log(y_prob_arr) + (1 - y_true_arr) * np.log(1 - y_prob_arr)
        )
    )


def accuracy(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    """Compute accuracy for binary outcomes."""
    y_true_arr = np.array(y_true, dtype=float)
    y_pred_arr = np.array(y_pred, dtype=float)
    return float(np.mean(y_true_arr == y_pred_arr))
