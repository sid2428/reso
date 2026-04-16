import React from "react";
import { Toaster } from "react-hot-toast";
import useStore from "./store/useStore";
import UploadZone from "./components/UploadZone";
import AnalysisReport from "./components/AnalysisReport";
import { Microscope } from "lucide-react";

export default function App() {
  const { analysisResult, isAnalyzing } = useStore();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Toaster
        position="top-center"
        toastOptions={{
          style: { background: "#1e293b", color: "#e2e8f0", border: "1px solid #334155" },
        }}
      />

      {/* ── Nav ─────────────────────────────────────────────────── */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-20">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-gradient-to-br from-violet-600 to-fuchsia-600 rounded-lg">
              <Microscope size={18} className="text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight">DermLens</span>
            <span className="text-xs text-slate-500 hidden sm:block">AI Skin Health Analysis</span>
          </div>
          <span className="text-xs text-slate-600 bg-slate-800 px-2 py-1 rounded-full">MVP v1.0</span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-10">
        {!analysisResult && !isAnalyzing && (
          <>
            {/* Hero */}
            <div className="text-center mb-10">
              <div className="inline-flex items-center gap-2 text-xs text-violet-400 bg-violet-950/50 border border-violet-800/40 px-3 py-1 rounded-full mb-4">
                🤖 YOLOv8 + EfficientNet-B3 + Claude AI
              </div>
              <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-3">
                Know your skin,{" "}
                <span className="bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
                  instantly.
                </span>
              </h1>
              <p className="text-slate-400 max-w-lg mx-auto text-base">
                Upload a selfie. Get a dermatologist-grade visual skin health report in under 10 seconds — no appointments, no cost.
              </p>
            </div>

            <UploadZone />

            {/* How it works */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-12">
              {[
                { icon: "📸", title: "Upload", desc: "Selfie in natural light" },
                { icon: "🔬", title: "Analyze", desc: "4 AI modules run in parallel" },
                { icon: "🗺️", title: "Map",     desc: "Zone-by-zone breakdown" },
                { icon: "💊", title: "Routine", desc: "Personalized skincare plan" },
              ].map((item) => (
                <div key={item.title} className="flex flex-col items-center gap-2 bg-slate-800/40 rounded-2xl p-4 border border-slate-700/40 text-center">
                  <span className="text-2xl">{item.icon}</span>
                  <span className="text-slate-200 font-semibold text-sm">{item.title}</span>
                  <span className="text-slate-500 text-xs">{item.desc}</span>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Loading state */}
        {isAnalyzing && (
          <div className="flex flex-col items-center justify-center py-24 gap-5">
            <div className="relative w-20 h-20">
              <div className="absolute inset-0 rounded-full border-4 border-violet-600 border-t-transparent animate-spin" />
              <div className="absolute inset-3 rounded-full border-4 border-fuchsia-600 border-b-transparent animate-spin animation-delay-150" />
            </div>
            <div className="text-center">
              <p className="text-slate-300 font-semibold">Analyzing your skin…</p>
              <p className="text-slate-500 text-sm">Running 4 AI modules in parallel</p>
            </div>
            <div className="flex flex-col gap-1 text-xs text-slate-600">
              {["Detecting face & validating quality", "Running YOLOv8 lesion detection", "Mapping facial zones with MediaPipe", "Generating personalized routine with Claude"].map((s, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-violet-600 animate-pulse" style={{ animationDelay: `${i * 200}ms` }} />
                  {s}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results */}
        {analysisResult && <AnalysisReport />}
      </main>

      <footer className="border-t border-slate-800 mt-16 py-6 text-center text-slate-700 text-xs">
        DermLens · AI Skin Health Awareness Tool · Not a medical device · {new Date().getFullYear()}
      </footer>
    </div>
  );
}
