from typing import Sequence

import numpy as np


def brier_score(y_true: Sequence[float], y_prob: Sequence[float]) -> float:
    """Compute the Brier score for probabilistic forecasts."""
    y_true = np.array(y_true)
    y_prob = np.array(y_prob)
    return np.mean((y_true - y_prob) ** 2)


def log_loss(y_true: Sequence[float], y_prob: Sequence[float], eps: float = 1e-15) -> float:
    """Compute the log loss for probabilistic forecasts."""
    y_true = np.array(y_true)
    y_prob = np.clip(np.array(y_prob), eps, 1 - eps)
    return -np.mean(y_true * np.log(y_prob) + (1 - y_true) * np.log(1 - y_prob))


def accuracy(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    """Compute accuracy for binary outcomes."""
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    return np.mean(y_true == y_pred)
