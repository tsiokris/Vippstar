"""
Portion-level dataset splitter

Splits the dataset at the portion level — all images from the same portion
folder (same food, weight, and session) are kept together in a single split.
This prevents near-duplicate images from leaking across train and test sets.

Produces four splits:
- holdout_val  : 15% of portions, reserved for validation during development
- holdout_test : 15% of portions, reserved for final evaluation only
- fold_0–fold_4: 70% of portions split into 5 folds for cross-validation

The split unit is the portion (a folder of ~20 images). Stratification is
done by plate label (full food combination), so each plate type appears
proportionally in every split.

HOW TO RUN
----------
From the project root:
  python -m scripts.split_by_portion --dataset_dir data

Output
------
<dataset_dir>/annotations/splits_portion_level.csv
Columns: images, split
"""

import pandas as pd
import argparse
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold

# ----------------- CONFIG -----------------
DEFAULT_SEED = 42
N_FOLDS = 5
HOLDOUT_FRACTION = 0.3


def plate_label(row: pd.Series) -> str:
    parts = [row["food_label_1"]]
    if pd.notna(row.get("food_label_2")):
        parts.append(row["food_label_2"])
    if pd.notna(row.get("food_label_3")):
        parts.append(row["food_label_3"])
    return ", ".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Split the dataset on portion level"
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

    df = pd.read_csv(metadata_path)

    # ----------------- Step 1: Create food label and weight id for the stratification -----------------
    df["plate"] = df.apply(plate_label, axis=1)
    df["portion_key"] = df["plate"] + " | " + df["images"].apply(lambda p: Path(p).parent.name)

    # ----------------- Step 2: Create portion-level DataFrame -----------------
    portions_df = df[["plate", "portion_key"]].drop_duplicates().reset_index(drop=True)

    # ----------------- Step 3: Split train and holdout -----------------
    train_df, holdout_df = train_test_split(
        portions_df,
        test_size=HOLDOUT_FRACTION,
        random_state=args.seed,
        stratify=portions_df["plate"]
    )

    # ----------------- Step 4: Split holdout into val and test -----------------
    val_df, test_df = train_test_split(
        holdout_df,
        test_size=0.5,
        random_state=args.seed,
        stratify=holdout_df["plate"]
    )

    val_df = val_df.assign(split="holdout_val")
    test_df = test_df.assign(split="holdout_test")
    train_df["split"] = None    # Placeholder

    # ----------------- Step 5: Create 5-fold split on the train set -----------------
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=args.seed)
    for fold, (_, val_idx) in enumerate(skf.split(train_df, train_df["plate"])):
        train_df.iloc[val_idx, train_df.columns.get_loc("split")] = f"fold_{fold}"

    # ----------------- Step 6: Combine and map the splits ---------------------------------
    final_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    mapping = final_df.set_index("portion_key")["split"].to_dict()
    df["split"] = df["portion_key"].map(mapping)

    # ----------------- Step 7: Save the final split -----------------------------
    df[["images", "split"]].to_csv(annot_dir / "splits_portion_level.csv", index=False)
    print(f"Final split saved to: {annot_dir / 'splits_portion_level.csv'}")


if __name__ == "__main__":
    main()