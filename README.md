# 🔬 DermLens — AI-Powered Skin Health Analysis Platform

> Upload a selfie. Get a dermatologist-grade visual skin health report in under 10 seconds.

![Stack](https://img.shields.io/badge/Stack-React%20%7C%20FastAPI%20%7C%20YOLOv8%20%7C%20EfficientNet--B3-6d28d9)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend (Port 3000)            │
│  UploadZone → AnnotatedViewer → Report Tabs → Tracker   │
└──────────────────────┬──────────────────────────────────┘
                       │  REST API (multipart/form-data)
┌──────────────────────▼──────────────────────────────────┐
│                  FastAPI Backend (Port 8000)             │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │ Module 1 │  │ Module 2 │  │ Module 3 │  │  M4    │  │
│  │Severity  │  │ YOLOv8   │  │MediaPipe │  │Dark    │  │
│  │EffNet-B3 │  │ Lesions  │  │Zone Map  │  │Spots   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘  │
│       └─────────────┴─────────────┴─────────────┘       │
│                          │                              │
│              ┌───────────▼──────────┐                   │
│              │  Overlay Compositor  │                   │
│              │  + Heatmap Generator │                   │
│              └───────────┬──────────┘                   │
│                          │                              │
│              ┌───────────▼──────────┐                   │
│              │   Claude API (LLM)   │                   │
│              │  Skincare Routine    │                   │
│              └───────────┬──────────┘                   │
│                          │                              │
│              ┌───────────▼──────────┐                   │
│              │   SQLite Progress DB │                   │
│              └──────────────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Option A — Docker (Recommended)

```bash
# 1. Clone and enter directory
cd dermlens-mvp

# 2. Set your Anthropic API key (optional — fallback routine works without it)
export ANTHROPIC_API_KEY=your_key_here

# 3. Run everything
docker compose up --build

# Frontend → http://localhost:3000
# Backend API → http://localhost:8000
# API Docs → http://localhost:8000/docs
```

### Option B — Local Development

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
```

---

## 🤖 AI Models

### Module 1 — Severity Grading (EfficientNet-B3)

| Mode | How to activate |
|------|----------------|
| **Heuristic (default)** | Works out of the box using OpenCV redness analysis |
| **Full ML** | Train on ACNE04 dataset → `python train_efficientnet.py --data-dir ./ACNE04` |

### Module 2 — Lesion Detection (YOLOv8)

| Mode | How to activate |
|------|----------------|
| **CV Fallback (default)** | Contour + color detection, no GPU needed |
| **YOLOv8 baseline** | `python download_models.py` (downloads yolov8n.pt) |
| **Fine-tuned (best)** | Train on Roboflow acne dataset → copy `best.pt` to `backend/models/yolov8_acne.pt` |

**Fine-tuning YOLOv8 on Roboflow:**
```bash
# 1. Get dataset from: https://universe.roboflow.com/search?q=class:acne
# 2. Export in YOLOv8 format
# 3. Train:
yolo train model=yolov8m.pt data=dataset.yaml epochs=50 imgsz=640
# 4. Copy best weights:
cp runs/detect/train/weights/best.pt backend/models/yolov8_acne.pt
```

### Module 3 — Zone Mapping (MediaPipe)

Auto-installed with requirements. Uses 468 facial landmarks to segment into:
Forehead · Left Cheek · Right Cheek · Nose · Chin · Jawline

### Module 4 — Dark Spots (OpenCV LAB)

No model needed. Uses LAB color space with Fitzpatrick-aware adaptive thresholding.

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Optional | Claude API key for personalized routine generation. Falls back to static routine if not set. |

---

## 📁 Project Structure

```
dermlens-mvp/
├── backend/
│   ├── main.py                    # FastAPI app & /analyze endpoint
│   ├── modules/
│   │   ├── preprocessing.py       # Face detection, quality validation
│   │   ├── severity.py            # EfficientNet-B3 severity grading
│   │   ├── lesion_detection.py    # YOLOv8 lesion detection
│   │   ├── zone_mapping.py        # MediaPipe facial zone segmentation
│   │   ├── dark_spots.py          # LAB dark spot detection
│   │   ├── overlay.py             # Image compositor + heatmap
│   │   ├── fitzpatrick.py         # Skin tone classification
│   │   ├── report_generator.py    # Claude API routine generator
│   │   └── progress_tracker.py    # SQLite scan history
│   ├── models/                    # Place .pt weight files here
│   ├── data/                      # SQLite database auto-created here
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Root component
│   │   ├── store/useStore.js      # Zustand global state
│   │   ├── api.js                 # Axios API client
│   │   └── components/
│   │       ├── UploadZone.jsx     # Drag-and-drop uploader
│   │       ├── AnnotatedImageViewer.jsx  # Annotated/heatmap/original toggle
│   │       ├── SeverityGauge.jsx  # IGA radial gauge
│   │       ├── LesionStats.jsx    # Lesion bar chart + type breakdown
│   │       ├── ZoneBreakdown.jsx  # Radar chart + zone cards
│   │       ├── DarkSpotCard.jsx   # Coverage bar + Fitzpatrick badge
│   │       ├── SkincareRoutine.jsx # AM/PM routine tabs
│   │       ├── ProgressTracker.jsx # History line charts + table
│   │       └── AnalysisReport.jsx  # Tabbed report container
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── download_models.py             # Model weight setup helper
├── train_efficientnet.py          # EfficientNet-B3 training script
└── README.md
```

---

## 🎯 Features

| Feature | Status | Module |
|---------|--------|--------|
| Face detection & quality validation | ✅ | MediaPipe / Haar |
| IGA severity grading (Clear/Mild/Moderate/Severe) | ✅ | EfficientNet-B3 / Heuristic |
| Lesion detection with type classification | ✅ | YOLOv8 / CV fallback |
| Color-coded bounding boxes | ✅ | OpenCV overlay |
| Facial zone mapping (6 zones) | ✅ | MediaPipe 468-pt mesh |
| Fitzpatrick skin tone classification | ✅ | HSV analysis |
| Dark spot detection (Fitzpatrick-aware) | ✅ | LAB adaptive threshold |
| Lesion density heatmap | ✅ | KDE + COLORMAP_JET |
| Personalized AM/PM skincare routine | ✅ | Claude API / static fallback |
| Progress tracking & trend charts | ✅ | SQLite + Recharts |
| Annotated image viewer (3 modes) | ✅ | Base64 PNG |
| Drag-and-drop upload with validation | ✅ | React Dropzone |
| Docker one-command deployment | ✅ | docker-compose |

---

## 🗺️ Roadmap (Post-MVP)

- [ ] PDF report export (ReportLab)
- [ ] Product ingredient cross-check
- [ ] Camera capture (PWA)
- [ ] Multilingual reports (Hindi, Marathi, Tamil)
- [ ] Multi-condition support (eczema, rosacea, psoriasis)
- [ ] On-device inference (ONNX / TFLite)

---

## ⚕️ Disclaimer

DermLens is a **skin health awareness tool**, not a medical device. It does not diagnose, treat, or prevent any disease. Users experiencing persistent or severe skin conditions should consult a qualified dermatologist. All AI-generated recommendations are for informational purposes only.

---

## 📚 Resources

| Resource | Link |
|----------|------|
| MediaPipe Face Mesh | https://github.com/google-ai-edge/mediapipe |
| Ultralytics YOLOv8 | https://github.com/ultralytics/ultralytics |
| ACNE04 Dataset | https://github.com/xpwu95/LDL |
| Roboflow Acne Models | https://universe.roboflow.com/search?q=class:acne |
| Claude API Docs | https://docs.anthropic.com |
| PyTorch Image Models | https://github.com/huggingface/pytorch-image-models |
