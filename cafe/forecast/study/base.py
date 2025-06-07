from abc import ABC, abstractmethod

class ForecastStudy(ABC):
    @abstractmethod
    def run(self, input_data):
        """Run the study on provided input_data and return results."""
        pass

    @abstractmethod
    def describe(self):
        """Return a description of the study (for metadata/logging)."""
        pass
