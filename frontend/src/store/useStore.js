import { create } from "zustand";

const useStore = create((set) => ({
  // ── Upload state ─────────────────────────────────────────
  uploadedFile: null,
  previewUrl: null,
  setUploadedFile: (file) => {
    const url = file ? URL.createObjectURL(file) : null;
    set({ uploadedFile: file, previewUrl: url });
  },

  // ── Analysis state ───────────────────────────────────────
  isAnalyzing: false,
  analysisResult: null,
  analysisError: null,
  setIsAnalyzing: (v) => set({ isAnalyzing: v }),
  setAnalysisResult: (r) => set({ analysisResult: r, analysisError: null }),
  setAnalysisError: (e) => set({ analysisError: e, isAnalyzing: false }),

  // ── History ──────────────────────────────────────────────
  history: [],
  setHistory: (h) => set({ history: h }),

  // ── Active tab ───────────────────────────────────────────
  activeTab: "overview",
  setActiveTab: (t) => set({ activeTab: t }),

  // ── View mode for annotated image ───────────────────────
  imageView: "annotated", // "annotated" | "heatmap" | "original"
  setImageView: (v) => set({ imageView: v }),

  // ── Reset ────────────────────────────────────────────────
  reset: () =>
    set({
      uploadedFile: null,
      previewUrl: null,
      analysisResult: null,
      analysisError: null,
      isAnalyzing: false,
      activeTab: "overview",
      imageView: "annotated",
    }),
}));

export default useStore;
