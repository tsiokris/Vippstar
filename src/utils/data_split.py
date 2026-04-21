from sklearn.model_selection import train_test_split


# ── Config ───────────────────────────────────────────────────────────────

TEST_RATIO = 0.15
VAL_RATIO = 0.15
RANDOM_SEED = 42


# ── Functions ─────────────────────────────────────────────────────────────

def assign_splits(portion_ids: list[str], food_types: list[str]) -> dict[str, str]:
    """
    Split portions into train / val / test stratified by food type.
    All 20 images of a portion stay in the same split — this is enforced
    because we split at the portion level, not the image level.
    """
    val_test_ratio = VAL_RATIO + TEST_RATIO

    train_ids, temp_ids, _, temp_labels = train_test_split(
        portion_ids, food_types,
        test_size=val_test_ratio,
        stratify=food_types,
        random_state=RANDOM_SEED,
    )

    # Split the temp set into val and test
    relative_test = 0.5
    val_ids, test_ids = train_test_split(
        temp_ids,
        test_size=relative_test,
        stratify=temp_labels,
        random_state=RANDOM_SEED,
    )

    splits = {}
    for pid in train_ids:
        splits[pid] = "train"
    for pid in val_ids:
        splits[pid] = "val"
    for pid in test_ids:
        splits[pid] = "test"
    return splits