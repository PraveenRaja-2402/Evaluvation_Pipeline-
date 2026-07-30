from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseEvaluator(ABC):
    @abstractmethod
    def evaluate(self, ground_truth: Dict[str, Any], extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates extracted data against ground truth.
        Returns a dictionary containing calculated scores and field-level feedback.
        """
        pass