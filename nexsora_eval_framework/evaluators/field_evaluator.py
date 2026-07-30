from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from rapidfuzz import fuzz


class FieldEvaluator:
    def __init__(self, numeric_tolerance: float = 0.01, fuzzy_threshold: float = 0.85):
        self.numeric_tolerance = numeric_tolerance
        self.fuzzy_threshold = fuzzy_threshold

    def evaluate_field(self, field_name: str, gt_val: Any, pred_val: Any) -> Dict[str, Any]:
        """
        Evaluates a single field and computes TP/FP/FN along with individual
        Accuracy, Precision, Recall, F1, and Similarity scores.
        """
        # Case 1: Ground Truth is Empty/Null
        if gt_val is None or gt_val == "":
            if pred_val is None or pred_val == "":
                return self._build_result(field_name, gt_val, pred_val, 1.0, "PASS", "TN", 1, 0, 0, 1)
            else:
                return self._build_result(field_name, gt_val, pred_val, 0.0, "HALLUCINATED", "FP", 0, 1, 0, 0)

        # Case 2: Ground Truth Exists, Extracted is Null
        if pred_val is None or pred_val == "":
            return self._build_result(field_name, gt_val, pred_val, 0.0, "MISSING", "FN", 0, 0, 1, 0)

        # Case 3: Both GT and Extracted Exist
        # Numeric Evaluation
        if isinstance(gt_val, (int, float)):
            try:
                pred_num = float(pred_val)
                gt_num = float(gt_val)
                rel_err = abs(gt_num - pred_num) / abs(gt_num) if gt_num != 0 else abs(pred_num)
                is_pass = rel_err <= self.numeric_tolerance
                score = round(max(0.0, 1.0 - rel_err), 4)
            except (ValueError, TypeError):
                is_pass, score = False, 0.0

            outcome = "TP" if is_pass else "FP"
            tp, fp = (1, 0) if is_pass else (0, 1)
            return self._build_result(field_name, gt_val, pred_val, score, "PASS" if is_pass else "FAIL", outcome, tp, fp, 0, 0)

        # Text Evaluation
        gt_str, pred_str = str(gt_val).strip().lower(), str(pred_val).strip().lower()
        if gt_str == pred_str:
            return self._build_result(field_name, gt_val, pred_val, 1.0, "PASS", "TP", 1, 0, 0, 0)

        sim = fuzz.ratio(gt_str, pred_str) / 100.0
        is_pass = sim >= self.fuzzy_threshold
        outcome = "TP" if is_pass else "FP"
        tp, fp = (1, 0) if is_pass else (0, 1)
        return self._build_result(field_name, gt_val, pred_val, round(sim, 4), "PASS" if is_pass else "FAIL", outcome, tp, fp, 0, 0)

    def _build_result(self, name: str, gt: Any, ext: Any, sim: float, status: str, outcome: str, tp: int, fp: int, fn: int, tn: int) -> Dict[str, Any]:
        precision = 1.0 if (tp + fp) > 0 and tp > 0 else 0.0
        recall = 1.0 if (tp + fn) > 0 and tp > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        accuracy = 1.0 if outcome in ["TP", "TN"] else 0.0

        return {
            "field_name": name,
            "ground_truth": gt,
            "extracted": ext,
            "similarity_score": sim,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "status": status,
            "outcome": outcome,
            "TP": tp, "FP": fp, "FN": fn, "TN": tn
        }

    def compute_batch_field_metrics(self, all_doc_evaluations: List[Dict[str, Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """
        Aggregates field evaluations across all documents. 
        Unrolled line items (e.g., 'Detail[1].Quantity') are grouped under their parent field ('Detail')
        so the overall report stays high-level and clean.
        """
        field_stats = {}

        for doc_eval in all_doc_evaluations:
            # Track parent keys processed for this document to avoid double-counting document sample totals
            doc_parent_outcomes = {}

            for field_key, res in doc_eval.items():
                # Roll up unrolled fields like 'Detail[1].Quantity' to 'Detail'
                parent_key = field_key.split("[")[0].split(".")[0] if ("[" in field_key or "." in field_key) else field_key

                if parent_key not in field_stats:
                    field_stats[parent_key] = {
                        "TP": 0, "FP": 0, "FN": 0, "TN": 0,
                        "sim_scores": [], "total": 0
                    }

                # Collect similarity scores for average calculation
                field_stats[parent_key]["sim_scores"].append(res.get("similarity_score", 0.0))

                # Aggregate outcomes per document
                if parent_key not in doc_parent_outcomes:
                    doc_parent_outcomes[parent_key] = []
                doc_parent_outcomes[parent_key].append(res.get("outcome"))

            # Determine the parent field status for each document
            for parent_key, outcomes in doc_parent_outcomes.items():
                # If any line item failed or was hallucinated, mark parent as FP/FN for this doc
                if "FP" in outcomes:
                    final_outcome = "FP"
                elif "FN" in outcomes:
                    final_outcome = "FN"
                elif "TP" in outcomes:
                    final_outcome = "TP"
                else:
                    final_outcome = "TN"

                field_stats[parent_key][final_outcome] += 1
                field_stats[parent_key]["total"] += 1

        # Compute classification metrics per aggregated field
        summary = {}
        for parent_key, s in field_stats.items():
            tp, fp, fn, tn, total = s["TP"], s["FP"], s["FN"], s["TN"], s["total"]
            
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
            acc = (tp + tn) / total if total > 0 else 0.0
            avg_sim = sum(s["sim_scores"]) / len(s["sim_scores"]) if s["sim_scores"] else 0.0

            summary[parent_key] = {
                "total_samples": total,
                "TP": tp,
                "FP": fp,
                "FN": fn,
                "TN": tn,
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "avg_similarity_score": round(avg_sim, 4)
            }

        return summary


    def flatten_and_evaluate(self, gt_data: Dict[str, Any], pred_data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """
        Recursively iterates over dictionaries and lists (like 'Detail' line items) 
        to create flat keys such as 'Detail[0].item_description'.
        """
        results = {}
        
        all_keys = set(gt_data.keys()).union(set(pred_data.keys())) if isinstance(gt_data, dict) and isinstance(pred_data, dict) else set()

        for key in all_keys:
            gt_val = gt_data.get(key) if isinstance(gt_data, dict) else None
            pred_val = pred_data.get(key) if isinstance(pred_data, dict) else None
            full_key = f"{prefix}.{key}" if prefix else key

            # Case A: Sub-dictionary
            if isinstance(gt_val, dict) or isinstance(pred_val, dict):
                sub_res = self.flatten_and_evaluate(gt_val or {}, pred_val or {}, prefix=full_key)
                results.update(sub_res)

            # Case B: Array of Line Items (e.g. 'Detail')
            elif isinstance(gt_val, list) or isinstance(pred_val, list):
                gt_list = gt_val if isinstance(gt_val, list) else []
                pred_list = pred_val if isinstance(pred_val, list) else []
                max_len = max(len(gt_list), len(pred_list))

                if max_len == 0:
                    # Empty Array Match
                    results[full_key] = self.evaluate_field(full_key, "[]", "[]")
                else:
                    for idx in range(max_len):
                        gt_item = gt_list[idx] if idx < len(gt_list) else None
                        pred_item = pred_list[idx] if idx < len(pred_list) else None
                        item_prefix = f"{full_key}[{idx + 1}]"

                        if isinstance(gt_item, dict) or isinstance(pred_item, dict):
                            sub_res = self.flatten_and_evaluate(gt_item or {}, pred_item or {}, prefix=item_prefix)
                            results.update(sub_res)
                        else:
                            results[item_prefix] = self.evaluate_field(item_prefix, gt_item, pred_item)

            # Case C: Primitive Field Value
            else:
                results[full_key] = self.evaluate_field(full_key, gt_val, pred_val)

        return results