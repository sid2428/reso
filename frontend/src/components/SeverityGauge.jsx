import React from "react";
import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from "recharts";

const IGA_CONFIG = {
  Clear:    { value: 10, color: "#22c55e", bg: "bg-green-950/40",  border: "border-green-500/40",  text: "text-green-400" },
  Mild:     { value: 40, color: "#eab308", bg: "bg-yellow-950/40", border: "border-yellow-500/40", text: "text-yellow-400" },
  Moderate: { value: 70, color: "#f97316", bg: "bg-orange-950/40", border: "border-orange-500/40", text: "text-orange-400" },
  Severe:   { value: 95, color: "#ef4444", bg: "bg-red-950/40",    border: "border-red-500/40",    text: "text-red-400" },
};

export default function SeverityGauge({ severity }) {
  if (!severity) return null;
  const cfg = IGA_CONFIG[severity.label] || IGA_CONFIG["Mild"];
  const data = [{ name: "severity", value: cfg.value }];

  return (
    <div className={`rounded-2xl border p-5 ${cfg.bg} ${cfg.border} flex flex-col items-center gap-2`}>
      <h3 className="text-slate-400 text-sm font-medium uppercase tracking-widest">IGA Severity</h3>

      <div className="relative w-40 h-40">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%" cy="50%"
            innerRadius="70%" outerRadius="100%"
            startAngle={210} endAngle={-30}
            data={data}
          >
            <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
            <RadialBar
              dataKey="value"
              cornerRadius={8}
              fill={cfg.color}
              background={{ fill: "#1e293b" }}
            />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center mt-4">
          <span className={`text-2xl font-bold ${cfg.text}`}>{severity.label}</span>
          <span className="text-slate-500 text-xs">{Math.round(severity.confidence * 100)}% conf.</span>
        </div>
      </div>

      <p className="text-slate-400 text-xs text-center max-w-xs">{severity.description}</p>

      {/* IGA scale legend */}
      <div className="flex gap-2 mt-1">
        {["Clear","Mild","Moderate","Severe"].map((l) => (
          <span key={l} className={`text-xs px-2 py-0.5 rounded-full font-medium
            ${l === severity.label ? `${IGA_CONFIG[l].text} ring-1 ring-current` : "text-slate-600"}`}>
            {l}
          </span>
        ))}
      </div>
    </div>
  );
}
