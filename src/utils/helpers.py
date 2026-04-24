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


def parse_labels(folder_name: str) -> list[str]:
    """
    Extract one or more food labels from a folder name.

    Single label  : "lasagne"                    → ["lasagne"]
    Multiple labels: "chicken, rice, currysauce" → ["chicken", "rice", "currysauce"]

    Labels are split on commas and stripped of surrounding whitespace.
    Always returns a list, even for a single label.
    """
    return [label.strip() for label in folder_name.split(",") if label.strip()]


def parse_weights(folder_name: str) -> list[float]:
    """
    Extract one or more weights in grams from a portion folder name.

    Single weight  : "150g"          → [150.0]
    Multiple weights: "45g, 80g, 20g" → [45.0, 80.0, 20.0]
    No match       : "lasagne_001"   → []

    Case-insensitive. Always returns a list.
    """
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*g", folder_name, re.IGNORECASE)
    return [float(m) for m in matches]