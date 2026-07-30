import os
from typing import List, Optional
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class ProjectConfig(BaseModel):
    name: str = "Nexsora RAG Evaluation Pipeline"
    environment: str = "development"

class PathsConfig(BaseModel):
    ground_truth_dir: str = "./data/ground_truth"
    extracted_data_dir: str = "./data/extracted"
    output_dir: str = "./exports"

class LLMConfig(BaseModel):
    provider: str = "google"
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.0
    api_key_env_var: str = "GEMINI_API_KEY"

class ThresholdsConfig(BaseModel):
    min_precision: float = 0.85
    min_recall: float = 0.85
    min_semantic_similarity: float = 0.90

class FrameworksConfig(BaseModel):
    enable_deepeval: bool = True
    enable_ragas: bool = True
    enable_deterministic: bool = True

class EvaluationConfig(BaseModel):
    frameworks: FrameworksConfig = FrameworksConfig()
    thresholds: ThresholdsConfig = ThresholdsConfig()

class TelemetryConfig(BaseModel):
    enabled: bool = True
    otel_exporter_endpoint: str = "http://localhost:4317"
    service_name: str = "nexsora-eval-service"

class LoggingConfig(BaseModel):
    level: str = "INFO"
    log_to_file: bool = True
    log_file_path: str = "./logs/evaluation.log"

class ReportingConfig(BaseModel):
    formats: List[str] = ["json", "csv", "excel", "markdown"]

class Settings(BaseSettings):
    project: ProjectConfig = ProjectConfig()
    paths: PathsConfig = PathsConfig()
    llm: LLMConfig = LLMConfig()
    evaluation: EvaluationConfig = EvaluationConfig()
    telemetry: TelemetryConfig = TelemetryConfig()
    logging: LoggingConfig = LoggingConfig()
    reporting: ReportingConfig = ReportingConfig()

    @classmethod
    def load_from_yaml(cls, yaml_path: str = "config.yaml") -> "Settings":
        if os.path.exists(yaml_path):
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return cls(**data)
        return cls()