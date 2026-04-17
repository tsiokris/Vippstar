"""
Phase 1 — Dataset setup script
================================
What this script does, in order:
  1. Walks your existing folder structure (food_type / Xg / images)
  2. Renames each portion folder to a unique ID  e.g. pasta_bolognese_001
  3. Parses the weight in grams from the original folder name
  4. Assigns train / val / test splits (stratified by food type)
  5. Writes dataset/annotations/metadata.csv
  6. Validates every image  (readable · min size · not blurry)
  7. Prints a short summary report

HOW TO RUN
----------
  python phase1_setup.py --dataset_dir /path/to/your/dataset

REQUIREMENTS
------------
  pip install pillow opencv-python pandas scikit-learn
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split


# ── Config ────────────────────────────────────────────────────────────

MIN_IMAGE_SIZE = 300          # minimum width AND height in pixels
BLUR_THRESHOLD = 80.0         # Laplacian variance below this = blurry
TRAIN_RATIO    = 0.70
VAL_RATIO      = 0.15
TEST_RATIO     = 0.15         
RANDOM_SEED    = 42
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_weight(folder_name: str) -> float | None:
    """
    Extract weight in grams from a folder name like '150g' or '150G'.
    Returns None if no weight pattern is found.
    """
    match = re.search(r"(\d+(?:\.\d+)?)\s*g", folder_name, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None


def make_portion_id(food_type: str, index: int) -> str:
    """
    Build a unique, filesystem-safe portion ID.
    Example: 'Pasta Bolognese' + 3  →  'pasta_bolognese_003'
    """
    slug = food_type.lower().strip().replace(" ", "_")
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    return f"{slug}_{index:03d}"


def is_blurry(image_path: Path, threshold: float = BLUR_THRESHOLD) -> bool:
    """
    Detect blur using the variance of the Laplacian.
    A low variance means the image lacks sharp edges → blurry.
    """
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return True  # unreadable counts as invalid
    return float(cv2.Laplacian(img, cv2.CV_64F).var()) < threshold


def validate_image(image_path: Path) -> list[str]:
    """
    Run all quality checks on a single image.
    Returns a list of problem strings (empty = all good).
    """
    problems = []

    # Check readable
    try:
        img = Image.open(image_path)
        img.verify()
    except Exception as e:
        problems.append(f"unreadable ({e})")
        return problems  # no point checking further

    # Re-open after verify (verify closes the file)
    try:
        img = Image.open(image_path)
        w, h = img.size
    except Exception as e:
        problems.append(f"could not read size ({e})")
        return problems

    # Check minimum resolution
    if w < MIN_IMAGE_SIZE or h < MIN_IMAGE_SIZE:
        problems.append(f"too small ({w}×{h} px, min {MIN_IMAGE_SIZE})")

    # Check blur
    if is_blurry(image_path):
        problems.append(f"blurry (Laplacian variance < {BLUR_THRESHOLD})")

    return problems


def assign_splits(portion_ids: list[str], food_types: list[str]) -> dict[str, str]:
    """
    Split portions into train / val / test stratified by food type.
    All 20 images of a portion stay in the same split — this is enforced
    because we split at the portion level, not the image level.
    """
    val_test_ratio = VAL_RATIO + TEST_RATIO

    train_ids, temp_ids, _, temp_labels = train_test_split(
        portion_ids, food_types,
        test_size=val_test_ratio,
        stratify=food_types,
        random_state=RANDOM_SEED,
    )

    # Split the temp set into val and test
    relative_test = 0.5
    val_ids, test_ids = train_test_split(
        temp_ids,
        test_size=relative_test,
        stratify=temp_labels,
        random_state=RANDOM_SEED,
    )

    splits = {}
    for pid in train_ids:
        splits[pid] = "train"
    for pid in val_ids:
        splits[pid] = "val"
    for pid in test_ids:
        splits[pid] = "test"
    return splits


# ── Main logic ────────────────────────────────────────────────────────────────

def run(dataset_dir: Path) -> None:
    raw_dir   = dataset_dir / "raw"
    annot_dir = dataset_dir / "annotations"
    annot_dir.mkdir(parents=True, exist_ok=True)

    if not raw_dir.exists():
        print(f"[ERROR] Could not find: {raw_dir}")
        print("Make sure your images are in:  dataset/raw/<food_type>/<weight_folder>/")
        sys.exit(1)

    print(f"\n{'='*60}")
    print("  Phase 1 — Dataset setup")
    print(f"{'='*60}\n")
    print(f"  Dataset root : {dataset_dir}")
    print(f"  Raw images   : {raw_dir}\n")

    # ── Step 1: Discover all portions ────────────────────────────────────────
    portions = []         # list of dicts, one per portion
    skipped_folders = []  # folders we couldn't parse

    food_type_dirs = sorted([d for d in raw_dir.iterdir() if d.is_dir()])

    if not food_type_dirs:
        print("[ERROR] No food type folders found inside raw/")
        sys.exit(1)

    # Count index per food type for unique IDs
    food_type_counters: dict[str, int] = {}

    for ft_dir in food_type_dirs:
        food_type = ft_dir.name
        food_type_counters[food_type] = 0
        portion_dirs = sorted([d for d in ft_dir.iterdir() if d.is_dir()])

        for p_dir in portion_dirs:
            weight = parse_weight(p_dir.name)
            if weight is None:
                skipped_folders.append(str(p_dir))
                continue

            food_type_counters[food_type] += 1
            portion_id = make_portion_id(food_type, food_type_counters[food_type])

            portions.append({
                "portion_id":     portion_id,
                "food_type":      food_type,
                "weight_g":       weight,
                "original_folder": p_dir,
            })

    if not portions:
        print("[ERROR] No valid portion folders found.")
        print("  Expected folder names like: 150g, 200g, 95g")
        sys.exit(1)

    print(f"  Found {len(portions)} portions across {len(food_type_counters)} food types.")
    if skipped_folders:
        print(f"  Skipped {len(skipped_folders)} folders (no weight pattern in name):")
        for f in skipped_folders:
            print(f"    - {f}")

    # ── Step 2: Assign splits ─────────────────────────────────────────────────
    print("\n  Assigning train / val / test splits ...")

    all_ids   = [p["portion_id"] for p in portions]
    all_types = [p["food_type"]  for p in portions]

    try:
        split_map = assign_splits(all_ids, all_types)
    except ValueError as e:
        # Not enough samples per class for stratified split
        print(f"[WARNING] Stratified split failed: {e}")
        print("  Falling back to random split without stratification.")
        ids = all_ids[:]
        np.random.seed(RANDOM_SEED)
        np.random.shuffle(ids)
        n = len(ids)
        n_train = int(n * TRAIN_RATIO)
        n_val   = int(n * VAL_RATIO)
        split_map = {}
        for pid in ids[:n_train]:           split_map[pid] = "train"
        for pid in ids[n_train:n_train+n_val]: split_map[pid] = "val"
        for pid in ids[n_train+n_val:]:     split_map[pid] = "test"

    for p in portions:
        p["split"] = split_map[p["portion_id"]]

    # ── Step 3: Rename portion folders ────────────────────────────────────────
    print("\n  Renaming portion folders to unique IDs ...")
    rename_errors = []

    for p in portions:
        old_path = p["original_folder"]
        new_path = old_path.parent / p["portion_id"]

        if old_path == new_path:
            continue
        if new_path.exists():
            rename_errors.append(f"  Target already exists: {new_path}")
            continue
        try:
            old_path.rename(new_path)
        except Exception as e:
            rename_errors.append(f"  Could not rename {old_path.name}: {e}")

    if rename_errors:
        print("[WARNING] Some folders could not be renamed:")
        for err in rename_errors:
            print(err)
    else:
        print("  All folders renamed successfully.")

    # ── Step 4: Write metadata.csv ────────────────────────────────────────────
    print("\n  Writing metadata.csv ...")

    rows = [
        {
            "portion_id": p["portion_id"],
            "food_type":  p["food_type"],
            "weight_g":   p["weight_g"],
            "split":      p["split"],
        }
        for p in portions
    ]

    df = pd.DataFrame(rows)
    csv_path = annot_dir / "metadata.csv"
    df.to_csv(csv_path, index=False)
    print(f"  Saved → {csv_path}")

    # ── Step 5: Validate all images ───────────────────────────────────────────
    print("\n  Validating images (this may take a moment) ...")

    validation_issues = []
    total_images = 0
    ok_images    = 0

    for p in portions:
        portion_path = raw_dir / p["food_type"] / p["portion_id"]
        if not portion_path.exists():
            continue  # rename may have failed

        image_files = [
            f for f in portion_path.iterdir()
            if f.suffix in IMAGE_EXTENSIONS
        ]

        if not image_files:
            validation_issues.append({
                "portion_id": p["portion_id"],
                "image":      "(none)",
                "problems":   "no images found in folder",
            })
            continue

        for img_path in sorted(image_files):
            total_images += 1
            problems = validate_image(img_path)
            if problems:
                validation_issues.append({
                    "portion_id": p["portion_id"],
                    "image":      img_path.name,
                    "problems":   " | ".join(problems),
                })
            else:
                ok_images += 1

    # Save validation report
    if validation_issues:
        report_path = annot_dir / "validation_issues.csv"
        pd.DataFrame(validation_issues).to_csv(report_path, index=False)
        print(f"  [WARNING] {len(validation_issues)} image(s) have issues.")
        print(f"  Full report saved → {report_path}")
    else:
        print(f"  All {total_images} images passed validation.")

    # ── Step 6: Summary report ────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  Summary")
    print(f"{'='*60}")
    print(f"  Food types  : {len(food_type_counters)}")
    print(f"  Portions    : {len(portions)}")
    print(f"  Images      : {total_images}  ({ok_images} ok, {len(validation_issues)} flagged)")
    print()

    split_counts = df["split"].value_counts()
    for split in ["train", "val", "test"]:
        count = split_counts.get(split, 0)
        pct   = 100 * count / len(df) if len(df) else 0
        print(f"  {split:<6} : {count} portions  ({pct:.0f}%)")

    print()
    print("  Portions per food type:")
    for ft, count in df.groupby("food_type")["portion_id"].count().items():
        print(f"    {ft:<30} {count}")

    print()
    print("  Weight statistics (grams):")
    print(f"    Min    : {df['weight_g'].min():.1f} g")
    print(f"    Max    : {df['weight_g'].max():.1f} g")
    print(f"    Mean   : {df['weight_g'].mean():.1f} g")
    print(f"    Median : {df['weight_g'].median():.1f} g")

    print(f"\n{'='*60}")
    print("  Phase 1 complete.")
    print(f"{'='*60}\n")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Phase 1 — Organize and validate the food weight dataset."
    )
    parser.add_argument(
        "--dataset_dir",
        type=Path,
        required=True,
        help="Path to the dataset root folder (must contain a raw/ subfolder).",
    )
    args = parser.parse_args()
    run(args.dataset_dir)
