# Food Weight Estimation

A machine learning project that estimates the **weight in grams** of a food portion from a single smartphone photo, identifies the **food type**, and computes a **nutritional breakdown** (kcal, protein, fat, carbohydrates).

---

## What it does

Given a photo of a plate with a credit card placed next to it as a size reference, the system:

1. Detects the credit card and computes a pixel-to-millimetre scale
2. Segments the food item (isolates it from the plate and background)
3. Classifies the food type (e.g. lasagne, burek, pasta bolognese)
4. Estimates the weight in grams using the real-world area and food density
5. Computes kcal, protein, fat, and carbohydrates from the predicted weight

---

## Project status

| Phase | Description | Status |
|---|---|---|
| 1 | Data foundation — organize dataset, QC, train/val/test split | 🔄 In progress |
| 2 | Classification baseline — predict food label from image | ⏳ Pending |
| 3 | Segmentation + credit card detection | ⏳ Pending |
| 4 | Weight estimation — area × depth × density → grams | ⏳ Pending |
| 5 | Nutrition output + evaluation + write-up | ⏳ Pending |

---

## Dataset

Images were collected by study pilots following a controlled capture protocol. The dataset covers dishes from **Italian**, **Bosnian**, **Greek** and **Belgian** cuisines.

Each food type has multiple portions photographed at varied weights. Each portion has at least 20 images: 10 from different positions and 10 from different tilt angles (20°–30°). A credit card is placed in every shot as a fixed-size reference object (85.6 × 54 mm).

> Raw images are not included in this repository. See `CLAUDE.md` for the full data specification and folder structure.

---

## Repo structure

```
food-weight-estimation/
├── CLAUDE.md                        # full project spec (read this first)
├── README.md                        # this file
├── .gitignore
├── dataset/
│   ├── raw/                         # images — not committed to git
│   ├── annotations/
│   │   ├── metadata.csv             # portion_id, food_type, weight_g, split
│   │   └── validation_issues.csv    # QC failures (auto-generated)
│   └── nutrition/
│       └── nutrition_per_100g.csv   # kcal, protein, fat, carbs per 100g
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_classification.ipynb
│   ├── 03_segmentation.ipynb
│   └── 04_weight_estimation.ipynb
├── src/
│   ├── data/
│   ├── models/
│   ├── reference/
│   └── nutrition/
├── scripts/
│   └── phase1_setup.py              # Phase 1 setup script
├── configs/
│   └── default.yaml
└── requirements.txt
```

---

## Setup

**Requirements:** Python 3.10+, pip

```bash
# Clone the repo
git clone https://github.com/your-username/food-weight-estimation.git
cd food-weight-estimation

# Create a virtual environment
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Phase 1 — Running the setup script

Place your raw images in `dataset/raw/<food_type>/<weight_folder>/` then run:

```bash
python scripts/phase1_setup.py --dataset_dir dataset/
```

This will rename portion folders to unique IDs, parse weights from folder names, assign train/val/test splits, write `metadata.csv`, and validate all images.

---

## Tech stack

- **Python 3.10+** with **PyTorch**
- Segmentation: SAM 2 / YOLOv8-seg
- Classification: EfficientNet-B0 (torchvision)
- Reference detection: OpenCV
- Data: pandas, Pillow, NumPy

---

## Context

This project is part of the **Vippstar** clinical research initiative (EU-funded). The goal is to support dietary assessment in clinical settings for visually impared children by providing automated, image-based food weight and nutrition estimation.

---

## License

For research use only. Dataset and nutritional values are property of the research institution.