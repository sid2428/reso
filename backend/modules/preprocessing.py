"""
Module: Preprocessing
- Face detection (MediaPipe BlazeFace)
- Image quality validation (blur, lighting, angle)
- Face crop & normalize
"""

import cv2
import numpy as np
from typing import Tuple, Optional

try:
    import mediapipe as mp
    _mp_face_detection = mp.solutions.face_detection
    _mp_face_mesh = mp.solutions.face_mesh
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False


def validate_image_quality(img_bgr: np.ndarray) -> dict:
    """
    Checks blur, lighting, and face presence.
    Returns {"passed": bool, "message": str}
    """
    h, w = img_bgr.shape[:2]

    # ── Resolution check ───────────────────────────────────────────────────
    if w < 256 or h < 256:
        return {"passed": False, "message": "Image is too small. Please upload a photo with at least 256×256 pixels."}

    # ── Blur check (Laplacian variance) ────────────────────────────────────
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < 50:
        return {"passed": False, "message": "Your photo is too blurry. Try holding your phone steady in good lighting."}

    # ── Lighting check ─────────────────────────────────────────────────────
    mean_brightness = np.mean(gray)
    if mean_brightness < 40:
        return {"passed": False, "message": "Your photo is too dark. Move to a well-lit area and try again."}
    if mean_brightness > 220:
        return {"passed": False, "message": "Your photo is overexposed. Avoid direct bright light or flash."}

    # ── Face presence (simple Haar fallback) ──────────────────────────────
    if MEDIAPIPE_AVAILABLE:
        with _mp_face_detection.FaceDetection(min_detection_confidence=0.5) as detector:
            rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb)
            if not results.detections:
                return {"passed": False, "message": "No face detected. Please upload a clear selfie facing the camera."}
    else:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) == 0:
            return {"passed": False, "message": "No face detected. Please upload a clear selfie facing the camera."}

    return {"passed": True, "message": "OK"}


def preprocess_image(img_bgr: np.ndarray) -> Tuple[np.ndarray, Optional[dict]]:
    """
    Detects face, crops with padding, resizes to 640×640.
    Returns (processed_img, face_box).
    """
    h, w = img_bgr.shape[:2]
    face_box = None

    if MEDIAPIPE_AVAILABLE:
        with _mp_face_detection.FaceDetection(min_detection_confidence=0.5) as detector:
            rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb)
            if results.detections:
                det = results.detections[0]
                bb = det.location_data.relative_bounding_box
                x = max(0, int(bb.xmin * w) - 30)
                y = max(0, int(bb.ymin * h) - 50)
                bw = min(w - x, int(bb.width * w) + 60)
                bh = min(h - y, int(bb.height * h) + 80)
                face_box = {"x": x, "y": y, "w": bw, "h": bh}
                img_bgr = img_bgr[y:y+bh, x:x+bw]
    else:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) > 0:
            x, y, fw, fh = faces[0]
            pad = 30
            x = max(0, x - pad)
            y = max(0, y - pad)
            fw = min(w - x, fw + 2 * pad)
            fh = min(h - y, fh + 2 * pad)
            face_box = {"x": x, "y": y, "w": fw, "h": fh}
            img_bgr = img_bgr[y:y+fh, x:x+fw]

    img_bgr = cv2.resize(img_bgr, (640, 640))
    return img_bgr, face_box
