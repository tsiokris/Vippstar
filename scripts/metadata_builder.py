"""
Metadata builder script

Walks the raw image folder tree (raw/<food_label>/<weight>/*.jpg), parses
food labels and weights from folder names, validates every image, and
writes annotations/metadata.csv (one row per image that passes validation)
plus annotations/validation_issues.csv for any image that fails.

HOW TO RUN
----------
From the project root:
  python -m scripts.metadata_builder --dataset_dir /path/to/your/dataset

OUTPUT
------
<dataset_dir>/annotations/metadata.csv
Columns: food_label_1, weight_1, food_label_2, weight_2, food_label_3, weight_3, images, masks

<dataset_dir>/annotations/validation_issues.csv (only written if issues are found)
Columns: images, problem
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.helpers import parse_labels, parse_weights
from src.utils.image_processing import validate_image

# ── Config ───────────────────────────────────────────────────────────────

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}

METADATA_COLUMNS = [
    "food_label_1", "weight_1",
    "food_label_2", "weight_2",
    "food_label_3", "weight_3",
    "images", "masks",
]


# ── Main logic ───────────────────────────────────────────────────────────

def build_metadata(dataset_dir: Path) -> pd.DataFrame:
    raw_dir = dataset_dir / "raw"
    annot_dir = dataset_dir / "annotations"

    if not raw_dir.exists():
        print(f"[ERROR] Could not find: {raw_dir}")
        print("Make sure your images are in:  <dataset_dir>/raw/<food_label>/<weight>/")
        sys.exit(1)

    annot_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print("  Dataset setup")
    print(f"{'='*60}\n")

    food_rows = []
    skipped_folders = []
    validation_issues = []
    plates_seen = set()
    num_portions = 0
    total_images = 0
    ok_images = 0

    print("  Validating images, this may take a while ...")

    for label_dir in sorted(p for p in raw_dir.iterdir() if p.is_dir()):
        labels = parse_labels(label_dir.name)

        for portion_dir in sorted(p for p in label_dir.iterdir() if p.is_dir()):
            weights = parse_weights(portion_dir.name)

            if not weights:
                skipped_folders.append((str(portion_dir), "no weight pattern in folder name"))
                continue

            if len(labels) != len(weights):
                skipped_folders.append((
                    str(portion_dir),
                    f"label/weight count mismatch ({len(labels)} labels, {len(weights)} weights)",
                ))
                continue

            image_files = [
                f for f in portion_dir.iterdir()
                if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
            ]

            if not image_files:
                skipped_folders.append((str(portion_dir), "no image files found"))
                continue

            num_portions += 1
            plates_seen.add(label_dir.name)

            for image_file in image_files:
                total_images += 1
                image_path = str(image_file.resolve())
                problems = validate_image(image_file)

                if problems:
                    validation_issues.append({
                        "images": image_path,
                        "problem": " | ".join(problems),
                    })
                    continue

                ok_images += 1
                food_rows.append({
                    "food_label_1": labels[0],
                    "weight_1":     weights[0],
                    "food_label_2": labels[1] if len(labels) > 1 else np.nan,
                    "weight_2":     weights[1] if len(weights) > 1 else np.nan,
                    "food_label_3": labels[2] if len(labels) > 2 else np.nan,
                    "weight_3":     weights[2] if len(weights) > 2 else np.nan,
                    "images":       image_path,
                    "masks":        np.nan,
                })

    # ── Write outputs ────────────────────────────────────────────────────

    if validation_issues:
        issues_path = annot_dir / "validation_issues.csv"
        pd.DataFrame(validation_issues).to_csv(issues_path, index=False)
        print(f"\n  [WARNING] {len(validation_issues)} image(s) failed validation and were excluded.")
        print(f"  Full report saved at {issues_path}")
    else:
        print(f"\n  All {total_images} images passed validation.")

    df = pd.DataFrame(food_rows, columns=METADATA_COLUMNS)
    metadata_path = annot_dir / "metadata.csv"
    df.to_csv(metadata_path, index=False)
    print(f"\n  Metadata saved to: {metadata_path}")

    if skipped_folders:
        print(f"\n  Skipped {len(skipped_folders)} folder(s):")
        for path, reason in skipped_folders:
            print(f"    - {path}  ({reason})")

    # ── Summary ──────────────────────────────────────────────────────────

    print(f"\n{'='*60}")
    print("  Summary")
    print(f"{'='*60}")
    print(f"  Plates (food label combos) : {len(plates_seen)}")
    print(f"  Portions                   : {num_portions}")
    print(f"  Images                     : {total_images}  ({ok_images} ok, {len(validation_issues)} flagged)")
    print()

    return df


# ── Entry point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build metadata.csv from the raw food image folder tree."
    )
    parser.add_argument(
        "--dataset_dir",
        type=Path,
        required=True,
        help="Path to the dataset root folder (must contain a raw/ subfolder).",
    )
    args = parser.parse_args()
    build_metadata(args.dataset_dir)
