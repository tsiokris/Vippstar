# CLAUDE.md — Food Weight Estimation Project

## Project overview

This is a machine learning project that estimates the **weight (in grams)** and predicts the **food label** of a dish from a single smartphone photo. It also computes a **nutritional breakdown** (kcal, protein, fat, carbohydrates) by combining the predicted weight with a per-100g nutritional database provided by a nutritionist.

The project serves two purposes:
- A **research and clinical study** tool (deployed in a controlled setting)
- A **portfolio / GitHub ML engineering project** (designed to be readable and educational, not just performant)

---

## Goals

| Output | Description |
|---|---|
| Food label | The name/class of the food item (e.g. "lasagne", "burek") |
| Weight in grams | Predicted weight of the portion on the plate |
| Nutritional breakdown | kcal, protein, fat, carbs — derived from weight × per-100g values |

---

## Cuisines covered

The food types will be drawn from three cuisines. The final list is **not yet finalized** but will include dishes from:

- **Italian** cuisine
- **Bosnian** cuisine
- **Belgian** cuisine

Each cuisine will contribute a fixed set of food classes. The list will be updated in this file once confirmed with the research team.

---

## Dataset

### Structure on disk

Original structure from pilots (what you received):
```
dataset/raw/
├── <food_type>/          # e.g. "lasagne", "burek"
│   ├── 100g/             # folder name = weight in grams
│   ├── 150g/
│   └── 220g/
│       ├── img_01.jpg    # 20 images per portion, no special naming
│       └── ...
```

Target structure after running `phase1_setup.py`:
```
dataset/
├── raw/
│   ├── <food_type>/
│   │   ├── <food_type>_001/      # renamed to unique portion ID
│   │   ├── <food_type>_002/
│   │   └── ...
├── annotations/
│   ├── metadata.csv              # one row per portion
│   └── validation_issues.csv    # flagged images (if any)
└── nutrition/
    └── nutrition_per_100g.csv    # provided by nutritionist
```

> **Note:** The weight is parsed automatically from the original folder name (e.g. `150g` → `weight_g = 150.0`). The script `phase1_setup.py` handles all renaming and CSV generation.

### Metadata CSV schema (`metadata.csv`)

Each row represents one **portion** (not one image). All 20 images of that portion share the same row.

```
portion_id, food_type, weight_g, split
portion_001, lasagne, 312.4, train
```

| Column | Type | Description |
|---|---|---|
| `portion_id` | string | Unique ID matching folder name |
| `food_type` | string | Food class label |
| `weight_g` | float | Ground truth weight measured on a digital kitchen scale |
| `split` | string | `train`, `val`, or `test` |

### Nutritional database schema (`nutrition_per_100g.csv`)

Provided by the project nutritionist. Values are per 100g of the food item.

```
food_type, kcal, protein_g, fat_g, carbs_g
lasagne, 135.0, 7.2, 5.8, 14.1
```

---

## Image capture protocol

The following protocol was shared with all pilots. It must be respected for any new data collection.

| # | Rule |
|---|---|
| 1 | Capture at least 200 different images per food type (with varied weights) |
| 2 | Per portion: 10 photos from different positions + 10 from different tilt angles = **20 images per portion** |
| 3 | Weigh every portion/plate with a **digital kitchen scale** before photographing |
| 4 | 10 different plates/portions of the same food dish minimum |
| 5 | Nutritional analysis (per 100g) must be provided for each food type |
| 6 | Camera-to-plate distance: **20–70 cm** |
| 7 | A **top-down (vertical/90°) shot** must be included per portion |
| 8 | **Angled shots (20°–30°)** must be included per portion |
| 9 | Entire plate must be **fully visible** in frame |
| 10 | No overlap between different food items on the plate |
| 11 | A **credit card must be placed** next to the plate as a size reference |
| 12 | The credit card must **not touch the plate** |
| 13 | Use **controlled lighting** — no harsh shadows |
| 14 | Plate must be **non-reflective (matte)** |
| 15 | Image resolution must be **≥ 500×500 px** |
| 16 | Image must be **in focus**, not blurry |

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

