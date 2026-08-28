import cv2
from PIL import Image
from pathlib import Path


# ── Config ──────────────────────────────────────────────────────────────

BLUR_THRESHOLD = 30
MIN_IMAGE_SIZE = 300


# ── Functions ────────────────────────────────────────────────────────────

def is_blurry(image_path: Path, threshold: float = BLUR_THRESHOLD) -> bool:
    """
    Detect blur using the variance of the Laplacian.
    A low variance means the image lacks sharp edges → blurry.
    """
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return True  # unreadable counts as invalid
    return float(cv2.Laplacian(img, cv2.CV_64F).var()) < threshold


def validate_image(image_path: Path) -> list[str]:
    """
    Run all quality checks on a single image.
    Returns a list of problem strings (empty = all good).
    """
    problems = []

    # Check readable
    try:
        img = Image.open(image_path)
        img.verify()
    except Exception as e:
        problems.append(f"unreadable ({e})")
        return problems  # no point checking further

    # Re-open after verify (verify closes the file)
    try:
        img = Image.open(image_path)
        w, h = img.size
    except Exception as e:
        problems.append(f"could not read size ({e})")
        return problems

    # Check minimum resolution
    if w < MIN_IMAGE_SIZE or h < MIN_IMAGE_SIZE:
        problems.append(f"too small ({w}×{h} px, min {MIN_IMAGE_SIZE})")

    # Check blur
    if is_blurry(image_path):
        problems.append(f"blurry (Laplacian variance < {BLUR_THRESHOLD})")

    return problems