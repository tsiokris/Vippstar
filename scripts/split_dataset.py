"""
Phase 1 — Dataset splitter
==========================
What this script does, in order:
  1. Loads annotations/metadata.csv
  2. Groups images into portions (plate + weight folder)
  3. Assigns 3 portions per plate to holdout (30%)
  4. Assigns remaining 7 portions per plate across 5 folds via StratifiedKFold
  5. Writes annotations/splits.csv  (image_path, split)

HOW TO RUN
----------
From the project root:
  python -m scripts.split_dataset --dataset_dir data

REQUIREMENTS
------------
  pip install pandas scikit-learn numpy
"""

import argparse
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import StratifiedKFold


HOLDOUT_PORTIONS = 3
N_FOLDS = 5
DEFAULT_SEED = 42


def plate_label(row: pd.Series) -> str:
    parts = [row["food_label_1"]]
    if pd.notna(row.get("food_label_2")):
        parts.append(row["food_label_2"])
    if pd.notna(row.get("food_label_3")):
        parts.append(row["food_label_3"])
    return " + ".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Phase 1 — Split the food weight dataset into holdout + 5-fold CV."
    )
    parser.add_argument(
        "--dataset_dir",
        type=Path,
        default=Path("data"),
        help="Path to the dataset root (must contain annotations/metadata.csv).",
    )
    parser.add_argument(
        "--seed", 
        type=int, 
        default=DEFAULT_SEED
    )
    args = parser.parse_args()

    annot_dir = args.dataset_dir / "annotations"
    metadata_path = annot_dir / "metadata.csv"

    if not metadata_path.exists():
        print(f"[ERROR] Could not find: {metadata_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print("  Phase 1 — Dataset split")
    print(f"{'='*60}\n")

    df = pd.read_csv(metadata_path)

    # ── Step 1: Derive plate label and portion key per row ───────────────────
    df["plate"] = df.apply(plate_label, axis=1)
    df["portion_key"] = df["plate"] + " | " + df["images"].apply(
        lambda p: Path(p).parent.name
    )

    portions = df[["plate", "portion_key"]].drop_duplicates().reset_index(drop=True)

    # ── Step 2: Assign holdout — 3 portions per plate, randomly ─────────────
    rng = np.random.default_rng(args.seed)
    holdout_keys: set[str] = set()
    train_val_rows = []

    for plate, group in portions.groupby("plate"):
        keys = list(rng.permutation(group["portion_key"].tolist()))
        holdout_keys.update(keys[:HOLDOUT_PORTIONS])
        for k in keys[HOLDOUT_PORTIONS:]:
            train_val_rows.append({"plate": plate, "portion_key": k})

    train_val = pd.DataFrame(train_val_rows)

    # ── Step 3: Assign 5-fold CV to remaining 70% (stratified by plate) ─────
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=args.seed)
    fold_map: dict[str, str] = {}

    for fold_idx, (_, val_idx) in enumerate(skf.split(train_val, train_val["plate"])):
        for key in train_val.iloc[val_idx]["portion_key"]:
            fold_map[key] = f"fold_{fold_idx + 1}"

    # ── Step 4: Map splits back to every image row ───────────────────────────
    def assign_split(portion_key: str) -> str:
        if portion_key in holdout_keys:
            return "holdout"
        return fold_map[portion_key]

    df["split"] = df["portion_key"].apply(assign_split)

    splits_df = df[["images", "split"]].rename(columns={"images": "image_path"})

    # ── Step 5: Write splits.csv ─────────────────────────────────────────────
    output_path = annot_dir / "splits.csv"
    splits_df.to_csv(output_path, index=False)
    print(f"  Splits saved to: {output_path}\n")

    # ── Step 6: Summary report ────────────────────────────────────────────────
    total = len(splits_df)
    split_order = ["holdout"] + [f"fold_{i}" for i in range(1, N_FOLDS + 1)]

    image_counts = splits_df["split"].value_counts()
    portion_counts = (
        df[["portion_key", "split"]].drop_duplicates()["split"].value_counts()
    )

    print(f"{'='*60}")
    print("  Summary")
    print(f"{'='*60}")
    print(f"  {'split':<12}  {'portions':>8}  {'images':>8}  {'%':>6}")
    print(f"  {'-'*42}")
    for split in split_order:
        imgs = image_counts.get(split, 0)
        ports = portion_counts.get(split, 0)
        pct = imgs / total * 100
        print(f"  {split:<12}  {ports:>8}  {imgs:>8}  {pct:>5.1f}%")
    print(f"  {'-'*42}")
    print(f"  {'total':<12}  {len(portions):>8}  {total:>8}  {'100.0%':>6}")
    print()


if __name__ == "__main__":
    main()