### Stage 1 — Reference detection (credit card)

- Detect the credit card in the image (corner detection, edge detection, or a small object detector)
- Compute the **px/mm ratio** using the known card dimensions (85.6 × 54 mm)
- This ratio is passed to Stage 4 for area conversion

### Stage 2 — Food segmentation

- Produce a binary mask isolating the food item from the background and plate
- Recommended starting point: **SAM 2** (Segment Anything Model v2) or **YOLOv8-seg**
- The top-down image from each portion is the primary input for area estimation

### Stage 3 — Food classification

- Classify the food type from the masked/cropped region
- Recommended starting point: a **pretrained CNN** (e.g. EfficientNet-B0 or ResNet-50) fine-tuned on the project dataset
- Input: the image with the background masked out
- Output: food class label + confidence score

### Stage 4 — Weight and nutrition estimation

Weight estimation approach (to be decided — options ranked by simplicity):

| Option | Approach | Complexity |
|---|---|---|
| A | **2D area + fixed depth + density** | Simplest. Assume a typical height per food type. |
| B | **Monocular depth estimation** | Medium. Use a pretrained depth model (e.g. Depth Anything v2). |
| C | **Multi-view 3D reconstruction** | Most accurate. Use the 20 images per portion to reconstruct volume. |

> **Recommendation for v1:** Start with Option A. It is transparent, explainable, and easy to debug. Depth and density values per food type can be stored in a simple lookup table alongside the nutritional data.

Once weight (g) is predicted:
```
nutrition = (predicted_weight_g / 100) × nutrition_per_100g
```

---

## Tech stack

| Component | Tool |
|---|---|
| Language | Python 3.10+ |
| ML framework | PyTorch |
| Segmentation | SAM 2 / YOLOv8-seg |
| Classification | EfficientNet-B0 (torchvision) |
| Reference detection | OpenCV |
| Data handling | pandas, Pillow, numpy |
| Experiment tracking | MLflow or Weights & Biases (TBD) |
| Notebooks | Jupyter |

---

## Compute

- **Primary:** EU-funded research workstation (MedLab / Forth / Precious project) — high-capability GPU server
- **Secondary:** Local development machine
- **Optional:** Google Colab for lightweight experiments and sharing

---

## Project structure (planned)

```
food-weight-estimation/
├── CLAUDE.md                  # this file
├── README.md                  # public-facing GitHub description
├── data/
│   ├── raw/                   # original images (not committed to git)
│   ├── processed/             # resized, normalised images
│   └── annotations/           # metadata.csv, nutrition_per_100g.csv
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_segmentation.ipynb
│   ├── 03_classification.ipynb
│   └── 04_weight_estimation.ipynb
├── src/
│   ├── data/
│   │   ├── dataset.py         # PyTorch Dataset class
│   │   └── transforms.py      # augmentations
│   ├── models/
│   │   ├── segmentation.py
│   │   ├── classifier.py
│   │   └── weight_estimator.py
│   ├── reference/
│   │   └── card_detector.py   # credit card px/mm ratio
│   ├── nutrition/
│   │   └── lookup.py          # weight → kcal/macros
│   └── pipeline.py            # end-to-end inference
├── configs/
│   └── default.yaml           # hyperparameters, paths
├── scripts/
│   ├── train_classifier.py
│   ├── train_segmentation.py
│   └── evaluate.py
├── tests/
└── requirements.txt
```

---

## Development plan

The project is built in five sequential phases. Complete each phase fully before starting the next. Each phase produces something concrete and runnable.

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

Ensure all images follow this exact layout:

```
dataset/
├── raw/
│   ├── <food_type>/              # e.g. "lasagne", "burek"
│   │   ├── <portion_id>/         # e.g. "lasagne_001"
│   │   │   ├── top_down.jpg      # the 90° shot — always this exact name
│   │   │   ├── pos_02.jpg        # remaining position shots
│   │   │   ├── ...
│   │   │   ├── tilt_01.jpg       # tilt angle shots
│   │   │   └── ...
│   │   └── ...
│   └── ...
├── annotations/
│   └── metadata.csv
└── nutrition/
    └── nutrition_per_100g.csv
```

