import React from "react";
import useStore from "../store/useStore";
import SeverityGauge from "./SeverityGauge";
import LesionStats from "./LesionStats";
import ZoneBreakdown from "./ZoneBreakdown";
import DarkSpotCard from "./DarkSpotCard";
import SkincareRoutine from "./SkincareRoutine";
import ProgressTracker from "./ProgressTracker";
import AnnotatedImageViewer from "./AnnotatedImageViewer";
import { RefreshCw, FileText } from "lucide-react";

const TABS = [
  { key: "overview",  label: "Overview"  },
  { key: "zones",     label: "Zones"     },
  { key: "routine",   label: "Routine"   },
  { key: "progress",  label: "Progress"  },
];

export default function AnalysisReport() {
  const { analysisResult: r, activeTab, setActiveTab, reset } = useStore();
  if (!r) return null;

  return (
    <div className="flex flex-col gap-6 w-full max-w-3xl mx-auto">
      {/* Header bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Your Skin Report</h2>
          <p className="text-slate-500 text-xs">Scan #{r.scan_id} · {new Date().toLocaleDateString()}</p>
        </div>
        <button
          onClick={reset}
          className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-700 text-slate-300 hover:bg-slate-600 transition text-sm"
        >
          <RefreshCw size={14} /> New Scan
        </button>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 bg-slate-800/60 rounded-xl p-1 border border-slate-700/50">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`flex-1 py-2 rounded-lg text-sm font-medium transition
              ${activeTab === t.key
                ? "bg-violet-600 text-white shadow"
                : "text-slate-400 hover:text-white"}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW TAB ───────────────────────────────────────── */}
      {activeTab === "overview" && (
        <div className="flex flex-col gap-5">
          <AnnotatedImageViewer result={r} />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <SeverityGauge severity={r.severity} />
            <LesionStats lesions={r.lesions} />
          </div>
          <DarkSpotCard darkSpots={r.dark_spots} fitzpatrick={r.fitzpatrick} />
        </div>
      )}

      {/* ── ZONES TAB ─────────────────────────────────────────── */}
      {activeTab === "zones" && (
        <div className="flex flex-col gap-5">
          <AnnotatedImageViewer result={r} />
          <ZoneBreakdown zones={r.zones} />
        </div>
      )}

      {/* ── ROUTINE TAB ───────────────────────────────────────── */}
      {activeTab === "routine" && (
        <SkincareRoutine routine={r.routine} />
      )}

      {/* ── PROGRESS TAB ──────────────────────────────────────── */}
      {activeTab === "progress" && (
        <ProgressTracker />
      )}

      {/* Disclaimer footer */}
      <div className="text-xs text-slate-600 text-center border-t border-slate-800 pt-4">
        ⚕️ {r.disclaimer}
      </div>
    </div>
  );
}
