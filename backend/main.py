"""
DermLens — AI-Powered Skin Health Analysis Platform
FastAPI Backend — Main Entry Point
"""

import os
import uuid
import base64
import logging
from io import BytesIO
from typing import Optional

import cv2
import numpy as np
from PIL import Image
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from modules.preprocessing import preprocess_image, validate_image_quality
from modules.severity import grade_severity
from modules.lesion_detection import detect_lesions
from modules.zone_mapping import map_facial_zones
from modules.dark_spots import detect_dark_spots
from modules.overlay import composite_overlays
from modules.fitzpatrick import classify_skin_tone
from modules.report_generator import generate_skincare_routine
from modules.progress_tracker import save_scan, get_history

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DermLens API",
    description="AI-Powered Skin Health Analysis Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisResponse(BaseModel):
    scan_id: str
    severity: dict
    lesions: dict
    zones: dict
    dark_spots: dict
    fitzpatrick: dict
    annotated_image: str   # base64 PNG
    heatmap_image: str     # base64 PNG
    routine: dict
    disclaimer: str


@app.get("/")
def root():
    return {"status": "ok", "service": "DermLens API v1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_skin(file: UploadFile = File(...)):
    """
    Main analysis endpoint.
    Accepts a face image and returns a comprehensive skin health report.
    """
    # ── Read uploaded image ────────────────────────────────────────────────
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, or WebP images are accepted.")

    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if img_bgr is None:
        raise HTTPException(status_code=400, detail="Could not decode image. Please try a different file.")

    # ── Preprocessing & validation ─────────────────────────────────────────
    validation = validate_image_quality(img_bgr)
    if not validation["passed"]:
        raise HTTPException(status_code=422, detail=validation["message"])

    img_bgr, face_box = preprocess_image(img_bgr)

    # ── Run all analysis modules in sequence ───────────────────────────────
    logger.info("Starting analysis pipeline...")

    fitzpatrick_result = classify_skin_tone(img_bgr)
    severity_result    = grade_severity(img_bgr)
    lesion_result      = detect_lesions(img_bgr)
    zone_result        = map_facial_zones(img_bgr)
    dark_spot_result   = detect_dark_spots(img_bgr, fitzpatrick_result["type"])

    # ── Composite overlays ─────────────────────────────────────────────────
    annotated_img, heatmap_img = composite_overlays(
        img_bgr, lesion_result, zone_result, dark_spot_result
    )

    # ── Build analysis JSON for LLM ────────────────────────────────────────
    analysis_summary = {
        "severity": severity_result,
        "lesions": lesion_result,
        "zones": zone_result,
        "dark_spots": dark_spot_result,
        "fitzpatrick": fitzpatrick_result,
    }

    routine = await generate_skincare_routine(analysis_summary)

    # ── Encode images to base64 ────────────────────────────────────────────
    def encode_img(arr):
        _, buf = cv2.imencode(".png", arr)
        return base64.b64encode(buf).decode("utf-8")

    scan_id = str(uuid.uuid4())[:8]
    save_scan(scan_id, analysis_summary)

    return AnalysisResponse(
        scan_id=scan_id,
        severity=severity_result,
        lesions=lesion_result,
        zones=zone_result,
        dark_spots=dark_spot_result,
        fitzpatrick=fitzpatrick_result,
        annotated_image=encode_img(annotated_img),
        heatmap_image=encode_img(heatmap_img),
        routine=routine,
        disclaimer=(
            "DermLens is a skin health awareness tool, not a medical device. "
            "It does not diagnose, treat, or prevent any disease. "
            "Consult a qualified dermatologist for persistent or severe conditions."
        ),
    )


@app.get("/history")
def get_scan_history():
    """Return stored scan history for progress tracking."""
    return get_history()
