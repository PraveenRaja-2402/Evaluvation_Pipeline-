import json
from typing import Dict, Any
from evaluators.base import BaseEvaluator
from adapters.llm_factory import _extract_text_content

class RagasEngine(BaseEvaluator):
    def __init__(self, llm_model):
        self.llm_model = llm_model

    def evaluate(self, ground_truth: Dict[str, Any], extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        gt_str = json.dumps(ground_truth)
        ext_str = json.dumps(extracted_data)

        try:
            prompt = (
                f"Compare the following extracted document payload against the ground truth.\n"
                f"Ground Truth: {gt_str}\n"
                f"Extracted Payload: {ext_str}\n"
                f"Respond with a single JSON object: {{\"faithfulness_score\": <float 0.0-1.0>, \"reason\": \"<brief explanation>\"}}"
            )
            raw_response = self.llm_model.generate(prompt)
            
            # Ensure raw_response is converted to string
            response_text = _extract_text_content(raw_response)
            
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean_json)
            
            return {
                "ragas_faithfulness": float(parsed.get("faithfulness_score", 0.0)),
                "ragas_reasoning": parsed.get("reason", "N/A")
            }
        except Exception as e:
            return {
                "ragas_faithfulness": 0.0,
                "ragas_reasoning": f"Ragas Engine Exception: {str(e)}"
            }