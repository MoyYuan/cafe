from cafe.experiments.experiment_tracker import ExperimentTracker

tracker = ExperimentTracker()
run_id = tracker.log_run(
    model="test-model",
    parameters={"lr": 0.01},
    metrics={"brier": 0.1, "accuracy": 1.0},
    notes="Baseline run",
)
print("Run ID:", run_id)
print("All runs:", tracker.list_runs())
