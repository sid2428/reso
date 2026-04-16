# DermLens Model Weights

Place your fine-tuned model weights here:

| File | Purpose | How to obtain |
|------|---------|---------------|
| `yolov8_acne.pt` | YOLOv8 acne lesion detector | Fine-tune YOLOv8m on Roboflow acne dataset (see README) |
| `efficientnet_acne.pt` | EfficientNet-B3 severity grader | Run `python train_efficientnet.py --data-dir ./ACNE04` |

## Without model weights
The app runs fully without these files using:
- **Severity**: OpenCV redness heuristic (reasonable for demo)
- **Lesion detection**: Contour + color blob detection (lighter but less accurate)

## Quick YOLO setup
```bash
pip install ultralytics
yolo train model=yolov8m.pt data=your_acne_dataset.yaml epochs=50 imgsz=640
cp runs/detect/train/weights/best.pt yolov8_acne.pt
```
