# Food Weight Estimation — Phase 1: Data Foundation

This repository is Phase 1 of a larger ML pipeline for image-based food weight and nutrition estimation. The scope here is limited to building a clean, validated dataset ready for model training.

> This is part of the **Vippstar** clinical research initiative (EU-funded), supporting dietary assessment for visually impaired children.

---

> **Rework in progress:** weight estimation has been dropped from the project agreement — classification is now the priority (weight data is still captured in case weight estimation resumes later). Dataset splitting has been removed for now pending a redesign; a classification-ready CSV builder is in progress.

## What this repo does

Given raw pilot images organised in a specific folder structure, it:

1. Walks the folder tree and extracts food labels and weights from folder names
2. Builds `annotations/metadata.csv` — one row per image that passes validation
3. Validates every image (readability, minimum resolution, blurriness); images that fail are excluded from `metadata.csv`
4. Writes `annotations/validation_issues.csv` for any flagged images
5. Prints a summary report

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

---

## Dataset splitting

Removed for now. The previous portion-level and image-level splitters were too generic relative to the current, more varied raw data and have been deleted along with their stale output. Splitting will be redesigned from scratch once the classification-ready CSV builder is in place — plate-level (not just `food_label_1`) stratification and portion-level grouping (to avoid near-duplicate leakage across train/test) remain the intended approach.

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
│       └── validation_issues.csv     # auto-generated, only if issues found
├── src/
│   └── utils/
│       ├── helpers.py                # parse_labels, parse_weights
│       └── image_processing.py       # validate_image
└── scripts/
    └── metadata_builder.py           # builds metadata.csv and validation_issues.csv
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
```

Must be run from the project root. `--dataset_dir` points to the folder that contains `raw/`.

---

## Project status

| Phase | Description | Status |
|---|---|---|
| 1 | Data foundation — metadata CSV, image QC | 🔄 Reworking (splitting removed pending redesign; classification CSV builder in progress) |
| 2 | Classification baseline — predict food label from image | ⏳ Pending |
| 3 | Segmentation + credit card detection | ⏸️ Dropped from project scope (may resume later) |
| 4 | Weight estimation — area × depth × density → grams | ⏸️ Dropped from project scope (may resume later) |
| 5 | Nutrition output + evaluation | ⏳ Pending |

---

## License

For research use only. Dataset and nutritional values are property of the research institution.
