# pipeline.py
"""Orchestrates the Drift-Aware News Stability Analyzer pipeline.

The main function `run_analysis` takes a raw news article (text) and returns a
human‑readable report.
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from .generation.variant_generator import generate_variants
from .extraction.claim_extractor import extract_claims
from .comparison.claim_comparator import compare_claims
from .reporting.report_generator import generate_report


def load_config(config_path: str = "config.yaml"):
    """Load configuration from a YAML file.

    Returns a dictionary with keys such as `model`, `num_variants`, etc.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_analysis(article_text: str, config_path: str = "config.yaml"):
    """Run the full analysis pipeline.

    Steps:
    1. Load configuration.
    2. Generate semantically‑consistent variants.
    3. Extract atomic claims from each variant.
    4. Compare claims across variants and classify drift.
    5. Generate a markdown report.
    """
    cfg = load_config(config_path)
    variants = generate_variants(article_text, cfg)
    claims = [extract_claims(v, cfg) for v in variants]
    comparison = compare_claims(claims, cfg)
    report_md = generate_report(comparison, cfg)
    return report_md

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python -m drift_analyzer.pipeline <article_file>")
        sys.exit(1)
    article_path = Path(sys.argv[1])
    article = article_path.read_text(encoding="utf-8")
    print(run_analysis(article))
