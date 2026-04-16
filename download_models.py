#!/usr/bin/env python3
"""
DermLens Model Setup Script
============================
Downloads/prepares YOLO and EfficientNet weights.

Usage:
    python download_models.py [--yolo-weights PATH] [--effnet-weights PATH]

Options:
    --yolo-weights    Path to custom fine-tuned YOLOv8 .pt file
                      If not provided, downloads yolov8n.pt as baseline.
    --effnet-weights  Path to fine-tuned EfficientNet-B3 .pt file
                      If not provided, model will run in heuristic mode.

To fine-tune YOLOv8 on Roboflow acne dataset:
    1. Sign up at https://universe.roboflow.com/search?q=class:acne
    2. Export dataset in YOLOv8 format
    3. Run:  yolo train model=yolov8m.pt data=dataset.yaml epochs=50 imgsz=640
    4. Copy best.pt to backend/models/yolov8_acne.pt

To fine-tune EfficientNet-B3 on ACNE04:
    1. Download ACNE04 from https://github.com/xpwu95/LDL
    2. Run: python train_efficientnet.py
    3. Copy best checkpoint to backend/models/efficientnet_acne.pt
"""

import os
import sys
import argparse
import shutil

MODELS_DIR = os.path.join(os.path.dirname(__file__), "backend", "models")


def ensure_dir():
    os.makedirs(MODELS_DIR, exist_ok=True)
    print(f"✓ Models directory: {MODELS_DIR}")


def download_yolo_baseline():
    """Downloads yolov8n.pt as a baseline (not fine-tuned on acne)."""
    try:
        from ultralytics import YOLO
        print("⬇  Downloading YOLOv8n baseline weights...")
        model = YOLO("yolov8n.pt")
        print("✓ YOLOv8n ready. For acne-specific results, fine-tune on Roboflow dataset.")
        return True
    except ImportError:
        print("⚠  ultralytics not installed. Run: pip install ultralytics")
        return False


def copy_custom_weights(src, dest_name):
    dest = os.path.join(MODELS_DIR, dest_name)
    if os.path.exists(src):
        shutil.copy2(src, dest)
        print(f"✓ Copied {src} → {dest}")
        return True
    else:
        print(f"✗ File not found: {src}")
        return False


def main():
    parser = argparse.ArgumentParser(description="DermLens model setup")
    parser.add_argument("--yolo-weights",   default=None, help="Path to fine-tuned YOLOv8 .pt")
    parser.add_argument("--effnet-weights", default=None, help="Path to fine-tuned EfficientNet-B3 .pt")
    args = parser.parse_args()

    ensure_dir()

    print("\n── YOLOv8 Setup ──────────────────────────────────────────")
    if args.yolo_weights:
        copy_custom_weights(args.yolo_weights, "yolov8_acne.pt")
    else:
        download_yolo_baseline()

    print("\n── EfficientNet-B3 Setup ─────────────────────────────────")
    if args.effnet_weights:
        copy_custom_weights(args.effnet_weights, "efficientnet_acne.pt")
    else:
        print("ℹ  No EfficientNet weights provided.")
        print("   Severity grading will use OpenCV heuristic fallback.")
        print("   To train: see train_efficientnet.py for full training script.")

    print("\n✅ Setup complete. Run: docker compose up --build\n")


if __name__ == "__main__":
    main()
