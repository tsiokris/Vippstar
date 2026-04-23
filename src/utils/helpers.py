import re


# ── Functions ────────────────────────────────────────────────────────────

def parse_weight(folder_name: str) -> float | None:
    """
    Extract weight in grams from a folder name like '150g' or '150G'.
    Returns None if no weight pattern is found.
    """
    match = re.search(r"(\d+(?:\.\d+)?)\s*g", folder_name, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None