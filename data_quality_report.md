# Data Quality Report — `data/raw/`

Generated during the Phase 1 rework (metadata builder rewrite). Covers the full raw dataset: 83 plates, 543 portions, 11,283 images. All paths below are relative to `data/raw/`.

Check items off as you review/resolve them manually. All-`[x]`, back to me and I'll re-run the scan to confirm each is actually gone before we move on.

---

## Status as of 2026-08-26

| # | Issue | Status |
|---|---|---|
| 4 | Blur threshold too strict | **Resolved** — `BLUR_THRESHOLD` lowered 80 → 30, see below |
| 1 | Cross-label duplicates (61 groups) | **Resolved** — 2 one-off collisions fixed by deleting the mistaken copy (2026-08-26); remaining 59-group `Cheesepie`/`Cottage cheese pudding with raisins` block resolved by dropping `Cottage cheese pudding with raisins` as a class in the classification build |
| 2 | Same-label, different-weight duplicates (43 groups) | **Resolved** — see below |
| 3 | Non-food content contamination (1 image) | **Resolved** — `boiled cheakpeas/300g/IMG_2971.png` deleted |

---

## 1. Cross-label duplicates — same photo filed under two different food labels

> **Update:** the 2 one-off collisions are fixed — the mistaken copy was deleted from disk in each case, keeping only the correct label (`IMG_1209.jpeg` kept under `traditional modlovan kozonac/300g/`, deleted from `fried egg, sweet pepper/100g, 100g/`; `IMG_1298.jpeg` kept under `Cottage cheese dumplings, sour cream/100g, 50g/`, deleted from `sour cherry and poppy seed roll/200g/`). The remaining 59-group `Cheesepie` ↔ `Cottage cheese pudding with raisins` block will be resolved by dropping `Cottage cheese pudding with raisins` as a class in the classification build — the contested images leave the dataset along with the dropped label, no arbitration needed. Checklist left as-is below for the historical record.

**61 groups.** The same physical photo (byte-identical, confirmed via MD5) exists under two contradictory labels. This directly corrupts the classification signal — the same input image would have two different "correct answers" depending on which copy training picks up.

**Dominant pattern:** 59 of the 61 groups are between `Cheesepie` and `Cottage cheese pudding with raisins`. Both folders have 60 total images each, and nearly all of them pair up with a consistent weight offset (`Cheesepie/150g` ↔ `.../200g`, `100g` ↔ `150g`, `50g` ↔ `100g`). This looks like one real photography session that got filed under two labels, not scattered copy-paste — worth figuring out which label (if either) is actually correct before deciding what to do with these two classes.

Two unrelated one-off collisions round out the list.

