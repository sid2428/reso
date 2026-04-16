import React from "react";

const SEV_STYLE = {
  None:        { bar: "w-0",    color: "bg-green-500",  text: "text-green-400"  },
  Mild:        { bar: "w-1/4",  color: "bg-yellow-500", text: "text-yellow-400" },
  Moderate:    { bar: "w-1/2",  color: "bg-orange-500", text: "text-orange-400" },
  Significant: { bar: "w-3/4",  color: "bg-red-500",    text: "text-red-400"    },
};

export default function DarkSpotCard({ darkSpots, fitzpatrick }) {
  if (!darkSpots) return null;
  const sev = SEV_STYLE[darkSpots.severity] || SEV_STYLE["Mild"];

  return (
    <div className="rounded-2xl border border-slate-700/50 bg-slate-800/40 p-5 flex flex-col gap-4">
      <h3 className="text-slate-300 font-semibold">Dark Spot Analysis</h3>

      {/* Coverage bar */}
      <div className="flex flex-col gap-2">
        <div className="flex justify-between text-sm">
          <span className="text-slate-400">Skin Coverage</span>
          <span className={`font-bold ${sev.text}`}>{darkSpots.coverage_percent}%</span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-700 ${sev.color}`}
            style={{ width: `${Math.min(100, darkSpots.coverage_percent * 5)}%` }}
          />
        </div>
        <span className={`text-xs font-semibold ${sev.text}`}>{darkSpots.severity}</span>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-2">
        <Stat label="Spots Detected" value={darkSpots.count} />
        <Stat label="LAB Threshold" value={darkSpots.threshold_used} unit="L" />
        <Stat label="Skin Baseline L" value={darkSpots.skin_baseline_L} />
      </div>

      {/* Fitzpatrick badge */}
      {fitzpatrick && (
        <div className="flex items-center gap-3 bg-slate-900/50 rounded-xl p-3">
          <div
            className="w-8 h-8 rounded-full ring-2 ring-slate-600 flex-shrink-0"
            style={{ background: fitzpatrick.hex }}
          />
          <div>
            <p className="text-slate-300 text-sm font-medium">{fitzpatrick.label}</p>
            <p className="text-slate-500 text-xs">{fitzpatrick.description}</p>
          </div>
        </div>
      )}

      <p className="text-slate-600 text-xs">
        ✦ Fitzpatrick-aware thresholding prevents over-detection on darker skin tones.
      </p>
    </div>
  );
}

function Stat({ label, value, unit }) {
  return (
    <div className="bg-slate-900/60 rounded-xl p-3 text-center">
      <p className="text-lg font-bold text-white">{value}{unit ? <span className="text-xs text-slate-500 ml-0.5">{unit}</span> : ""}</p>
      <p className="text-slate-500 text-xs mt-0.5">{label}</p>
    </div>
  );
}
