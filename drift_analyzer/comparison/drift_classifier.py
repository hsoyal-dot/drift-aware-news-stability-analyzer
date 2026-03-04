# comparison/drift_classifier.py
"""Drift classifier module.

Classifies groups of claims into stable, style‑sensitive, or drift‑prone based on
presence across variants and similarity scores.
"""

from typing import List, Dict

def classify_drift(groups: List[Dict], num_variants: int, config: Dict) -> List[Dict]:
    """Classify each claim group.

    Args:
        groups: Output from `compare_claims`, each with keys `example_claim`,
                `variants` (list of variant indices where the claim appears),
                and `size`.
        num_variants: Total number of generated variants.
        config: May contain thresholds for classification.
    Returns:
        List of dictionaries with added `drift_category` field.
    """
    stable_thresh = config.get("stable_threshold", 0.9)  # proportion of variants
    style_thresh = config.get("style_sensitive_threshold", 0.6)
    result = []
    for grp in groups:
        presence = len(set(grp["variants"])) / num_variants
        if presence >= stable_thresh and grp["size"] == num_variants:
            category = "stable"
        elif presence >= style_thresh:
            category = "style_sensitive"
        else:
            category = "drift_prone"
        new_grp = dict(grp)
        new_grp["drift_category"] = category
        result.append(new_grp)
    return result
