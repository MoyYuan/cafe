from cafe.evaluation.evaluator import DefaultEvaluator
from cafe.evaluation.metrics import accuracy, brier_score, log_loss

y_true = [1, 0, 1]
y_prob = [0.8, 0.2, 0.6]
y_pred = [1, 0, 1]

print("Brier score:", brier_score(y_true, y_prob))
print("Log loss:", log_loss(y_true, y_prob))
print("Accuracy:", accuracy(y_true, y_pred))

results = DefaultEvaluator.evaluate(y_true, y_prob, y_pred)
print("All metrics:", results)
