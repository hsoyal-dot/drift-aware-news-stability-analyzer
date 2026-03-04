# reporting/report_generator.py
"""Report generator module.

Generates a markdown report summarizing claim drift analysis.
"""

from typing import List, Dict

def _format_claim(claim: Dict) -> str:
    """Format a single claim dictionary into a readable string."""
    subj = claim.get("subject", "")
    pred = claim.get("predicate", "")
    obj = claim.get("object", "")
    return f"- **{subj}** {pred} **{obj}**"

def generate_report(classified_groups: List[Dict], config: Dict) -> str:
    """Generate a markdown report from classified claim groups.

    Args:
        classified_groups: List of groups with `example_claim` and `drift_category`.
        config: Configuration dict, may contain report title.
    Returns:
        Markdown string.
    """
    title = config.get("report_title", "News Stability Analysis Report")
    lines = [f"# {title}\n"]
    categories = {"stable": [], "style_sensitive": [], "drift_prone": []}
    for grp in classified_groups:
        cat = grp.get("drift_category", "drift_prone")
        claim_text = _format_claim(grp.get("example_claim", {}))
        categories.setdefault(cat, []).append(claim_text)
    for cat, claims in categories.items():
        if not claims:
            continue
        header = cat.replace("_", " ").title()
        lines.append(f"## {header} Claims\n")
        lines.extend(claims)
        lines.append("\n")
    return "\n".join(lines)
