import time
from typing import Dict, Any
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource

class TelemetryManager:
    def __init__(self, service_name: str, endpoint: str, enabled: bool = True):
        self.enabled = enabled
        self.service_name = service_name
        self.endpoint = endpoint

        if self.enabled:
            resource = Resource.create({"service.name": self.service_name})

            # Setup Tracing
            trace_provider = TracerProvider(resource=resource)
            span_processor = BatchSpanProcessor(
                OTLPSpanExporter(endpoint=self.endpoint, insecure=True)
            )
            trace_provider.add_span_processor(span_processor)
            trace.set_tracer_provider(trace_provider)
            self.tracer = trace.get_tracer(self.service_name)

            # Setup Metrics
            self.metric_reader = PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=self.endpoint, insecure=True),
                export_interval_millis=1000  # Export every 1s
            )
            self.meter_provider = MeterProvider(resource=resource, metric_readers=[self.metric_reader])
            metrics.set_meter_provider(self.meter_provider)
            self.meter = metrics.get_meter(self.service_name)

            # Instruments
            self.eval_counter = self.meter.create_counter(
                "rag_evaluations_total",
                description="Total count of document extractions evaluated"
            )
            self.eval_duration = self.meter.create_histogram(
                "rag_evaluation_duration_seconds",
                description="Time taken to evaluate a single document"
            )
            
            # Use Gauges for scores!
            self.precision_gauge = self.meter.create_gauge(
                "rag_field_precision_score",
                description="Deterministic field precision score (0.0 - 1.0)"
            )
            self.recall_gauge = self.meter.create_gauge(
                "rag_field_recall_score",
                description="Deterministic field recall score (0.0 - 1.0)"
            )
            self.deepeval_score_gauge = self.meter.create_gauge(
                "rag_deepeval_correctness_score",
                description="DeepEval GEval correctness score (0.0 - 1.0)"
            )
        else:
            self.tracer = trace.get_tracer("noop")
            self.meter = None

    def get_tracer(self):
        return self.tracer

    def record_document_metrics(self, doc_name: str, duration: float, det_metrics: dict, deepeval_score: float):
        """Pushes structured document evaluation metrics to the OTel Collector."""
        if not self.enabled:
            return

        attributes = {"document_name": doc_name}

        # Record metrics
        self.eval_counter.add(1, attributes)
        self.eval_duration.record(duration, attributes)

        if det_metrics:
            prec = det_metrics.get("field_precision", 0.0)
            rec = det_metrics.get("field_recall", 0.0)
            self.precision_gauge.set(prec, attributes)
            self.recall_gauge.set(rec, attributes)

        if deepeval_score is not None:
            self.deepeval_score_gauge.set(deepeval_score, attributes)

    def shutdown(self):
        """Forces an immediate flush of metric buffers before process exits."""
        if self.enabled and hasattr(self, 'meter_provider'):
            try:
                self.meter_provider.force_flush()
                self.meter_provider.shutdown()
            except Exception:
                pass