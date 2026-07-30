import os
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class DocumentMatcher:
    def __init__(self, ground_truth_dir: str, extracted_data_dir: str, logger=None):
        self.gt_dir = Path(ground_truth_dir)
        self.ext_dir = Path(extracted_data_dir)
        self.logger = logger

    def get_matched_pairs(self) -> List[Tuple[Path, Path]]:
        """
        Executes Multi-Tier Document Matching:
        Tier 1: Exact Filename Match
        Tier 2: Stem/Base Name Match (e.g. inv_01.pdf vs inv_01.json)
        Tier 3: Internal Key Lookup (document_id / extraction_id)
        """
        matched_pairs = []
        if not self.gt_dir.exists() or not self.ext_dir.exists():
            if self.logger:
                self.logger.error(f"Directory missing: GT={self.gt_dir.exists()}, EXT={self.ext_dir.exists()}")
            return matched_pairs

        gt_files = list(self.gt_dir.glob("*.*"))
        ext_files = list(self.ext_dir.glob("*.*"))

        ext_by_exact = {f.name: f for f in ext_files}
        ext_by_stem = {f.stem: f for f in ext_files}
        
        # Build Tier 3 Map (Internal IDs)
        ext_by_internal_id = {}
        for f in ext_files:
            if f.suffix.lower() == ".json":
                try:
                    with open(f, "r", encoding="utf-8") as file:
                        data = json.load(file)
                        doc_id = data.get("document_id") or data.get("extraction_id") or data.get("s3_key")
                        if doc_id:
                            ext_by_internal_id[str(doc_id)] = f
                except Exception:
                    pass

        for gt_file in gt_files:
            # Tier 1: Exact Match
            if gt_file.name in ext_by_exact:
                matched_pairs.append((gt_file, ext_by_exact[gt_file.name]))
                if self.logger:
                    self.logger.verbose(f"[Match Tier 1] Exact: {gt_file.name}")
                continue

            # Tier 2: Stem Match
            if gt_file.stem in ext_by_stem:
                matched_pairs.append((gt_file, ext_by_stem[gt_file.stem]))
                if self.logger:
                    self.logger.verbose(f"[Match Tier 2] Stem: {gt_file.stem}")
                continue

            # Tier 3: Metadata Key Match
            if gt_file.suffix.lower() == ".json":
                try:
                    with open(gt_file, "r", encoding="utf-8") as file:
                        gt_data = json.load(file)
                        doc_id = gt_data.get("document_id") or gt_data.get("extraction_id") or gt_data.get("s3_key")
                        if doc_id and str(doc_id) in ext_by_internal_id:
                            matched_pairs.append((gt_file, ext_by_internal_id[str(doc_id)]))
                            if self.logger:
                                self.logger.verbose(f"[Match Tier 3] Internal ID ({doc_id}): {gt_file.name}")
                            continue
                except Exception:
                    pass

            if self.logger:
                self.logger.warning(f"[Match Mismatch] No corresponding extracted file found for GT: {gt_file.name}")

        return matched_pairs