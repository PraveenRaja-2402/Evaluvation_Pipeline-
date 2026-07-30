import json
from typing import Dict, Any
from deepeval.test_case import LLMTestCase
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams
from evaluators.base import BaseEvaluator

class DeepEvalEngine(BaseEvaluator):
    def __init__(self, llm_model):
        self.llm_model = llm_model
        # Metric assessing structural & semantic accuracy between extracted JSON and ground truth JSON
        self.correctness_metric = GEval(
            name="Extraction Correctness",
            criteria="Determine if the extracted document payload correctly captures all facts, numbers, dates, and schema values present in the ground truth payload.",
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
            model=self.llm_model
        )

    def evaluate(self, ground_truth: Dict[str, Any], extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        gt_str = json.dumps(ground_truth, indent=2)
        ext_str = json.dumps(extracted_data, indent=2)

        test_case = LLMTestCase(
            input="Extract structured field data from the given document context.",
            actual_output=ext_str,
            expected_output=gt_str
        )

        try:
            self.correctness_metric.measure(test_case)
            score = float(self.correctness_metric.score)
            reason = self.correctness_metric.reason
        except Exception as e:
            score = 0.0
            reason = f"DeepEval Execution Error: {str(e)}"

        return {
            "deepeval_correctness_score": round(score, 4),
            "deepeval_reasoning": reason
        }