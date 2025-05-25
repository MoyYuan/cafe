import uuid
from typing import Dict, Any, List
from datetime import datetime

class ExperimentTracker:
    def __init__(self):
        self.runs = []

    def log_run(self, model: str, parameters: Dict[str, Any], metrics: Dict[str, float], notes: str = ""):
        run_id = str(uuid.uuid4())
        self.runs.append({
            'run_id': run_id,
            'model': model,
            'parameters': parameters,
            'metrics': metrics,
            'notes': notes,
            'timestamp': datetime.utcnow().isoformat()
        })
        return run_id

    def list_runs(self) -> List[Dict[str, Any]]:
        return self.runs
