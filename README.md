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

`annotations/metadata.csv` — one row per image:

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
    └── metadata_builder.py           # main script
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

## Running the script

```bash
python -m scripts.metadata_builder --dataset_dir /path/to/your/dataset
```

Must be run from the project root. `--dataset_dir` points to the parent of `raw/`.

---

## Project status

| Phase | Description | Status |
|---|---|---|
| 1 | Data foundation — metadata CSV, image QC | 🔄 In progress |
| 2 | Classification baseline — predict food label from image | ⏳ Pending |
| 3 | Segmentation + credit card detection | ⏳ Pending |
| 4 | Weight estimation — area × depth × density → grams | ⏳ Pending |
| 5 | Nutrition output + evaluation | ⏳ Pending |

---

## License

For research use only. Dataset and nutritional values are property of the research institution.
