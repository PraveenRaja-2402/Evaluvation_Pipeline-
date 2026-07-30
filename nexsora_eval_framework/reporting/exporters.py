import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List


class MultiFormatExporter:
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.doc_dir = self.output_dir / "documents"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.doc_dir.mkdir(parents=True, exist_ok=True)

    def export_all(
        self,
        overall_summary: Dict[str, Any],
        field_batch_metrics: Dict[str, Dict[str, Any]],
        doc_level_results: List[Dict[str, Any]]
    ):
        # 1. Export Per-Document JSON and Markdown
        for doc in doc_level_results:
            doc_id = doc.get("document_id", "unknown")
            
            # Individual JSON
            doc_json_path = self.doc_dir / f"{doc_id}.json"
            with open(doc_json_path, "w", encoding="utf-8") as f:
                json.dump(doc, f, indent=2)

            # Individual Markdown
            doc_md_path = self.doc_dir / f"{doc_id}.md"
            self._write_individual_markdown(doc, doc_md_path)

        # 2. Export Global overall.json
        overall_json_path = self.output_dir / "overall.json"
        overall_payload = {
            "overall_summary": overall_summary,
            "field_wise_batch_metrics": field_batch_metrics
        }
        with open(overall_json_path, "w", encoding="utf-8") as f:
            json.dump(overall_payload, f, indent=2)

        # 3. Export Global overall.md
        overall_md_path = self.output_dir / "overall.md"
        self._write_overall_markdown(overall_summary, field_batch_metrics, overall_md_path)

        # 4. Export Consolidated Excel Report
        self._write_excel_report(overall_summary, field_batch_metrics, doc_level_results)

    def _write_individual_markdown(self, doc: Dict[str, Any], filepath: Path):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Evaluation Report: `{doc['document_id']}`\n\n")
            f.write("## 1. Document Overview\n\n")
            f.write(f"- **GT File**: `{doc.get('gt_file')}`\n")
            f.write(f"- **Extracted File**: `{doc.get('ext_file')}`\n")
            
            # System Metrics
            det = doc.get("deterministic", {})
            f.write(f"- **Overall Field Precision**: {det.get('field_precision', 0.0):.2%}\n")
            f.write(f"- **Overall Field Recall**: {det.get('field_recall', 0.0):.2%}\n")
            f.write(f"- **DeepEval Correctness**: {doc.get('deepeval', {}).get('deepeval_correctness_score', 0.0):.2f}\n\n")

            f.write("## 2. Field-Wise Evaluation Details\n\n")
            f.write("| Field Name | Ground Truth | Extracted | Status | Similarity | Precision | Recall | F1-Score | Accuracy |\n")
            f.write("| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")

            field_res = doc.get("field_results", {})
            for field, res in field_res.items():
                gt_str = str(res.get("ground_truth", ""))
                ext_str = str(res.get("extracted", ""))
                # Shorten long strings for table formatting
                gt_disp = gt_str if len(gt_str) <= 25 else gt_str[:22] + "..."
                ext_disp = ext_str if len(ext_str) <= 25 else ext_str[:22] + "..."
                
                status_icon = "✅ PASS" if res.get("status") == "PASS" else "❌ " + str(res.get("status"))

                f.write(
                    f"| `{field}` | `{gt_disp}` | `{ext_disp}` | {status_icon} | "
                    f"{res.get('similarity_score', 0.0):.4f} | {res.get('precision', 0.0):.1f} | "
                    f"{res.get('recall', 0.0):.1f} | {res.get('f1_score', 0.0):.1f} | {res.get('accuracy', 0.0):.1f} |\n"
                )

            # DeepEval & Ragas Reasoning
            f.write("\n## 3. LLM Diagnostic Reasoning\n\n")
            if "deepeval" in doc and "deepeval_reasoning" in doc["deepeval"]:
                f.write(f"> **DeepEval Reasoning**: {doc['deepeval']['deepeval_reasoning']}\n\n")
            if "ragas" in doc and "ragas_reasoning" in doc["ragas"]:
                f.write(f"> **Ragas Reasoning**: {doc['ragas']['ragas_reasoning']}\n\n")

    def _write_overall_markdown(self, overall_summary: Dict[str, Any], field_metrics: Dict[str, Dict[str, Any]], filepath: Path):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Global Extraction Performance Summary\n\n")
            f.write("## System-Level Aggregates\n\n")
            f.write("| Metric | Value |\n")
            f.write("| :--- | :---: |\n")
            f.write(f"| **Total Documents Evaluated** | {overall_summary.get('total_documents_evaluated', 0)} |\n")
            f.write(f"| **Overall Accuracy** | {overall_summary.get('overall_accuracy', 0.0):.2%} |\n")
            f.write(f"| **Average Precision** | {overall_summary.get('avg_precision', 0.0):.4f} |\n")
            f.write(f"| **Average Recall** | {overall_summary.get('avg_recall', 0.0):.4f} |\n")
            f.write(f"| **Average F1-Score** | {overall_summary.get('avg_f1_score', 0.0):.4f} |\n\n")

            f.write("## Field-Wise Metrics Across Dataset\n\n")
            f.write("| Field Name | Total Samples | TP | FP | FN | Accuracy | Precision | Recall | F1-Score | Avg Similarity |\n")
            f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
            for field, m in field_metrics.items():
                f.write(
                    f"| `{field}` | {m['total_samples']} | {m['TP']} | {m['FP']} | {m['FN']} | "
                    f"{m['accuracy']:.2%} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1_score']:.4f} | "
                    f"{m['avg_similarity_score']:.4f} |\n"
                )

    def _write_excel_report(self, overall_summary: Dict[str, Any], field_batch_metrics: Dict[str, Dict[str, Any]], doc_level_results: List[Dict[str, Any]]):
        excel_path = self.output_dir / "evaluation_report.xlsx"
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            pd.DataFrame([overall_summary]).to_excel(writer, sheet_name="Overall Summary", index=False)
            
            field_rows = [{"field_name": f, **m} for f, m in field_batch_metrics.items()]
            if field_rows:
                pd.DataFrame(field_rows).to_excel(writer, sheet_name="Field-Wise Metrics", index=False)