import pytest

from cafe.evaluation.metrics import accuracy, brier_score, log_loss


def test_brier_score():
    y_true = [1, 0, 1]
    y_prob = [0.8, 0.2, 0.6]
    assert abs(brier_score(y_true, y_prob) - 0.053333) < 1e-4


def test_log_loss():
    y_true = [1, 0, 1]
    y_prob = [0.8, 0.2, 0.6]
    assert log_loss(y_true, y_prob) > 0


def test_accuracy():
    y_true = [1, 0, 1]
    y_pred = [1, 0, 0]
    assert accuracy(y_true, y_pred) == 2 / 3
