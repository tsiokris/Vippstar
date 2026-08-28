"""
Classification dataset builder script

Builds a training-ready CSV for the classification task from metadata.csv
and splits.csv: combines food_label_1/2/3 into a single label per image
(verbatim join, original folder order preserved) and drops the weight
columns.

HOW TO RUN
----------
From the project root:
  python -m scripts.classification_dataset_builder --dataset_dir data

OUTPUT
------
<dataset_dir>/annotations/classification_dataset.csv
Columns: images, food_label, fold
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

# ── Main logic ───────────────────────────────────────────────────────────

def combine_labels(row: pd.Series) -> str:
    """Join food_label_1/2/3 verbatim, original folder order preserved."""
    labels = [row["food_label_1"], row["food_label_2"], row["food_label_3"]]
    labels = [str(label).strip() for label in labels if pd.notna(label)]
    return "_".join(labels)


def build_classification_dataset(metadata_path: Path, splits_path: Path) -> pd.DataFrame:
    metadata_df = pd.read_csv(metadata_path)
    splits_df = pd.read_csv(splits_path)

    df = pd.merge(metadata_df, splits_df, on="images")
    df["food_label"] = df.apply(combine_labels, axis=1)

    return df[["images", "food_label", "fold"]]


# ── Entry point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build a classification-ready CSV from metadata.csv and splits.csv."
    )
    parser.add_argument(
        "--dataset_dir",
        type=Path,
        required=True,
        help="Path to the dataset root folder (must contain annotations/metadata.csv and annotations/splits.csv).",
    )
    args = parser.parse_args()

    annot_dir = args.dataset_dir / "annotations"
    metadata_path = annot_dir / "metadata.csv"
    splits_path = annot_dir / "splits.csv"

    for path in (metadata_path, splits_path):
        if not path.exists():
            print(f"[ERROR] Could not find: {path}")
            sys.exit(1)

    df = build_classification_dataset(metadata_path, splits_path)

    output_path = annot_dir / "classification_dataset.csv"
    df.to_csv(output_path, index=False)
    print(f"\nClassification dataset saved to: {output_path}")
    print(f"  Images  : {len(df)}")
    print(f"  Classes : {df['food_label'].nunique()}")
