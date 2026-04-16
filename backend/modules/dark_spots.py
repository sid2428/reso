"""
Module 4: Dark Spot Detection
- LAB color space adaptive thresholding
- Fitzpatrick-aware: uses relative L-channel comparison against user's own skin baseline
- Returns dark spot contours + coverage percentage
"""

import cv2
import numpy as np
from typing import List


def detect_dark_spots(img_bgr: np.ndarray, fitzpatrick_type: int = 3) -> dict:
    """
    Detects hyperpigmented regions (dark spots, post-inflammatory hyperpigmentation).

    fitzpatrick_type: 1–6 (lighter to darker skin)
    Returns contours, coverage %, and count.
    """
    # Convert to LAB color space — L channel is perceptual lightness
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l_channel = lab[:, :, 0]

    # ── Skin region mask ───────────────────────────────────────────────────
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    skin_lower = np.array([0, 15, 60])
    skin_upper = np.array([25, 180, 255])
    skin_mask = cv2.inRange(hsv, skin_lower, skin_upper)
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))

    # ── Fitzpatrick-aware threshold ────────────────────────────────────────
    # For darker skin tones, use relative comparison to the user's own skin baseline
    # rather than absolute L-channel values (prevents over-flagging on melanin-rich skin)
    skin_pixels = l_channel[skin_mask > 0]
    if len(skin_pixels) < 100:
        skin_mean = 150.0
        skin_std = 20.0
    else:
        skin_mean = float(np.mean(skin_pixels))
        skin_std = float(np.std(skin_pixels))

    # Adjust threshold sensitivity based on Fitzpatrick type
    # Lighter skin (I–II): tighter threshold; darker skin (V–VI): looser relative threshold
    std_multiplier = {1: 1.2, 2: 1.4, 3: 1.6, 4: 1.8, 5: 2.0, 6: 2.2}.get(fitzpatrick_type, 1.6)
    threshold = max(60.0, skin_mean - std_multiplier * skin_std)

    dark_mask = (l_channel < threshold).astype(np.uint8) * 255
    dark_mask = cv2.bitwise_and(dark_mask, skin_mask)

    # ── Morphological cleanup ──────────────────────────────────────────────
    kernel = np.ones((5, 5), np.uint8)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel)

    # ── Find contours ──────────────────────────────────────────────────────
    contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    valid_contours = []
    total_dark_area = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area < 40:  # filter tiny noise
            continue
        valid_contours.append(c.tolist())
        total_dark_area += area

    total_pixels = img_bgr.shape[0] * img_bgr.shape[1]
    coverage_pct = round(min(100.0, (total_dark_area / total_pixels) * 100), 2)

    severity = (
        "None" if coverage_pct < 1 else
        "Mild" if coverage_pct < 5 else
        "Moderate" if coverage_pct < 15 else
        "Significant"
    )

    return {
        "count": len(valid_contours),
        "coverage_percent": coverage_pct,
        "severity": severity,
        "contours": valid_contours,
        "threshold_used": round(threshold, 1),
        "skin_baseline_L": round(skin_mean, 1),
        "fitzpatrick_adjustment": std_multiplier,
    }
