import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const TYPE_CONFIG = {
  comedonal:    { label: "Comedonal",     color: "#22c55e", emoji: "🟢", desc: "Blackheads & whiteheads" },
  inflammatory: { label: "Inflammatory",  color: "#ef4444", emoji: "🔴", desc: "Papules & pustules" },
  nodular:      { label: "Nodular/Cystic",color: "#3b82f6", emoji: "🔵", desc: "Deep cystic lesions" },
};

export default function LesionStats({ lesions }) {
  if (!lesions) return null;

  const chartData = Object.entries(lesions.counts || {}).map(([key, val]) => ({
    name: TYPE_CONFIG[key]?.label || key,
    count: val,
    color: TYPE_CONFIG[key]?.color || "#6b7280",
    key,
  }));

  return (
    <div className="rounded-2xl border border-slate-700/50 bg-slate-800/40 p-5 flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h3 className="text-slate-300 font-semibold">Lesion Detection</h3>
        <span className="text-2xl font-bold text-white">{lesions.total}
          <span className="text-slate-500 text-sm font-normal ml-1">({lesions.bucket})</span>
        </span>
      </div>

      {/* Bar chart */}
      <ResponsiveContainer width="100%" height={100}>
        <BarChart data={chartData} barSize={32}>
          <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis hide />
          <Tooltip
            contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
            labelStyle={{ color: "#e2e8f0" }}
            itemStyle={{ color: "#94a3b8" }}
          />
          <Bar dataKey="count" radius={[6, 6, 0, 0]}>
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Type breakdown cards */}
      <div className="grid grid-cols-3 gap-2">
        {Object.entries(lesions.counts || {}).map(([key, val]) => {
          const cfg = TYPE_CONFIG[key] || {};
          return (
            <div key={key} className="flex flex-col items-center gap-1 bg-slate-900/60 rounded-xl p-2">
              <span className="text-lg">{cfg.emoji}</span>
              <span className="text-lg font-bold text-white">{val}</span>
              <span className="text-slate-500 text-xs text-center">{cfg.desc}</span>
            </div>
          );
        })}
      </div>

      <p className="text-slate-600 text-xs">Source: {lesions.source}</p>
    </div>
  );
}