Naming rules:
- `portion_id` format: `<food_type>_<3-digit-number>` e.g. `lasagne_001`
- The top-down image must always be named `top_down.jpg` — Phase 4 depends on this
- All filenames lowercase, no spaces, use underscores

**Task 2 — Build metadata.csv**

Run `scripts/build_metadata.py` to auto-generate the CSV skeleton from the folder structure. Then manually fill in `weight_g` from the pilot scale records.

Final schema (one row per portion):
```
portion_id, food_type, weight_g, split
lasagne_001, lasagne, 312.4, train
```

**Task 3 — Image quality check (QC)**

Run `scripts/qc_images.py`. It produces `annotations/qc_report.csv` flagging:

| Check | Method | Flag if |
|---|---|---|
| Resolution | PIL image size | width or height < 500px |
| Blurriness | OpenCV Laplacian variance | variance < 100 |
| Top-down present | Check file exists | `top_down.jpg` missing |
| Credit card visible | Rectangle detection (OpenCV) | No card-shaped rectangle found |

Images that fail QC must be reviewed manually. Do not delete — mark as `qc_fail=True` in the report and exclude from training.

**Task 4 — Train/val/test split**

Run `scripts/split_dataset.py`. This adds the `split` column to `metadata.csv`.

Rules:
- Split ratio: **70% train / 15% val / 15% test**
- Split at the **portion level** — all 20 images of a portion go into the same split
- Use **stratified splitting** — each food type must appear in all three splits
- Set `random_seed = 42` for reproducibility

**Task 5 — Exploration notebook**

Open and run `notebooks/01_data_exploration.ipynb`. It should show:
- Total portions and images per food type
- Weight distribution (histogram) per food type
- Sample grid of top-down images (3 per food type)
- QC failure summary
- Confirmation that no portion appears in more than one split

### Phase 1 complete when
- [ ] All images are in the correct folder structure with consistent naming
- [ ] `metadata.csv` is complete — no missing `weight_g` values
- [ ] `qc_report.csv` exists and all failures have been reviewed
- [ ] `metadata.csv` has a `split` column with no data leakage
- [ ] `01_data_exploration.ipynb` runs end-to-end without errors

---

## Open decisions (to be resolved)

| Decision | Status | Notes |
|---|---|---|
| Final food type list | ⏳ Pending | Italian, Bosnian, Belgian — specific dishes TBD |
| Weight estimation approach | ⏳ Pending | Start with Option A (2D area + density) |
| Nutritional data | ⏳ Pending | Nutritionist is preparing per-100g values |
| Annotation tooling | ⏳ Pending | Need to choose tool for mask annotation (e.g. CVAT, Label Studio) |
| Experiment tracking tool | ⏳ Pending | MLflow vs Weights & Biases |
| Train/val/test split strategy | ⏳ Pending | Must split by portion, not by image, to avoid leakage |

---

## Important constraints and notes

- **Split by portion, not by image.** All 20 images of a portion must go into the same split. Never let images of the same portion appear in both train and test — this would cause data leakage and artificially inflate accuracy.
- **Top-down image is primary.** For area estimation, always use the top-down (90°) photo. Angled images are useful for depth cues and data augmentation, but not for area measurement.
- **One food item per plate** in the current phase. Multi-item plates are a future extension.
- **Do not commit raw images to git.** Use `.gitignore` and document the data download/access procedure in README.md.
- **Credit card detection must be validated** before any weight estimate is computed. If the card is not detected, the image should be flagged and skipped.

---

## Glossary

| Term | Meaning |
|---|---|
| Portion | A single plate of food with a known weight, photographed 20 times |
| Food type | The class label (e.g. "burek", "lasagne") |
| px/mm ratio | Pixels per millimetre — derived from the credit card reference |
| Mask | A binary image indicating which pixels belong to the food item |
| Density | Mass per unit volume (g/cm³) — used to convert area × depth → weight |
| Ground truth | The actual weight measured on a digital kitchen scale |