- [ ] fried egg, sweet pepper/100g, 100g/IMG_1209.jpeg  <->  traditional modlovan kozonac/300g/IMG_1209.jpeg
- [ ] Cottage cheese dumplings, sour cream/100g, 50g/IMG_1298.jpeg  <->  sour cherry and poppy seed roll/200g/IMG_1298.jpeg
- [ ] Cheesepie/150g/IMG_9190.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9190.jpeg
- [ ] Cheesepie/150g/IMG_9128.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9128.jpeg
- [ ] Cheesepie/150g/IMG_9159.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9159.jpeg
- [ ] Cheesepie/150g/IMG_9198.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9198.jpeg
- [ ] Cheesepie/150g/IMG_9179.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9179.jpeg
- [ ] Cheesepie/150g/IMG_9189.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9189.jpeg
- [ ] Cheesepie/150g/IMG_9127.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9127.jpeg
- [ ] Cheesepie/150g/IMG_9140.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9140.jpeg
- [ ] Cheesepie/150g/IMG_9169.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9169.jpeg
- [ ] Cheesepie/150g/IMG_9144.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9144.jpeg
- [ ] Cheesepie/150g/IMG_9129.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9129.jpeg
- [ ] Cheesepie/150g/IMG_9126.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9126.jpeg
- [ ] Cheesepie/150g/IMG_9133.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9133.jpeg
- [ ] Cheesepie/150g/IMG_9158.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9158.jpeg
- [ ] Cheesepie/150g/IMG_9134.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9134.jpeg
- [ ] Cheesepie/150g/IMG_9145.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9145.jpeg
- [ ] Cheesepie/150g/IMG_9139.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9139.jpeg
- [ ] Cheesepie/150g/IMG_9160.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9160.jpeg
- [ ] Cheesepie/150g/IMG_9195.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9195.jpeg
- [ ] Cheesepie/150g/IMG_9174.jpeg  <->  Cottage cheese pudding with raisins/200g/IMG_9174.jpeg
- [ ] Cheesepie/100g/IMG_9104.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9104.jpeg
- [ ] Cheesepie/100g/IMG_9108.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9108.jpeg
- [ ] Cheesepie/100g/IMG_9068.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9068.jpeg
- [ ] Cheesepie/100g/IMG_9072.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9072.jpeg
- [ ] Cheesepie/100g/IMG_9092.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9092.jpeg
- [ ] Cheesepie/100g/IMG_9075.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9075.jpeg
- [ ] Cheesepie/100g/IMG_9078.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9078.jpeg
- [ ] Cheesepie/100g/IMG_9094.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9094.jpeg
- [ ] Cheesepie/100g/IMG_9099.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9099.jpeg
- [ ] Cheesepie/100g/IMG_9114.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9114.jpeg
- [ ] Cheesepie/100g/IMG_9069.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9069.jpeg
- [ ] Cheesepie/100g/IMG_9084.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9084.jpeg
- [ ] Cheesepie/100g/IMG_9071.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9071.jpeg
- [ ] Cheesepie/100g/IMG_9117.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9117.jpeg
- [ ] Cheesepie/100g/IMG_9093.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9093.jpeg
- [ ] Cheesepie/100g/IMG_9067.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9067.jpeg
- [ ] Cheesepie/100g/IMG_9059.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9059.jpeg
- [ ] Cheesepie/100g/IMG_9058.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9058.jpeg
- [ ] Cheesepie/100g/IMG_9080.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9080.jpeg
- [ ] Cheesepie/100g/IMG_9124.jpeg  <->  Cottage cheese pudding with raisins/150g/IMG_9124.jpeg
- [ ] Cheesepie/100g/IMG_8993.jpeg  <->  Cheesepie/50g/IMG_8993.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_8993.jpeg
- [ ] Cheesepie/50g/IMG_8994.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_8994.jpeg
- [ ] Cheesepie/50g/IMG_9046.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_9046.jpeg
- [ ] Cheesepie/50g/IMG_9019.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_9019.jpeg
- [ ] Cheesepie/50g/IMG_8998.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_8998.jpeg
- [ ] Cheesepie/50g/IMG_9029.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_9029.jpeg
- [ ] Cheesepie/50g/IMG_9004.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_9004.jpeg
- [ ] Cheesepie/50g/IMG_9048.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_9048.jpeg
- [ ] Cheesepie/50g/IMG_9040.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_9040.jpeg
- [ ] Cheesepie/50g/IMG_9039.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_9039.jpeg
- [ ] Cheesepie/50g/IMG_8978.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_8978.jpeg
- [ ] Cheesepie/50g/IMG_9020.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_9020.jpeg
- [ ] Cheesepie/50g/IMG_9052.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_9052.jpeg
- [ ] Cheesepie/50g/IMG_8989.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_8989.jpeg
- [ ] Cheesepie/50g/IMG_8977.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_8977.jpeg
- [ ] Cheesepie/50g/IMG_9003.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_9003.jpeg
- [ ] Cheesepie/50g/IMG_9049.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_9049.jpeg
- [ ] Cheesepie/50g/IMG_9043.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_9043.jpeg
- [ ] Cheesepie/50g/IMG_9028.jpeg  <->  Cottage cheese pudding with raisins/100g/IMG_9028.jpeg

---

## 2. Same-label, different-weight duplicates — same photo claims two different weights

> **Update — resolved 2026-08-27.** The two wholesale-duplication classes (`buckwheat porrige with milk`, `Buckwheat porrige, rabbit meat`) were deleted entirely — reason: deleting just the duplicate weight-folder from either class would have left one portion with a different image count than its siblings, complicating the portion-grouped split. Simpler and cleaner to drop both classes outright (40 of the 43 groups). The remaining 3 pairs (`Baked potatoes, cabbage pea salad` ×2, `Boiled pasta, baked fish, roasted pepper` ×1) were resolved by deleting the smaller-weight copy of each and keeping the larger-weight one — those were judged the wrong copies. All 43 groups accounted for. Checklist left as-is below for the historical record.

**43 groups.** Same food label both times, but the identical photo sits under two different declared portion weights — so the weight metadata contradicts itself for these portions. Matters for you specifically since weight is being kept for possible future weight-estimation work.

