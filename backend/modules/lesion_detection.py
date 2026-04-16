"""
Module 2: Lesion Detection
- YOLOv8m fine-tuned on Roboflow acne dataset
- Detects and classifies: Comedonal, Inflammatory, Nodular/Cystic
- Falls back to OpenCV contour detection if YOLO not available
"""

import os
import cv2
import numpy as np
from typing import List

# Class definitions matching YOLO training labels
LESION_CLASSES = {
    0: {"name": "comedonal",    "label": "Comedonal",     "color": (0, 200, 0),   "hex": "#22c55e"},
    1: {"name": "inflammatory", "label": "Inflammatory",  "color": (0, 0, 220),   "hex": "#ef4444"},
    2: {"name": "nodular",      "label": "Nodular/Cystic","color": (200, 0, 0),   "hex": "#3b82f6"},
}

YOLO_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/yolov8_acne.pt")

_yolo_model = None


def _load_yolo():
    global _yolo_model
    if _yolo_model is not None:
        return _yolo_model
    try:
        from ultralytics import YOLO
        if os.path.exists(YOLO_MODEL_PATH):
            _yolo_model = YOLO(YOLO_MODEL_PATH)
            return _yolo_model
        else:
            # Try pre-trained nano as baseline — user must fine-tune for production
            _yolo_model = YOLO("yolov8n.pt")
            return _yolo_model
    except Exception:
        return None


def _bucket(count: int) -> str:
    if count == 0:     return "0"
    elif count <= 2:   return "1–2"
    elif count <= 5:   return "3–5"
    elif count <= 10:  return "6–10"
    else:              return "11+"


def _cv_fallback_detection(img_bgr: np.ndarray) -> List[dict]:
    """
    Contour-based lesion detection as fallback.
    Looks for reddish, circular blobs — approximates papules/pustules.
    """
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    # Red range mask (inflammatory lesions)
    m1 = cv2.inRange(hsv, np.array([0, 60, 60]), np.array([10, 255, 255]))
    m2 = cv2.inRange(hsv, np.array([160, 60, 60]), np.array([180, 255, 255]))
    mask = cv2.bitwise_or(m1, m2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detections = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < 30 or area > 3000:
            continue
        x, y, w, h = cv2.boundingRect(c)
        # Aspect ratio filter (roughly round)
        if max(w, h) / (min(w, h) + 1e-5) > 3:
            continue
        detections.append({
            "class": 1,
            "class_name": "inflammatory",
            "confidence": 0.55,
            "bbox": [x, y, x + w, y + h],
        })

    # Also detect dark comedones (dark small spots)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    _, dark_mask = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
    dark_contours, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in dark_contours:
        area = cv2.contourArea(c)
        if area < 15 or area > 300:
            continue
        x, y, w, h = cv2.boundingRect(c)
        if max(w, h) / (min(w, h) + 1e-5) > 2.5:
            continue
        detections.append({
            "class": 0,
            "class_name": "comedonal",
            "confidence": 0.50,
            "bbox": [x, y, x + w, y + h],
        })

    return detections


def detect_lesions(img_bgr: np.ndarray) -> dict:
    """
    Main lesion detection function.
    Returns structured result with counts and bounding boxes.
    """
    model = _load_yolo()
    detections = []

    if model is not None:
        try:
            results = model(img_bgr, verbose=False, conf=0.35, iou=0.45)
            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    class_name = LESION_CLASSES.get(cls, {"name": "unknown"})["name"]
                    detections.append({
                        "class": cls,
                        "class_name": class_name,
                        "confidence": round(conf, 2),
                        "bbox": [x1, y1, x2, y2],
                    })
        except Exception:
            detections = _cv_fallback_detection(img_bgr)
    else:
        detections = _cv_fallback_detection(img_bgr)

    # ── Aggregate counts ───────────────────────────────────────────────────
    counts = {"comedonal": 0, "inflammatory": 0, "nodular": 0}
    for d in detections:
        name = d["class_name"]
        if "comedonal" in name:
            counts["comedonal"] += 1
        elif "inflammatory" in name:
            counts["inflammatory"] += 1
        elif "nodular" in name or "cystic" in name:
            counts["nodular"] += 1

    total = sum(counts.values())

    return {
        "total": total,
        "bucket": _bucket(total),
        "counts": counts,
        "detections": detections,
        "source": "yolov8" if (model and len(detections) > 0) else "cv_fallback",
    }
