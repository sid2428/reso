import React from "react";
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from "recharts";

const STATUS_STYLE = {
  Clear:    "text-green-400 bg-green-950/40 border-green-800/40",
  Mild:     "text-yellow-400 bg-yellow-950/40 border-yellow-800/40",
  Affected: "text-red-400 bg-red-950/40 border-red-800/40",
};

const ZONE_ORDER = ["forehead", "left_cheek", "right_cheek", "nose", "chin", "jawline"];

export default function ZoneBreakdown({ zones }) {
  if (!zones) return null;

  const radarData = ZONE_ORDER.map((key) => ({
    zone: zones[key]?.label?.replace(" ", "\n") || key,
    lesions: zones[key]?.lesion_count || 0,
  }));

  return (
    <div className="rounded-2xl border border-slate-700/50 bg-slate-800/40 p-5 flex flex-col gap-4">
      <h3 className="text-slate-300 font-semibold">Facial Zone Analysis</h3>

      {/* Radar chart */}
      <ResponsiveContainer width="100%" height={200}>
        <RadarChart data={radarData}>
          <PolarGrid stroke="#334155" />
          <PolarAngleAxis dataKey="zone" tick={{ fill: "#94a3b8", fontSize: 10 }} />
          <Radar
            name="Lesions"
            dataKey="lesions"
            stroke="#a855f7"
            fill="#a855f7"
            fillOpacity={0.3}
          />
          <Tooltip
            contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
            labelStyle={{ color: "#e2e8f0" }}
          />
        </RadarChart>
      </ResponsiveContainer>

      {/* Zone cards grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {ZONE_ORDER.map((key) => {
          const zone = zones[key];
          if (!zone) return null;
          const style = STATUS_STYLE[zone.status] || STATUS_STYLE["Mild"];
          return (
            <div key={key} className={`rounded-xl border p-3 flex flex-col gap-1 ${style}`}>
              <span className="text-xs font-semibold">{zone.label}</span>
              <div className="flex items-center justify-between">
                <span className="text-lg font-bold">{zone.lesion_count}</span>
                <span className="text-xs opacity-75 font-medium">{zone.status}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
