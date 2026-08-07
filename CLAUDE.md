# CLAUDE.md — Food Weight Estimation Project

## Project context

This is Phase 1 of a larger ML pipeline that estimates food weight and nutritional content from smartphone images. Phase 1 is concerned only with dataset preparation — no model training happens here. The goal is to produce a clean, validated `metadata.csv` that can be loaded directly by a PyTorch `Dataset` class in Phase 2.

---

## Repo scope

**Rework in progress:** weight estimation has been dropped from the project agreement — classification is now the priority. Weight data is still captured where present since weight estimation may return later. Dataset splitting has been removed for now pending a redesign (the old splitter was too generic); `split_by_portion.py` and `split_by_image.py` no longer exist.

This repo currently does three things:

1. Walks a raw image folder tree and parses food labels and weights from folder names
2. Builds `annotations/metadata.csv` — one row per image, labels kept verbatim from folder names
3. Validates every image and excludes failed images from `metadata.csv`, flagging them in `annotations/validation_issues.csv`

A second script producing a classification-ready CSV (normalized single combined label, weights dropped) is in progress and not yet in the repo.

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
    └── validation_issues.csv       # only written if issues are found
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
1. Walks `raw/<food_label>/<weight>/` and collects image files (filtered by extension: `.jpg`, `.jpeg`, `.png`)
2. Calls `parse_labels` and `parse_weights` on each folder name
3. Skips folders where no weight is found, label/weight counts don't match, or no image files are present
4. Validates each image via `validate_image`; only images that **pass** validation become rows in `metadata.csv` — failed images are excluded and logged in `validation_issues.csv` instead (both files use the `images` column, so they join directly)
5. Prints a summary report (plate count, portion count, image count)

`images` paths are written as resolved absolute paths, so `metadata.csv` stays valid regardless of the working directory it's later read from.

**Dataset splitting has been removed for now.** `split_by_portion.py` and `split_by_image.py` were deleted — the old design was too generic and its output was stale relative to the current raw data. Splitting will be redesigned once the classification CSV builder is in place.

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
**Removed for now.** The previous portion/image-level splitters were too generic and have been deleted along with their stale output CSVs. Splitting will be redesigned from scratch once the classification CSV builder (Task 4) is done.

### Task 4 — Classification-ready CSV
Build a second CSV from `metadata.csv` for the classification task: combine `food_label_1/2/3` into a single normalized label per image (lowercase, typo-corrected, joined with `_`, original folder order preserved) and drop the weight columns. Weight is kept in `metadata.csv` itself in case weight estimation resumes later. In progress.

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