**Two are complete wholesale duplications** — every single image in one weight folder is a byte-copy of every image in the other:
- `buckwheat porrige with milk`: `300g` (20 images) is a full duplicate of `200g` (20 images)
- `Buckwheat porrige, rabbit meat`: `200g, 100g` portion (20 images) is a full duplicate of `200g, 200g` portion (20 images)

Two more have partial overlap (2 and 1 shared images respectively) — likely a copy-paste of a couple of files rather than a whole-folder mixup.

- [ ] buckwheat porrige with milk/200g/IMG_9597.jpeg  <->  buckwheat porrige with milk/300g/IMG_9597.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9641.jpeg  <->  buckwheat porrige with milk/300g/IMG_9641.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9638.jpeg  <->  buckwheat porrige with milk/300g/IMG_9638.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9648.jpeg  <->  buckwheat porrige with milk/300g/IMG_9648.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9642.jpeg  <->  buckwheat porrige with milk/300g/IMG_9642.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9651.jpeg  <->  buckwheat porrige with milk/300g/IMG_9651.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9618.jpeg  <->  buckwheat porrige with milk/300g/IMG_9618.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9588.jpeg  <->  buckwheat porrige with milk/300g/IMG_9588.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9621.jpeg  <->  buckwheat porrige with milk/300g/IMG_9621.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9626.jpeg  <->  buckwheat porrige with milk/300g/IMG_9626.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9604.jpeg  <->  buckwheat porrige with milk/300g/IMG_9604.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9591.jpeg  <->  buckwheat porrige with milk/300g/IMG_9591.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9649.jpeg  <->  buckwheat porrige with milk/300g/IMG_9649.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9633.jpeg  <->  buckwheat porrige with milk/300g/IMG_9633.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9599.jpeg  <->  buckwheat porrige with milk/300g/IMG_9599.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9628.jpeg  <->  buckwheat porrige with milk/300g/IMG_9628.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9607.jpeg  <->  buckwheat porrige with milk/300g/IMG_9607.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9632.jpeg  <->  buckwheat porrige with milk/300g/IMG_9632.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9623.jpeg  <->  buckwheat porrige with milk/300g/IMG_9623.jpeg
- [ ] buckwheat porrige with milk/200g/IMG_9587.jpeg  <->  buckwheat porrige with milk/300g/IMG_9587.jpeg
- [ ] Baked potatoes, cabbage pea salad/200g, 200g/IMG_1570.jpeg  <->  Baked potatoes, cabbage pea salad/300g, 300g/IMG_1570.jpeg
- [ ] Baked potatoes, cabbage pea salad/200g, 200g/IMG_1571.jpeg  <->  Baked potatoes, cabbage pea salad/300g, 300g/IMG_1571.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7969.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7969.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7947.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7947.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7949.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7949.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7918.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7918.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7904.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7904.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7906.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7906.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7912.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7912.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7935.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7935.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7927.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7927.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7917.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7917.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7924.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7924.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7955.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7955.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7958.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7958.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7914.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7914.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7940.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7940.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7908.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7908.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7932.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7932.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7919.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7919.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7913.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7913.jpeg
- [ ] Buckwheat porrige, rabbit meat/200g, 100g/IMG_7903.jpeg  <->  Buckwheat porrige, rabbit meat/200g, 200g/IMG_7903.jpeg
- [ ] Boiled pasta, baked fish, roasted pepper/200g, 100g, 50g/IMG_7686.jpeg  <->  Boiled pasta, baked fish, roasted pepper/300g, 150g, 75g/IMG_7686.jpeg

---

## 3. Non-food content contamination

- [x] `boiled cheakpeas/300g/IMG_2971.png` — **deleted 2026-08-26.** Was a phone screenshot of an OZON Armenia shopping listing for bamboo skewers, not a food photo. It was sharp and correctly sized, so none of the automated checks (blur/resolution/readability) caught it — only found by noticing it was the one `.png` among 11,283 `.jpg`/`.jpeg` files with a wildly different resolution/aspect ratio, then actually opening it.
  - **Caveat (still applies):** this detection method only worked because this particular contaminant happened to stand out via file metadata. There could be other non-food images that are visually normal JPEGs and wouldn't be caught this way — deleting this one is not a guarantee the dataset is now clean of contamination, just that the one findable-without-a-full-manual-pass instance is gone.

---

## 4. Blur exclusions — concentration and threshold notes

