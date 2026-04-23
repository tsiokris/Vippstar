"""
Phase 1 — Metadata builder script
================================
What this script does, in order:
  1. Walks your existing folder structure (food_type / Xg / images)
  2. Parses the weight in grams from the original folder name
  3. Writes dataset/annotations/metadata.csv
  4. Validates every image  (readable · min size · not blurry)            
  5. Prints a short summary report                                      

HOW TO RUN
----------
from the project root, run:
  python scripts/metadata_builder.py --dataset_dir /path/to/your/dataset

REQUIREMENTS
------------
  pip install pillow opencv-python pandas scikit-learn
"""


import argparse
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from src.utils.helpers import parse_weight
from src.utils.image_processing import validate_image

# ── Config ───────────────────────────────────────────────────────────────

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}
BLUR_THRESHOLD = 80
MIN_IMAGE_SIZE = 300


# ── Main Logic ───────────────────────────────────────────────────────────────

def create_metadata(dataset_dir: Path) -> pd.DataFrame:
    
    data_dir = dataset_dir / "raw"
    annot_dir = dataset_dir / "annotations"
    annot_dir.mkdir(parents=True, exist_ok=True)
    annot_dir = data_dir.parent / "annotations"

    if not data_dir.exists():
        print(f"[ERROR] Could not find: {data_dir}")
        print("Make sure your images are in:  data/raw/<food_type>/<weight_folder>/")
        sys.exit(1)

    print(f"\n{'='*60}")
    print("  Phase 1 — Dataset setup")
    print(f"{'='*60}\n")
    print(f"  Dataset root : {dataset_dir}")


    food_info = []
    skipped_folders = []  # folders we couldn't parse
    validation_issues = []
    total_images = 0
    ok_images = 0

    # ── Step 1: Discover all images ────────────────────────────────────────

    food_type_dirs = [d for d in data_dir.iterdir() if d.is_dir()]


    print(f"  Validatting images, this may take a while ...")
    
    for food_type_dir in food_type_dirs:
        portion_dirs = [p for p in food_type_dir.iterdir() if p.is_dir()]
        
        for portion_dir in portion_dirs:
            image_files = [f for f in portion_dir.iterdir() if f.is_file()]

            weight = parse_weight(portion_dir.name)
            if weight is None:
                skipped_folders.append(str(portion_dir))
                continue


            if not image_files:
                validation_issues.append({
                    "image": None,
                    "problem": f"No images found in: {portion_dir}"
                    })
                continue
            
            for image_file in image_files:
                food_info.append({
                    "food_label": food_type_dir.name,
                    "weight": weight,
                    "images": image_file,
                    "masks": np.nan  # placeholder for future columns (e.g. calories)  
                })

    # ── Step 2: Validate all images ────────────────────────────────────────   

            for image_file in image_files:
                total_images += 1
                problems = validate_image(image_file)
                if problems:
                    validation_issues.append({
                        "image": image_file,
                        "problem": " | ".join(problems)
                    })
                else:
                    ok_images += 1

    if validation_issues:
        report_path = annot_dir / "validation_issues.csv"
        pd.DataFrame(validation_issues).to_csv(report_path, index=False)
        print(f"  [WARNING] {len(validation_issues)} image(s) have issues.")
        print(f"  Full report saved at {report_path}")
        print()
    else:
        print(f"  All {total_images} images passed validation.")

            
    
    # ── Step 3: Metadata creation ────────────────────────────────────────────────
    print("\n  Writing metadata.csv ...")
    df = pd.DataFrame(food_info)
    csv_path = annot_dir / "metadata.csv"
    df.to_csv(csv_path, index=False)
    print(f"Metadata saved to: {csv_path}")

    if skipped_folders:
        print(f"  Skipped {len(skipped_folders)} folders (no weight pattern in name):")
        for f in skipped_folders:
            print(f"    - {f}")

    # ── Step 4: Summary report ────────────────────────────────────────────────

    num_food_labels = df["food_label"].nunique()
    num_portions = df[["food_label", "weight"]].drop_duplicates().shape[0]
    print(f"\n{'='*60}")
    print("  Summary")
    print(f"{'='*60}")
    print(f"  Food types  : {num_food_labels}")
    print(f"  Portions    : {num_portions}")
    print(f"  Images      : {total_images}  ({ok_images} ok, {len(validation_issues)} flagged)")
    print()


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
    create_metadata(args.dataset_dir)