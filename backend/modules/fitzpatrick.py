"""
Module: Fitzpatrick Skin Tone Classification
- HSV analysis of skin region
- Returns Fitzpatrick Type I–VI
- Used to calibrate dark spot detection thresholds
"""

import cv2
import numpy as np


FITZPATRICK_LABELS = {
    1: {"label": "Type I",   "description": "Very fair — always burns, never tans",       "hex": "#FDDBB4"},
    2: {"label": "Type II",  "description": "Fair — usually burns, sometimes tans",        "hex": "#F5C99B"},
    3: {"label": "Type III", "description": "Medium — sometimes burns, always tans",       "hex": "#E8A87C"},
    4: {"label": "Type IV",  "description": "Olive — rarely burns, always tans",           "hex": "#C68C5A"},
    5: {"label": "Type V",   "description": "Brown — very rarely burns, tans darkly",      "hex": "#9A5C38"},
    6: {"label": "Type VI",  "description": "Dark brown/black — never burns, always dark", "hex": "#5C2C0C"},
}


def classify_skin_tone(img_bgr: np.ndarray) -> dict:
    """
    Classifies Fitzpatrick skin type using HSV skin region analysis.
    Uses the mean brightness (V channel) and saturation (S channel)
    of detected skin pixels as proxy for melanin content.
    """
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    # Broad skin color mask
    lower = np.array([0, 10, 60])
    upper = np.array([30, 200, 255])
    skin_mask = cv2.inRange(hsv, lower, upper)

    skin_pixels_hsv = hsv[skin_mask > 0]

    if len(skin_pixels_hsv) < 50:
        # Can't classify — default to Type III
        fitz_type = 3
    else:
        mean_v = float(np.mean(skin_pixels_hsv[:, 2]))  # brightness
        mean_s = float(np.mean(skin_pixels_hsv[:, 1]))  # saturation

        # Heuristic mapping: brighter + less saturated → lighter skin type
        # Darker + more saturated → darker skin type
        score = (255 - mean_v) * 0.6 + mean_s * 0.4

        if score < 30:    fitz_type = 1
        elif score < 55:  fitz_type = 2
        elif score < 80:  fitz_type = 3
        elif score < 110: fitz_type = 4
        elif score < 150: fitz_type = 5
        else:             fitz_type = 6

    info = FITZPATRICK_LABELS[fitz_type]
    return {
        "type": fitz_type,
        "label": info["label"],
        "description": info["description"],
        "hex": info["hex"],
    }
