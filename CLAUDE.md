# CLAUDE.md — Food Weight Estimation Project

## Project context

This is Phase 1 of a larger ML pipeline that estimates food weight and nutritional content from smartphone images. Phase 1 is concerned only with dataset preparation — no model training happens here. The goal is to produce a clean, validated `metadata.csv` that can be loaded directly by a PyTorch `Dataset` class in Phase 2.

---

## Repo scope

This repo does four things:

1. Walks a raw image folder tree and parses food labels and weights from folder names
2. Builds `annotations/metadata.csv` — one row per image
3. Validates every image and flags issues in `annotations/validation_issues.csv`
4. Splits the dataset into a holdout set + 5-fold CV at the portion level, writing `annotations/splits.csv`

---

## Dataset

### Input structure

```
<dataset_dir>/
└── raw/
    └── <food_label>/               # e.g. "lasagne"  or  "chicken, rice, currysauce"
        └── <weight>/               # e.g. "150g"     or  "45g, 80g, 20g"
            ├── img_01.jpg
            └── ...
```

- The food label folder name is the label. Multiple dishes are comma-separated.
- The portion folder name encodes the weight(s) in grams. Multiple weights are comma-separated, matching the order of the labels.
- The number of labels and weights must match. Mismatched folders are skipped and logged.

### Output structure

```
<dataset_dir>/
└── annotations/
    ├── metadata.csv
    ├── validation_issues.csv
    └── splits.csv
```

### Metadata CSV schema

One row per image, fixed 8 columns:

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

---

## Scripts

### `scripts/metadata_builder.py`

Main entry point. Run from project root:

```bash
python -m scripts.metadata_builder --dataset_dir /path/to/dataset
```

`--dataset_dir` must point to the folder that contains `raw/`. Exits with an error if `raw/` is not found.

What it does in order:
1. Walks `raw/<food_label>/<weight>/` and collects all image files
2. Calls `parse_labels` and `parse_weights` on each folder name
3. Skips folders where no weight is found or label/weight counts don't match
4. Validates each image via `validate_image`
5. Writes `metadata.csv` and (if needed) `validation_issues.csv`
6. Prints a summary report

### `scripts/split_dataset.py`

Splits the dataset into a holdout set and 5-fold CV. Run from project root:

```bash
python -m scripts.split_dataset --dataset_dir data
```

`--dataset_dir` must point to the folder that contains `annotations/metadata.csv`. Accepts an optional `--seed` (default: 42).

What it does in order:
1. Loads `metadata.csv` and derives a **plate label** per row (all food labels joined with ` + `)
2. Derives a **portion key** per row (plate label + weight folder name)
3. For each plate, randomly assigns 3 of its 10 portions to `holdout` (30%)
4. Distributes the remaining 7 portions across 5 folds using `StratifiedKFold` (stratified by plate)
5. Writes `splits.csv` with columns `image_path` and `split`

**Key design decisions:**
- **Plate-level labels:** `chicken` and `chicken + rice` are distinct classes. Counting by `food_label_1` alone undercounts unique classes and biases the split.
- **Portion-level split:** All ~20 images of a portion stay together. Image-level splitting leaks near-duplicate images (same food, weight, session) across train and test.
- **Stratified by plate:** Each of the 42 plate combinations contributes proportionally to every split.

### `src/utils/helpers.py`

| Function | Input | Output | Example |
|---|---|---|---|
| `parse_labels(folder_name)` | folder name string | `list[str]` | `"chicken, rice"` → `["chicken", "rice"]` |
| `parse_weights(folder_name)` | folder name string | `list[float]` | `"45g, 80g"` → `[45.0, 80.0]` |
| `parse_weight(folder_name)` | folder name string | `float / None` | `"150g"` → `150.0` — legacy, unused |

### `src/utils/image_processing.py`

| Function | What it checks |
|---|---|
| `validate_image(path)` | Readable, minimum size (300px), not blurry (Laplacian variance < 80) |

---

## Phase 1 tasks

### Task 1 — Metadata builder
Build `metadata.csv` from the raw folder tree. Complete when:
- [x] All images have `food_label_1` and `weight_1` populated
- [x] Multi-label rows populate `food_label_2`/`weight_2` and `food_label_3`/`weight_3` correctly
- [x] No missing values in required columns

### Task 2 — Image QC
Validate all images. Complete when:
- [x] Every image has been checked for readability, resolution, and blur
- [x] `validation_issues.csv` is produced for any flagged images

### Task 3 — Dataset split
Split the dataset for model training. Complete when:
- [x] Holdout set contains exactly 30% of portions (3 per plate), never seen during training
- [x] Remaining 70% is assigned to 5 folds, stratified by plate combination
- [x] Split is at the portion level — no portion spans two splits
- [x] `splits.csv` is written with `image_path` and `split` columns

---

## Important constraints

- **Do not commit raw images to git.**
- **`raw/` must always exist.** The script does not create it — missing `raw/` exits with an error.
- **Portion folder names must encode the weight.** The regex `(\d+(?:\.\d+)?)\s*g` (case-insensitive) is used to extract weights. Folders that don't match are skipped.
- **Label and weight counts must match.** A folder named `"chicken, rice"` with a portion named `"45g, 80g, 20g"` (2 labels, 3 weights) is skipped and logged.
- **Maximum 3 labels per image.** The schema is fixed-width at 3 label/weight pairs.

---

## Tech stack

| Component | Tool |
|---|---|
| Language | Python 3.10+ |
| Data handling | pandas, numpy |
| Image handling | Pillow, opencv-python |
