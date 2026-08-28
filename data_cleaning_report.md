# Data Cleaning Report — `data/raw/`

Summarizes the issues found in `data_quality_report.md` (2026-08-25 audit) and the cleanup actions taken between 2026-08-25 and 2026-08-27, with reasoning for each decision. This is the "what we did and why" record; `data_quality_report.md` has the original per-image findings and checklists.

**Starting point:** 83 classes, 543 portions, 11,283 raw images.
**Current state:** 80 classes, 534 portions, 11,092 raw images.

`annotations/metadata.csv` needs a fresh `metadata_builder.py` run to reflect all of the below — it currently still has rows for files that were deleted during this cleanup.

---

## 1. Blur validation threshold was too strict

**Problem:** `BLUR_THRESHOLD = 80` (Laplacian variance, in `src/utils/image_processing.py`) excluded 811 of 11,283 images (7.2%) from `metadata.csv`. Exclusions were extremely concentrated — some classes lost up to 98.3% of their images — rather than spread evenly.

**Investigation:** Manually viewed borderline-scoring images (variance ~17–50) across both smooth, low-texture foods (`Cheesepie`) and textured foods (a salad). None showed visible blur — sharp plate edges, legible text, well-defined food texture in all of them.

**Reasoning:** Laplacian variance measures edge/high-frequency content. A smooth food (porridge, a cheesepie's crust) naturally produces less of that even in perfect focus, so a single global threshold systematically penalizes smooth-textured foods rather than only catching genuine blur.

**Action:** Lowered `BLUR_THRESHOLD` from 80 to 30. Re-ran `metadata_builder.py`.

**Result:** Exclusions dropped from 811 to 10 images. The worst-hit classes recovered almost completely (before → after):
- `Wheat porridge, beef meatballs, boiled beet sallad`: 1 image / 1 portion → 60 images / 3 portions
- `stuffed pepper with chicken rice, sour cream`: 6 images / 2 portions → 64 images / 3 portions
- `Cheesepie`: 10 images / 2 portions → 56 images / 3 portions

**Open, unresolved:** One image (`Cheesepie/150g/IMG_9189.jpeg`, variance 17.85) still fails at the new threshold despite looking sharp on manual review. Left as-is — not worth chasing further for one image.

---

## 2. Non-food content contamination

**Problem:** `boiled cheakpeas/300g/IMG_2971.png` was a phone screenshot of a shopping listing, not a food photo. It passed every automated check (readable, correctly sized, not blurry) — only found because it was the one `.png` among 11,283 `.jpg`/`.jpeg` files with a different resolution/aspect ratio.

**Action:** Deleted.

**Reasoning:** Straightforward — it's not training data for a food classifier.

**Caveat carried forward:** this detection method only worked because this particular contaminant happened to stand out via file metadata. There's no guarantee other visually-normal contaminated images aren't still in the dataset.

---

## 3. Cross-label duplicates — same photo filed under two different food labels

**Problem:** 61 groups of byte-identical photos filed under two different, contradictory labels — the same input image would have two different "correct answers" for a classifier depending on which copy training picks up.

### 3a. Two isolated one-off collisions

- `IMG_1209.jpeg` — filed under both `fried egg, sweet pepper/100g, 100g/` and `traditional modlovan kozonac/300g/` (two unrelated dishes)
- `IMG_1298.jpeg` — filed under both `Cottage cheese dumplings, sour cream/100g, 50g/` and `sour cherry and poppy seed roll/200g/` (two unrelated dishes)

**Action:** Deleted the mistaken copy in each case, kept the correct label.
- `IMG_1209.jpeg` kept under `traditional modlovan kozonac/300g/`
- `IMG_1298.jpeg` kept under `Cottage cheese dumplings, sour cream/100g, 50g/`

**Reasoning:** Single stray files, not a systematic mixup — cheap to fix by hand once the correct label was identified.

### 3b. The big one — `Cheesepie` ↔ `Cottage cheese pudding with raisins` (59 of 61 groups)

Nearly all of both classes' images (60 each) paired up with a consistent weight offset, strongly suggesting one real photography session got filed under two labels rather than scattered copy-paste.

**Action:** Dropped `Cottage cheese pudding with raisins` as a class entirely.

**Reasoning:** Rather than manually arbitrating which of the two labels was correct for 59 image pairs, removing the weaker class resolves the contradiction outright — no photo has two labels anymore because one of the labels no longer exists. `Cottage cheese pudding with raisins` was picked to drop over `Cheesepie` because it also had the weaker raw folder structure (2 portions vs. Cheesepie's 3) — see section 4, same reasoning applies here too.

---

## 4. Same-label, different-weight duplicates — same photo claims two different weights

**Problem:** 43 groups where the same food label was used both times, but an identical photo sat under two different declared portion weights — contradicting the weight metadata for those portions (relevant since weight is being kept for possible future weight-estimation work).

### 4a. Two wholesale-duplication classes (40 of 43 groups)

- `buckwheat porrige with milk`: every image in `300g` (20 images) was a byte-copy of every image in `200g` (20 images) — i.e. the class only had 2 weight-folders total, and they were duplicates of each other.
- `Buckwheat porrige, rabbit meat`: the `200g, 100g` portion (20 images) was a full duplicate of the `200g, 200g` portion (20 images) — 2 of its 3 raw portions were the same underlying photos.

**Action:** Dropped both classes entirely.

**Reasoning — this is the "fewer than 3 usable portions" rule the split design needs:** the split strategy groups images by portion (so near-duplicate angles of the same plate never land in both train and test) and needs at least 3 real, distinct portions per class for a clean 3-fold stratified split. Deleting just the duplicate weight-folder from either class would have left it with only 1 unique portion of real content — worse than starting over, and still not splittable. Dropping the class outright was simpler and left no partial, unusable class behind.

This same reasoning is why `Cottage cheese pudding with raisins` (section 3b) was the one dropped instead of `Cheesepie`: it only had 2 raw portions to begin with, never 3, so it would have failed the same splitting requirement even without the duplicate-label problem.

**Classes dropped for having fewer than 3 usable portions (combining sections 3b and 4a):**
| Class | Raw portions | Why fewer than 3 usable |
|---|---|---|
| `Cottage cheese pudding with raisins` | 2 | Only ever had 2 raw portions |
| `buckwheat porrige with milk` | 2 | Both portions were duplicates of each other → effectively 1 unique portion |
| `Buckwheat porrige, rabbit meat` | 3 | 2 of the 3 portions were duplicates of each other → effectively 2 unique portions |

### 4b. Three stray pairs (3 of 43 groups)

- `Baked potatoes, cabbage pea salad`: `IMG_1570.jpeg` and `IMG_1571.jpeg`, each duplicated between `200g, 200g` and `300g, 300g`
- `Boiled pasta, baked fish, roasted pepper`: `IMG_7686.jpeg`, duplicated between `200g, 100g, 50g` and `300g, 150g, 75g`

**Action:** Kept the larger-weight copy, deleted the smaller-weight copy, for all 3.

**Reasoning:** Only 1-2 stray files per class, not enough to threaten the 3-portion minimum for either class — didn't need the drop-the-whole-class treatment that section 4a did.

---

## Summary of classes dropped

| Class | Reason |
|---|---|
| `Cottage cheese pudding with raisins` | Cross-label duplicate scandal with `Cheesepie` (59 photos) + only 2 raw portions to begin with |
| `buckwheat porrige with milk` | Wholesale duplicate portions left only 1 unique portion, below the 3-portion split minimum |
| `Buckwheat porrige, rabbit meat` | Wholesale duplicate portions left only 2 unique portions, below the 3-portion split minimum |

## What's left

All four issues from `data_quality_report.md` are resolved. Remaining steps are implementation, not further cleaning:

1. Re-run `metadata_builder.py` to sync `metadata.csv` with all the deletions above.
2. Build `scripts/split_dataset.py` (portion-grouped, stratified k-fold) — every remaining class now has ≥3 raw portions, so this can proceed without further exceptions.
3. Finish `scripts/classification_dataset_builder.py` (combine labels, drop weight columns, merge in the fold assignment).
