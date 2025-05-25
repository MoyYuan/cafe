from cafe.experiments.experiment_tracker import ExperimentTracker

def test_experiment_tracker():
    tracker = ExperimentTracker()
    run_id = tracker.log_run(
        model='test-model',
        parameters={'param1': 1},
        metrics={'brier': 0.1},
        notes='Test run'
    )
    runs = tracker.list_runs()
    assert len(runs) == 1
    assert runs[0]['run_id'] == run_id
    assert runs[0]['model'] == 'test-model'
