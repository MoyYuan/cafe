from abc import ABC, abstractmethod


class ForecastPipeline(ABC):
    @abstractmethod
    def run(self, input_data):
        """Run the pipeline on provided input_data and return results."""
        pass

    @abstractmethod
    def describe(self):
        """Return a description of the pipeline (for metadata/logging)."""
        pass
