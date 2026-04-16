"""
Module 3: Facial Zone Mapping
- Uses MediaPipe 468-point face mesh
- Segments face into: Forehead, Left Cheek, Right Cheek, Nose, Chin, Jawline
- Returns per-zone lesion density and status
"""

import cv2
import numpy as np
from typing import List, Tuple

try:
    import mediapipe as mp
    _mp = mp.solutions.face_mesh
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

# MediaPipe landmark indices for each facial zone
ZONE_LANDMARK_INDICES = {
    "forehead":    [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                    397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                    172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109],
    "nose":        [1, 2, 98, 327, 326, 97, 2, 326, 49, 279, 48, 278,
                    219, 439, 218, 438, 237, 457, 44, 274, 45, 275],
    "left_cheek":  [36, 31, 228, 229, 230, 231, 232, 233, 244, 245, 122, 6,
                    196, 3, 51, 45, 4, 275, 281, 46, 37, 72, 38],
    "right_cheek": [266, 261, 448, 449, 450, 451, 452, 453, 464, 465, 351, 6,
                    419, 248, 281, 275, 4, 45, 51, 276, 267, 302, 268],
    "chin":        [175, 171, 208, 428, 199, 200, 201, 202, 204, 424, 422,
                    421, 418, 421, 171, 175],
    "jawline":     [172, 136, 150, 149, 176, 148, 152, 377, 378, 379, 365,
                    397, 288, 361, 323, 454, 356, 389, 251, 284, 332, 297, 338, 10],
}

ZONE_COLORS_BGR = {
    "forehead":   (255, 200, 0),
    "nose":       (0, 200, 255),
    "left_cheek": (180, 0, 255),
    "right_cheek":(255, 0, 180),
    "chin":       (0, 255, 180),
    "jawline":    (255, 100, 0),
}

ZONE_LABELS = {
    "forehead":    "Forehead",
    "nose":        "Nose",
    "left_cheek":  "Left Cheek",
    "right_cheek": "Right Cheek",
    "chin":        "Chin",
    "jawline":     "Jawline",
}


def _get_landmarks(img_bgr: np.ndarray):
    if not MEDIAPIPE_AVAILABLE:
        return None
    h, w = img_bgr.shape[:2]
    with _mp.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True,
                      min_detection_confidence=0.5) as fm:
        rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        results = fm.process(rgb)
        if not results.multi_face_landmarks:
            return None
        lm = results.multi_face_landmarks[0].landmark
        return [(int(l.x * w), int(l.y * h)) for l in lm]


def _fallback_zones(img_bgr: np.ndarray) -> dict:
    """Simple geometric zone split when MediaPipe unavailable."""
    h, w = img_bgr.shape[:2]
    return {
        "forehead":    {"polygon": [[0,0],[w,0],[w,h//3],[0,h//3]]},
        "nose":        {"polygon": [[w//3,h//3],[2*w//3,h//3],[2*w//3,2*h//3],[w//3,2*h//3]]},
        "left_cheek":  {"polygon": [[0,h//3],[w//3,h//3],[w//3,2*h//3],[0,2*h//3]]},
        "right_cheek": {"polygon": [[2*w//3,h//3],[w,h//3],[w,2*h//3],[2*w//3,2*h//3]]},
        "chin":        {"polygon": [[w//3,2*h//3],[2*w//3,2*h//3],[2*w//3,h],[w//3,h]]},
        "jawline":     {"polygon": [[0,2*h//3],[w,2*h//3],[w,h],[0,h]]},
    }


def map_facial_zones(img_bgr: np.ndarray, lesion_detections: List[dict] = None) -> dict:
    """
    Maps face into zones and counts lesions per zone.
    """
    h, w = img_bgr.shape[:2]
    landmarks = _get_landmarks(img_bgr)

    if landmarks:
        zone_polygons = {}
        for zone, indices in ZONE_LANDMARK_INDICES.items():
            pts = [landmarks[i] for i in indices if i < len(landmarks)]
            pts = list(set(pts))
            zone_polygons[zone] = {"polygon": pts}
    else:
        zone_polygons = _fallback_zones(img_bgr)

    # Count lesions per zone
    zone_results = {}
    for zone, data in zone_polygons.items():
        poly = np.array(data["polygon"], dtype=np.int32)
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [poly], 255)

        lesion_count = 0
        if lesion_detections:
            for det in lesion_detections:
                x1, y1, x2, y2 = det["bbox"]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                if 0 <= cy < h and 0 <= cx < w and mask[cy, cx] > 0:
                    lesion_count += 1

        status = "Clear" if lesion_count == 0 else ("Mild" if lesion_count <= 2 else "Affected")

        zone_results[zone] = {
            "label": ZONE_LABELS[zone],
            "lesion_count": lesion_count,
            "status": status,
            "polygon": data["polygon"],
            "color": "#{:02x}{:02x}{:02x}".format(*ZONE_COLORS_BGR[zone][::-1]),
        }

    return zone_results
