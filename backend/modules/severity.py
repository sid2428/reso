"""
Module 1: Severity Grading
- EfficientNet-B3 fine-tuned on ACNE04 dataset
- Returns IGA scale: Clear / Mild / Moderate / Severe
- Falls back to heuristic CV analysis if model not loaded
"""

import os
import cv2
import numpy as np


# Model weights path (populated after training / download)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/efficientnet_acne.pt")

IGA_LABELS = ["Clear", "Mild", "Moderate", "Severe"]
IGA_COLORS = ["#22c55e", "#eab308", "#f97316", "#ef4444"]

_model = None


def _load_model():
    global _model
    if _model is not None:
        return _model
    try:
        import torch
        import timm

        model = timm.create_model("efficientnet_b3", pretrained=False, num_classes=4)
        if os.path.exists(MODEL_PATH):
            state = torch.load(MODEL_PATH, map_location="cpu")
            model.load_state_dict(state)
            model.eval()
            _model = model
            return model
    except Exception as e:
        pass
    return None


def _heuristic_severity(img_bgr: np.ndarray) -> dict:
    """
    CV-based fallback when model weights are not available.
    Uses skin-colored region analysis + redness detection.
    """
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    # Detect reddish/inflamed areas
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 50, 50])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    red_ratio = np.sum(red_mask > 0) / (img_bgr.shape[0] * img_bgr.shape[1])

    # Approximate severity from red pixel ratio
    if red_ratio < 0.01:
        idx, conf = 0, 0.85
    elif red_ratio < 0.04:
        idx, conf = 1, 0.78
    elif red_ratio < 0.10:
        idx, conf = 2, 0.72
    else:
        idx, conf = 3, 0.68

    return {
        "label": IGA_LABELS[idx],
        "index": idx,
        "confidence": round(conf, 2),
        "color": IGA_COLORS[idx],
        "source": "heuristic",
        "description": _iga_description(idx),
    }


def _iga_description(idx: int) -> str:
    descs = [
        "No visible lesions. Skin appears clear.",
        "Fewer than 20 comedones or fewer than 15 inflammatory lesions.",
        "20–100 comedones, 15–50 inflammatory lesions, or both.",
        "More than 100 comedones or more than 50 inflammatory lesions. Cysts may be present.",
    ]
    return descs[idx]


def grade_severity(img_bgr: np.ndarray) -> dict:
    """
    Main severity grading function.
    Tries EfficientNet-B3 first, falls back to heuristic.
    """
    model = _load_model()

    if model is not None:
        try:
            import torch
            from torchvision import transforms

            transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((300, 300)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ])

            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            tensor = transform(img_rgb).unsqueeze(0)

            with torch.no_grad():
                logits = model(tensor)
                probs = torch.softmax(logits, dim=1)[0]
                idx = int(probs.argmax())
                conf = float(probs[idx])

            return {
                "label": IGA_LABELS[idx],
                "index": idx,
                "confidence": round(conf, 2),
                "color": IGA_COLORS[idx],
                "source": "efficientnet_b3",
                "description": _iga_description(idx),
            }
        except Exception:
            pass

    return _heuristic_severity(img_bgr)
