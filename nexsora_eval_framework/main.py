import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file immediately
load_dotenv()

from config.settings import Settings
from core.logger import setup_logger
from core.telemetry import TelemetryManager
from core.ingestion import DocumentMatcher
from adapters.llm_factory import LLMFactory
from evaluators.deterministic import DeterministicEvaluator
from evaluators.field_evaluator import FieldEvaluator
from evaluators.deepeval_engine import DeepEvalEngine
from evaluators.ragas_engine import RagasEngine
from reporting.exporters import MultiFormatExporter


def main():
    parser = argparse.ArgumentParser(
        description="Nexsora RAG & Granular Field-Wise Extraction Evaluation Pipeline"
    )
    parser.add_argument(
        "--config", default="config.yaml", help="Path to runtime config.yaml file"
    )
    args = parser.parse_args()

    # 1. Load Runtime Settings from YAML
    settings = Settings.load_from_yaml(args.config)

    # 2. Initialize Framework Logger
    logger = setup_logger(
        name="nexsora_eval",
        log_level=settings.logging.level,
        log_file=settings.logging.log_file_path if settings.logging.log_to_file else None,
    )

    logger.info("Starting Nexsora RAG & Granular Field-Wise Evaluation Pipeline...")

    # 3. Initialize OpenTelemetry Metrics & Tracing
    telemetry = TelemetryManager(
        service_name=settings.telemetry.service_name,
        endpoint=settings.telemetry.otel_exporter_endpoint,
        enabled=settings.telemetry.enabled,
    )
    tracer = telemetry.get_tracer()

    with tracer.start_as_current_span("eval_pipeline_run"):
        # 4. Scan Directories and Match Ground Truth <-> Extracted File Pairs
        logger.info("Scanning data directories and pairing JSON files...")
        matcher = DocumentMatcher(
            ground_truth_dir=settings.paths.ground_truth_dir,
            extracted_data_dir=settings.paths.extracted_data_dir,
            logger=logger,
        )
        matched_pairs = matcher.get_matched_pairs()

        if not matched_pairs:
            logger.error("No matching document pairs found! Please check data paths.")
            sys.exit(1)

        logger.info(f"Successfully matched {len(matched_pairs)} document pairs to evaluate.")

        # 5. Initialize LLM Adapter if LLM-as-a-Judge Frameworks are Enabled
        llm = None
        if (
            settings.evaluation.frameworks.enable_deepeval
            or settings.evaluation.frameworks.enable_ragas
        ):
            llm = LLMFactory.create_llm(
                provider=settings.llm.provider,
                model_name=settings.llm.model_name,
                temperature=settings.llm.temperature,
                api_key_env_var=settings.llm.api_key_env_var,
            )

        # 6. Initialize Evaluation Engines
        deterministic_eval = DeterministicEvaluator()
        field_evaluator = FieldEvaluator(numeric_tolerance=0.01, fuzzy_threshold=0.85)
        deepeval_engine = (
            DeepEvalEngine(llm_model=llm)
            if settings.evaluation.frameworks.enable_deepeval
            else None
        )
        ragas_engine = (
            RagasEngine(llm_model=llm)
            if settings.evaluation.frameworks.enable_ragas
            else None
        )

        doc_level_results = []
        all_field_evaluations = []

        # 7. Iterate and Evaluate Each Document Pair
        for gt_path, ext_path in matched_pairs:
            logger.info(f"Evaluating: Ground Truth ({gt_path.name}) <==> Extracted ({ext_path.name})")
            doc_id = ext_path.stem

            with tracer.start_as_current_span("evaluate_document") as span:
                span.set_attribute("document.gt_file", gt_path.name)
                span.set_attribute("document.ext_file", ext_path.name)

                try:
                    with open(gt_path, "r", encoding="utf-8") as f:
                        gt_data = json.load(f)
                    with open(ext_path, "r", encoding="utf-8") as f:
                        ext_data = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load JSON files ({gt_path.name}, {ext_path.name}): {str(e)}")
                    span.record_exception(e)
                    continue

                # Unwrap payload if nested inside "extracted_data"
                gt_fields = (
                    gt_data.get("extracted_data", gt_data)
                    if isinstance(gt_data.get("extracted_data"), dict)
                    else gt_data
                )
                pred_fields = (
                    ext_data.get("extracted_data", ext_data)
                    if isinstance(ext_data.get("extracted_data"), dict)
                    else ext_data
                )

                # A. Document-level Deterministic Metric Computation
                det_results = (
                    deterministic_eval.evaluate(gt_data, ext_data)
                    if settings.evaluation.frameworks.enable_deterministic
                    else {}
                )

                # B. Granular Field-Wise Evaluation with Array Unrolling ('Detail' line items)
                field_results = field_evaluator.flatten_and_evaluate(gt_fields, pred_fields)
                all_field_evaluations.append(field_results)

                # C. DeepEval Correctness Evaluation
                deepeval_results = (
                    deepeval_engine.evaluate(gt_data, ext_data)
                    if deepeval_engine
                    else {}
                )

                # D. Ragas Evaluation
                ragas_results = (
                    ragas_engine.evaluate(gt_data, ext_data)
                    if ragas_engine
                    else {}
                )

                doc_record = {
                    "document_id": doc_id,
                    "gt_file": gt_path.name,
                    "ext_file": ext_path.name,
                    "deterministic": det_results,
                    "field_results": field_results,
                    "deepeval": deepeval_results,
                    "ragas": ragas_results,
                }
                doc_level_results.append(doc_record)

        # 8. Compute Batch Metrics per Field Key Across Dataset
        field_batch_metrics = field_evaluator.compute_batch_field_metrics(
            all_field_evaluations
        )

        # 9. Compute Overall Aggregate Metrics Across Dataset
        total_docs = len(doc_level_results)
        avg_precision = (
            sum(m["precision"] for m in field_batch_metrics.values()) / len(field_batch_metrics)
            if field_batch_metrics
            else 0.0
        )
        avg_recall = (
            sum(m["recall"] for m in field_batch_metrics.values()) / len(field_batch_metrics)
            if field_batch_metrics
            else 0.0
        )
        avg_f1 = (
            sum(m["f1_score"] for m in field_batch_metrics.values()) / len(field_batch_metrics)
            if field_batch_metrics
            else 0.0
        )
        avg_accuracy = (
            sum(m["accuracy"] for m in field_batch_metrics.values()) / len(field_batch_metrics)
            if field_batch_metrics
            else 0.0
        )

        overall_summary = {
            "total_documents_evaluated": total_docs,
            "overall_accuracy": round(avg_accuracy, 4),
            "avg_precision": round(avg_precision, 4),
            "avg_recall": round(avg_recall, 4),
            "avg_f1_score": round(avg_f1, 4),
        }

        # 10. Multi-Format Report Exporter (Exports overall + per-document JSON/Markdown)
        logger.info("Exporting multi-format evaluation reports...")
        exporter = MultiFormatExporter(output_dir=settings.paths.output_dir)
        exporter.export_all(
            overall_summary=overall_summary,
            field_batch_metrics=field_batch_metrics,
            doc_level_results=doc_level_results,
        )

        logger.info(
            f"Evaluation pipeline finished successfully! Reports exported to: '{settings.paths.output_dir}'"
        )

        # 11. Flush Telemetry Spans
        if telemetry.enabled:
            telemetry.shutdown()


if __name__ == "__main__":
    main()