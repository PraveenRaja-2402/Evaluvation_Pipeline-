from typing import Dict, Any, List
from rapidfuzz import fuzz
from evaluators.base import BaseEvaluator

class DeterministicEvaluator(BaseEvaluator):
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold

    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        items: List[tuple] = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def evaluate(self, ground_truth: Dict[str, Any], extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        gt_flat = self._flatten_dict(ground_truth)
        ext_flat = self._flatten_dict(extracted_data)

        total_gt_fields = len(gt_flat)
        if total_gt_fields == 0:
            return {
                "field_precision": 0.0,
                "field_recall": 0.0,
                "exact_match_ratio": 0.0,
                "average_string_similarity": 0.0,
                "field_breakdown": {}
            }

        exact_matches = 0
        similar_matches = 0
        total_similarity = 0.0
        field_breakdown = {}

        for key, gt_val in gt_flat.items():
            ext_val = ext_flat.get(key)
            gt_str = str(gt_val).strip() if gt_val is not None else ""
            ext_str = str(ext_val).strip() if ext_val is not None else ""

            is_exact = gt_str == ext_str
            sim_score = (fuzz.ratio(gt_str, ext_str) / 100.0) if (gt_str or ext_str) else 1.0

            if is_exact:
                exact_matches += 1
            if sim_score >= self.similarity_threshold:
                similar_matches += 1

            total_similarity += sim_score
            field_breakdown[key] = {
                "ground_truth": gt_val,
                "extracted": ext_val,
                "exact_match": is_exact,
                "similarity_score": round(sim_score, 4)
            }

        correct_extracted = sum(1 for k, v in ext_flat.items() if str(v).strip() == str(gt_flat.get(k, "")).strip())
        precision = round(correct_extracted / len(ext_flat), 4) if ext_flat else 0.0
        recall = round(exact_matches / total_gt_fields, 4)
        avg_sim = round(total_similarity / total_gt_fields, 4)

        return {
            "field_precision": precision,
            "field_recall": recall,
            "exact_match_ratio": round(exact_matches / total_gt_fields, 4),
            "average_string_similarity": avg_sim,
            "field_breakdown": field_breakdown
        }