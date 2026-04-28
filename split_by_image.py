"""


HOW TO RUN
----------
From the project root:
  python -m scripts.split_by_image --dataset_dir data
"""

import pandas as pd
import argparse
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split, StratifiedKFold

# ----------------- CONFIG -----------------
DEFAULT_SEED = 42
N_FOLDS = 5
HOLDOUT_PORTIONS = 0.3


def plate_label(row: pd.Series) -> str:
    parts = [row["food_label_1"]]
    if pd.notna(row.get("food_label_2")):
        parts.append(row["food_label_2"])
    if pd.notna(row.get("food_label_3")):
        parts.append(row["food_label_3"])
    return ", ".join(parts)


def main():
    parser = argparse.ArgumentParser(
        description="Split the dataset on image level"
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

    # ----------------- Step 2: Split train and holdout -----------------
    train_df, holdout_df = train_test_split(
        df,
        test_size=HOLDOUT_PORTIONS,
        random_state=args.seed,
        stratify=df["portion_key"]
    )

    # ----------------- Step 3: Split holdout into val and test -----------------
    val_df, test_df = train_test_split(
        holdout_df,
        test_size=0.5,
        random_state=args.seed,
        stratify=holdout_df["portion_key"]
    )
    val_df = val_df.assign(split="holdout_val")
    test_df = test_df.assign(split="holdout_test")

    # ----------------- Step 4: Create 5-fold split on the train set -----------------
    train_df = train_df.copy()
    train_df["split"] = None
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=args.seed)

    for fold, (_, val_idx) in enumerate(skf.split(train_df, train_df["portion_key"])):
        train_df.iloc[val_idx, train_df.columns.get_loc("split")] = f"fold_{fold}"

    # ----------------- Step 5: Combine and save final split -----------------
    final_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    final_df = final_df[["images", "split"]]
    final_df.to_csv(annot_dir / "final_split.csv", index=False)
    print(f"Final split saved to: {annot_dir / 'final_split.csv'}")


if __name__ == "__main__":
    main()