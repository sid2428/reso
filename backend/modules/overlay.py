"""
Module: Overlay Compositor
- Alpha-blends all analysis results onto the original face image
- Generates lesion density heatmap (KDE-based)
- Outputs: annotated_img, heatmap_img
"""

import cv2
import numpy as np
from typing import Tuple

LESION_COLORS = {
    "comedonal":    (0, 200, 0),
    "inflammatory": (0, 0, 220),
    "nodular":      (200, 0, 0),
}
ZONE_ALPHA = 0.30
BOX_THICKNESS = 2


def _draw_lesion_boxes(img: np.ndarray, lesion_result: dict) -> np.ndarray:
    overlay = img.copy()
    for det in lesion_result.get("detections", []):
        x1, y1, x2, y2 = det["bbox"]
        cls_name = det.get("class_name", "inflammatory")
        color = LESION_COLORS.get(cls_name, (0, 200, 0))
        conf = det.get("confidence", 0.5)
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, BOX_THICKNESS)
        label = f"{cls_name[:3].upper()} {conf:.0%}"
        cv2.putText(overlay, label, (x1, max(0, y1 - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)
    return overlay


def _draw_zone_overlays(img: np.ndarray, zone_result: dict) -> np.ndarray:
    overlay = img.copy()
    for zone_key, data in zone_result.items():
        poly = data.get("polygon", [])
        if not poly:
            continue
        pts = np.array(poly, dtype=np.int32)
        hex_color = data.get("color", "#ffffff")
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        cv2.fillPoly(overlay, [pts], (b, g, r))
        # Label centroid
        M = cv2.moments(pts)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            label = data.get("label", zone_key)[:3].upper()
            cv2.putText(img, label, (cx - 10, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (b, g, r), 1, cv2.LINE_AA)
    return cv2.addWeighted(overlay, ZONE_ALPHA, img, 1 - ZONE_ALPHA, 0)


def _draw_dark_spot_contours(img: np.ndarray, dark_spot_result: dict) -> np.ndarray:
    for raw_contour in dark_spot_result.get("contours", []):
        pts = np.array(raw_contour, dtype=np.int32)
        cv2.drawContours(img, [pts], -1, (255, 140, 0), 2)
    return img


def _generate_heatmap(img_bgr: np.ndarray, lesion_result: dict) -> np.ndarray:
    """
    KDE-based lesion density heatmap.
    Creates a Gaussian-blended heat signature from lesion centroids.
    """
    h, w = img_bgr.shape[:2]
    heat = np.zeros((h, w), dtype=np.float32)

    detections = lesion_result.get("detections", [])
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        # Gaussian splat around centroid
        sigma = max(w, h) * 0.06
        size = int(sigma * 4)
        gx = np.clip(np.arange(w) - cx, -size, size)
        gy = np.clip(np.arange(h) - cy, -size, size)
        gx2d, gy2d = np.meshgrid(gx, gy)
        heat += np.exp(-(gx2d ** 2 + gy2d ** 2) / (2 * sigma ** 2))

    if heat.max() > 0:
        heat = (heat / heat.max() * 255).astype(np.uint8)
    else:
        heat = np.zeros((h, w), dtype=np.uint8)

    heat_color = cv2.applyColorMap(heat, cv2.COLORMAP_JET)
    # Blend with original at ~40% opacity
    heat_color = cv2.addWeighted(heat_color, 0.45, img_bgr, 0.55, 0)
    return heat_color


def composite_overlays(
    img_bgr: np.ndarray,
    lesion_result: dict,
    zone_result: dict,
    dark_spot_result: dict,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Produces:
    - annotated_img: zones + lesion boxes + dark spot contours
    - heatmap_img: KDE density heatmap
    """
    annotated = img_bgr.copy()
    annotated = _draw_zone_overlays(annotated, zone_result)
    annotated = _draw_dark_spot_contours(annotated, dark_spot_result)
    annotated = _draw_lesion_boxes(annotated, lesion_result)

    heatmap = _generate_heatmap(img_bgr, lesion_result)

    return annotated, heatmap
