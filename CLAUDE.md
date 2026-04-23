# CLAUDE.md — Food Weight Estimation Project

## Project overview

This repo is the 1st phase of a bigger project that is a machine learning pipeline that estimates the **weight (in grams)** and predicts the **food label** of a dish from a single smartphone photo. It also computes a **nutritional breakdown** (kcal, protein, fat, carbohydrates) by combining the predicted weight with a per-100g nutritional database provided by a nutritionist.

Here we only care about the proper dataset developement. Model developement is a future advancement but its good to have the goal in mind.

## What the final project does

Given a photo of a plate with a credit card placed next to it as a size reference, the system:

1. Detects the credit card and computes a pixel-to-millimetre scale
2. Segments the food item (isolates it from the plate and background)
3. Classifies the food type (e.g. lasagne, burek, pasta bolognese)
4. Estimates the weight in grams using the real-world area and food density
5. Computes kcal, protein, fat, and carbohydrates from the predicted weight

## Goals

| Output | Description |
|---|---|
| Food label | The name/class of the food item (e.g. "lasagne", "burek") |
| Weight in grams | Predicted weight of the portion on the plate |
| Nutritional breakdown | kcal, protein, fat, carbs — derived from weight × per-100g values |

---

## Dataset

### Structure on disk

Original structure from pilots (what you received):
```
data/raw/
├── <food_type>/          # e.g. "lasagne", "burek"
│   ├── 100g/             # folder name = weight in grams
│   ├── 150g/
│   └── 220g/
│       ├── img_01.jpg    # at least 20 images per portion, no special naming
│       └── ...
```

Target structure:
```
data/
├── raw/
│   ├── <food_type>/
│   │   ├── <food_type>_001/      # renamed to unique portion ID
│   │   ├── <food_type>_002/
│   │   └── ...
└── annotations/
    ├── metadata.csv   
    └── validation_issues.csv    # flagged images (if any)

```

### Metadata CSV schema (`metadata.csv`)

Each row represents one **image** .

```
food_label, weight, images, masks
pizza, 25, path/to/img, path/to/mask
```

| Column | Type | Description |
|---|---|---|
| `food_label` | string | Food class label |
| `weight` | float | Ground truth weight measured on a digital kitchen scale |
| `images` | string | Relative path for the image |
| `masks` | string | Relative path for the mask |


### Credit card as reference object

The credit card (ISO/IEC 7810 ID-1 standard) has fixed real-world dimensions:
- **85.6 mm × 54.0 mm**

This allows computing a **pixel-per-millimetre (px/mm) ratio** from every image, which is used to convert segmentation mask areas from pixels into real-world units (mm² → cm²).

---

## ML pipeline

The pipeline has four sequential stages. The design principle is: **as simple as possible while remaining accurate**.

```
Input image
    │
    ▼
[Stage 1] Reference detection      → detect credit card → compute px/mm scale
    │
    ▼
[Stage 2] Food segmentation        → produce a pixel mask of the food item
    │
    ▼
[Stage 3] Food classification      → predict food label from the masked region
    │
    ▼
[Stage 4] Weight & nutrition       → area (px) × scale → real area (cm²)
                                      × assumed depth × density → grams
                                      × nutrition per 100g → kcal, macros
```



## Tech stack

| Component | Tool |
|---|---|
| Language | Python 3.10+ |
| Data handling | pandas, Pillow, numpy |
| Notebooks | Jupyter |

---

## Development plan

The project is built in five sequential phases. This repository represents Phase 1

| Phase | Name | Status | Goal |
|---|---|---|---|
| 1 | Data foundation | 🔄 Current | Clean dataset, metadata CSV, QC, train/val/test split |
| 2 | Classification baseline | ⏳ Pending | Train a CNN to predict food label from top-down image |
| 3 | Segmentation + reference detection | ⏳ Pending | Food masks + px/mm scale from credit card |
| 4 | Weight estimation | ⏳ Pending | Area × depth × density → grams |
| 5 | Nutrition output + evaluation | ⏳ Pending | Full pipeline, metrics, portfolio write-up |

---

## Phase 1 — Data foundation

### Goal
Produce a clean, well-organised dataset that is ready to be loaded by a PyTorch `Dataset` class in Phase 2. No model training happens in this phase.

### Tasks

**Task 1 — Folder structure**

Task 1 targets to create/construct the csv file that will contain the metadata. The endgoal of this task is to have a .py file that will take the input dataset and will either produce or update (if it already exists) the csv that contains the information for each food type and portion that will later be used in model training and the data loaders that we will create.

```
data/
├── raw/
│   ├── <food_type>/              # e.g. "lasagne", "burek"
│   │   ├── <portion_id>/         # e.g. "lasagne_001"
│   │   │   ├── img1.jpg      
│   │   │   ├── img2.jpg        
│   │   │   ├── ...
│   │   │   ├── ...       
│   │   │   └── ...
│   │   └── ...
│   └── ...
└── annotations/
    └── metadata.csv

```


Final schema (one row per portion):
```
food_label, weight, images, masks
pizza, 25, path/to/image, path/to/mask 
```

**Task 2 — Image quality check (QC)**

Creates a csv file with img problems

| Check | Method | Flag if |
|---|---|---|
| Resolution | PIL image size | width or height < 500px |
| Blurriness | OpenCV Laplacian variance | variance < 100 |


### Phase 1 complete when
- [ ] `metadata.csv` is complete — no missing `weight` valuesed
- [ ] `metadata.csv` has all 4 columns


---

## Important constraints and notes

- **Do not commit raw images to git.** Use `.gitignore` and document the data download/access procedure in README.md.

---

## Glossary

| Term | Meaning |
|---|---|
| Portion | A single plate of food with a known weight, photographed at least 20 times |
| Food type | The class label (e.g. "pizza", "lasagne") |
| px/mm ratio | Pixels per millimetre — derived from the credit card reference |
| Mask | A binary image indicating which pixels belong to the food item |
| Density | Mass per unit volume (g/cm³) — used to convert area × depth → weight |
| Ground truth | The actual weight measured on a digital kitchen scale |
