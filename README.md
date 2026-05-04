# Food Weight Estimation — Phase 1: Data Foundation

This repository is Phase 1 of a larger ML pipeline for image-based food weight and nutrition estimation. The scope here is limited to building a clean, validated dataset ready for model training.

> This is part of the **Vippstar** clinical research initiative (EU-funded), supporting dietary assessment for visually impaired children.

---

## What this repo does

Given raw pilot images organised in a specific folder structure, it:

1. Walks the folder tree and extracts food labels and weights from folder names
2. Builds `annotations/metadata.csv` — one row per image
3. Validates every image (readability, minimum resolution, blurriness)
4. Writes `annotations/validation_issues.csv` for any flagged images
5. Splits the dataset into a holdout set + 5-fold CV at the portion level, writing `annotations/splits_portion_level.csv`
6. Optionally splits at the image level for comparison, writing `annotations/splits_image_level.csv`
7. Prints a summary report

---

## Input structure

Images must be placed under a `raw/` folder following this layout:

**Single-label portion** (one dish per image):
```
<dataset_dir>/
└── raw/
    └── lasagne/
        └── 150g/
            ├── img_01.jpg
            └── ...
```

**Multi-label portion** (multiple dishes per image, up to 3):
```
<dataset_dir>/
└── raw/
    └── chicken, rice, currysauce/
        └── 45g, 80g, 20g/
            ├── img_01.jpg
            └── ...
```

Rules:
- The food label folder name is the label (comma-separated for multiple dishes)
- The portion folder name must contain the weight in grams (e.g. `150g`, `45g, 80g, 20g`)
- The number of labels and weights must match — mismatched folders are skipped
- `--dataset_dir` must point to the folder that **contains** `raw/`, not to `raw/` itself

---

## Output

### `annotations/metadata.csv` — one row per image

| Column | Type | Description |
|---|---|---|
| `food_label_1` | string | Primary food label |
| `weight_1` | float | Weight in grams for label 1 |
| `food_label_2` | string / NaN | Second food label (if present) |
| `weight_2` | float / NaN | Weight in grams for label 2 |
| `food_label_3` | string / NaN | Third food label (if present) |
| `weight_3` | float / NaN | Weight in grams for label 3 |
| `images` | string | Path to the image file |
| `masks` | string / NaN | Path to the mask (placeholder, not yet used) |

### `annotations/splits_portion_level.csv` and `annotations/splits_image_level.csv` — one row per image

Both files share the same schema:

| Column | Type | Description |
|---|---|---|
| `images` | string | Path to the image file (joins with `metadata.csv` on `images`) |
| `split` | string | `holdout_val`, `holdout_test`, `fold_0`, `fold_1`, `fold_2`, `fold_3`, or `fold_4` |

---

## Dataset split design

### Label definition — plates, not ingredients

A label is the full **plate combination**, not an individual ingredient. `chicken` and `chicken + rice + currysauce` are two different plates. This matters for counting unique classes (42 plates) and for stratifying the split correctly — grouping by `food_label_1` alone would undercount classes and bias the split.

### Splitting at the portion level to avoid data leakage

Each plate has ~10 portions (different weights, e.g. 100g, 150g, 200g …) and each portion has ~20 images photographed in the same session. Images within a portion are near-duplicates: same food, same weight, same background and lighting conditions. Splitting at the **image level** would allow near-duplicate images from the same session to appear in both train and test — a direct data leak.

The split is therefore performed at the **portion level**: all ~20 images of a portion travel together into the same split. No portion ever spans two splits.

### Split structure

- **15% holdout_val** — reserved for validation during development and model selection.
- **15% holdout_test** — reserved for final evaluation only; never used during training or tuning.
- **70% 5-fold CV** — distributed across 5 folds using `StratifiedKFold` (stratified by plate combination). Each fold serves as the validation set once; the other four are training.

### Two split strategies

| Strategy | File | Unit | Leakage risk |
|---|---|---|---|
| Portion-level (preferred) | `splits_portion_level.csv` | All images from a portion folder stay together | None |
| Image-level | `splits_image_level.csv` | Each image assigned independently | Near-duplicate images may appear in both train and test |

Both are kept to allow direct performance comparison in Phase 2.

### How to use splits in Phase 2

```python
import pandas as pd

meta = pd.read_csv("data/annotations/metadata.csv")
splits = pd.read_csv("data/annotations/splits_portion_level.csv")
df = meta.merge(splits, on="images")

holdout_test = df[df["split"] == "holdout_test"]

# Train on folds 1-4, validate on fold 0
train = df[df["split"].isin(["fold_1", "fold_2", "fold_3", "fold_4"])]
val   = df[df["split"] == "fold_0"]
```

---

## Repo structure

```
Vippstar/
├── CLAUDE.md
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                          # images — not committed to git
│   └── annotations/
│       ├── metadata.csv              # auto-generated
│       ├── validation_issues.csv     # auto-generated, only if issues found
│       ├── splits_portion_level.csv  # auto-generated
│       └── splits_image_level.csv    # auto-generated
├── src/
│   └── utils/
│       ├── helpers.py                # parse_labels, parse_weights
│       └── image_processing.py       # validate_image
└── scripts/
    ├── metadata_builder.py           # builds metadata.csv and validation_issues.csv
    ├── split_by_portion.py           # builds splits_portion_level.csv
    └── split_by_image.py             # builds splits_image_level.csv
```

---

## Setup

**Requirements:** Python 3.10+

```bash
git clone https://github.com/tsiokris/Vippstar.git
cd Vippstar

python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

pip install -r requirements.txt
```

---

## Running the scripts

```bash
# Build metadata.csv and validation_issues.csv
python -m scripts.metadata_builder --dataset_dir /path/to/your/dataset

# Split at the portion level (recommended)
python -m scripts.split_by_portion --dataset_dir data

# Split at the image level (for comparison)
python -m scripts.split_by_image --dataset_dir data
```

Must be run from the project root. `--dataset_dir` points to the parent of `raw/` for the metadata builder, and to the parent of `annotations/` for the split scripts.

---

## Project status

| Phase | Description | Status |
|---|---|---|
| 1 | Data foundation — metadata CSV, image QC | ✅ Complete |
| 2 | Classification baseline — predict food label from image | ⏳ Pending |
| 3 | Segmentation + credit card detection | ⏳ Pending |
| 4 | Weight estimation — area × depth × density → grams | ⏳ Pending |
| 5 | Nutrition output + evaluation | ⏳ Pending |

---

## License

For research use only. Dataset and nutritional values are property of the research institution.
