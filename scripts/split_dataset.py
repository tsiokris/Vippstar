"""
Dataset splitter script

Assigns every image in metadata.csv to one of 3 cross-validation folds.
Splitting is done at the portion level (all images from one
food_label/weight folder stay together) and stratified by the combined
food label, so every class appears in every fold and near-duplicate images
from the same portion never leak across folds.

3 folds because the smallest classes in this dataset have exactly 3
portions — any more folds would leave those classes with empty folds.

HOW TO RUN
----------
From the project root:
  python -m scripts.split_dataset --dataset_dir data

REQUIREMENTS
------------
  pip install scikit-learn

OUTPUT
------
<dataset_dir>/annotations/splits.csv
Columns: images, fold   (fold is 0, 1, or 2)
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

# ── Config ───────────────────────────────────────────────────────────────

N_FOLDS = 3
DEFAULT_SEED = 42


# ── Main logic ───────────────────────────────────────────────────────────

def combine_labels(row: pd.Series) -> str:
    """Combine food_label_1/2/3 into a single string for stratification."""
    labels = [row["food_label_1"], row["food_label_2"], row["food_label_3"]]
    labels = [str(label).strip() for label in labels if pd.notna(label)]
    return "_".join(labels)


def assign_folds(df: pd.DataFrame, seed: int = DEFAULT_SEED) -> pd.DataFrame:
    df = df.copy()
    df["food_label"] = df.apply(combine_labels, axis=1)
    df["portion_key"] = df["images"].apply(lambda p: str(Path(p).parent))

    portions = df[["portion_key", "food_label"]].drop_duplicates().reset_index(drop=True)

    sgkf = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
    splits = sgkf.split(portions, portions["food_label"], groups=portions["portion_key"])

    portion_fold = {}
    for fold_idx, (_, val_idx) in enumerate(splits):
        for key in portions.iloc[val_idx]["portion_key"]:
            portion_fold[key] = fold_idx

    df["fold"] = df["portion_key"].map(portion_fold)
    return df


# ── Entry point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Assign 3-fold cross-validation splits to metadata.csv, "
                     "grouped by portion and stratified by food label."
    )
    parser.add_argument(
        "--dataset_dir",
        type=Path,
        required=True,
        help="Path to the dataset root folder (must contain annotations/metadata.csv).",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    annot_dir = args.dataset_dir / "annotations"
    metadata_path = annot_dir / "metadata.csv"

    if not metadata_path.exists():
        print(f"[ERROR] Could not find: {metadata_path}")
        print("Run scripts.metadata_builder first.")
        sys.exit(1)

    df = pd.read_csv(metadata_path)
    df = assign_folds(df, seed=args.seed)

    splits_path = annot_dir / "splits.csv"
    df[["images", "fold"]].to_csv(splits_path, index=False)
    print(f"\nSplits saved to: {splits_path}\n")

    summary = df.groupby("fold").agg(
        portions=("portion_key", "nunique"),
        images=("images", "count"),
        classes=("food_label", "nunique"),
    )
    print(summary)
    print()

    classes_per_fold = df.groupby("food_label")["fold"].nunique()
    missing = classes_per_fold[classes_per_fold < N_FOLDS]
    if not missing.empty:
        print(f"[WARNING] {len(missing)} class(es) do not appear in all {N_FOLDS} folds:")
        for label, n in missing.items():
            print(f"  - {label} (in {n} of {N_FOLDS} folds)")
