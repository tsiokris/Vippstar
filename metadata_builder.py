"""
Phase 1 — Metadata builder script
================================
What this script does, in order:
  1. Walks your existing folder structure (food_type / Xg / images)
  2. Parses the weight in grams from the original folder name
  3. Assigns train / val / test splits (stratified by food type)           ## not implemented yet
  4. Writes dataset/annotations/metadata.csv
  5. Validates every image  (readable · min size · not blurry)             ## not implemented yet
  6. Prints a short summary report                                         ## not implemented yet

HOW TO RUN
----------
  python metadata_builder.py --dataset_dir /path/to/your/dataset

REQUIREMENTS
------------
  pip install pillow opencv-python pandas scikit-learn
"""


import argparse
import pandas as pd
import sys
from pathlib import Path
from src.utils.helpers import parse_weight



def create_metadata(dataset_dir: Path) -> pd.DataFrame:
    
    data_dir = dataset_dir / "raw"

    if not data_dir.exists():
        print(f"[ERROR] Could not find: {data_dir}")
        print("Make sure your images are in:  data/raw/<food_type>/<weight_folder>/")
        sys.exit(1)


    food_info = []
    skipped_folders = []  # folders we couldn't parse
    food_type_dirs = [d for d in data_dir.iterdir() if d.is_dir()]

    for food_type_dir in food_type_dirs:
        portion_dirs = [p for p in food_type_dir.iterdir() if p.is_dir()]
        
        for portion_dir in portion_dirs:
            image_files = [f for f in portion_dir.iterdir() if f.is_file()]

            weight = parse_weight(portion_dir.name)
            if weight is None:
                skipped_folders.append(str(portion_dir))
                continue
            
            for image_file in image_files:
                food_info.append({
                    "type": food_type_dir.name,
                    "weight": weight,
                    "path": image_file  
                })


    if skipped_folders:
        print(f"  Skipped {len(skipped_folders)} folders (no weight pattern in name):")
        for f in skipped_folders:
            print(f"    - {f}")

    return pd.DataFrame(food_info)



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