**Resolved 2026-08-26.** Manual review of borderline-scoring images (Laplacian variance 17–50) across multiple food types — including smooth foods like `Cheesepie` and textured ones like `salad with cheese chicken pepper and yogurt` — found no visible blur in any of them: sharp plate edges, legible card text, well-defined food texture. This confirmed the hypothesis below (smooth, low-texture foods score low on Laplacian variance even in focus) applied more broadly than just the smooth-food plates. `BLUR_THRESHOLD` was lowered from 80 to 30 in `src/utils/image_processing.py` and `metadata_builder.py` was re-run on the full dataset.

**Result:** exclusions dropped from 811 to **10** images (11,253 of 11,263 pass, vs. 10,472 of 11,283 before — note the raw image total also shifted slightly, 11,283 → 11,263, most likely minor filesystem/folder-scan variance between runs, not investigated further). The four worst-hit classes recovered almost completely:

| Class | Before (images / portions) | After (images / portions) |
|---|---|---|
| `Wheat porridge, beef meatballs, boiled beet sallad` | 1 / 1 | 60 / 3 |
| `stuffed pepper with chicken rice, sour cream` | 6 / 2 | 64 / 3 |
| `Cheesepie` | 10 / 2 | 56 / 3 |
| `Cottage cheese pudding with raisins` | 10 / 2 | 39 / 2 (raw folder only ever had 2 portions — being dropped as a class regardless, see section 1) |

**Open flag:** `Cheesepie/150g/IMG_9189.jpeg` (variance 17.85) was manually reviewed during this process and judged sharp on visual inspection, but it's still below the new threshold of 30 and remains excluded — along with 9 other images, all scoring 17–29. Either the threshold has a bit more room to drop, or the visual review (done on a downscaled render, not full 5712×4284 resolution) missed real softness. Not resolved further; flagging in case it matters later. Full list of the 10 remaining exclusions is in `annotations/validation_issues.csv`.

**Original finding (threshold 80), kept for reference:**

811 of 11,283 images (7.2%) were excluded for blur (`BLUR_THRESHOLD = 80` in `src/utils/image_processing.py`). Not evenly spread:

- 51 of 83 plates have at least one blurry image; 32 have zero.
- Top 10 plates account for 476 of the 811 exclusions (59%):

| Plate | Excluded | Total images | % excluded |
|---|---|---|---|
| Wheat porridge, beef meatballs, boiled beet sallad | 59 | 60 | 98.3% |
| stuffed pepper with chicken rice, sour cream | 58 | 64 | 90.6% |
| Cheese bun | 52 | 61 | 85.2% |
| Cheesepie | 50 | 60 | 83.3% |
| Cottage cheese pudding with raisins | 50 | 60 | 83.3% |
| Baked potatoes, cabbage pea salad | 54 | 75 | 72.0% |
| salad with cheese chicken pepper and yogurt | 46 | 65 | 70.8% |
| Couscous porridge with milk | 40 | 60 | 66.7% |
| Cottage cheese dumplings, sour cream | 37 | 63 | 58.7% |
| Rice porrige | 30 | 75 | 40.0% |

Note: `Cheesepie` and `Cottage cheese pudding with raisins` are both in this list and are also the two labels involved in the duplicate-photo issue in section 1 — some of their "blur" numbers are inflated by counting the same underlying blurry photos twice (once per fake label). Re-check their real blur rate after resolving section 1.

**Threshold analysis:** recomputed the actual Laplacian variance for the 323 excluded images across the top 6 plates (threshold is 80):
- 46% (148/323) score 60–80 — borderline, just under the cutoff
- 51% (165/323) score 30–60 — moderately blurry, wouldn't be saved by a small threshold tweak
- 3% (10/323) score below 30 — clearly, severely blurry

Pattern worth noting: the most-affected plates (`Cheesepie`, `Cottage cheese pudding with raisins`, `Rice porrige`, `Couscous porridge with milk`) are all smooth, low-texture foods. Laplacian variance measures edge/high-frequency content, so an in-focus bowl of porridge naturally scores lower than an in-focus salad — the single global threshold of 80 may be systematically penalizing smooth-textured foods rather than only catching genuine blur. Worth re-evaluating threshold (or using a per-content-type threshold) after fixing sections 1 and 2, since those are currently muddying the true blur numbers for the most-affected plates.

---

## Checked, not an issue

- 8 portions have 40 images instead of the usual ~20 (`Torta Fetta` ×3, `Mezzo Uovo` ×3, `Salsiccia` ×2). Verified all images in each are genuinely unique content — just larger photography sessions, no duplication bug.
- No unreadable or too-small images anywhere in the dataset — all 811 validation failures are blur-only.
