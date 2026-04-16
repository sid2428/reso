import React, { useEffect } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer,
} from "recharts";
import { TrendingDown, TrendingUp, Minus } from "lucide-react";
import useStore from "../store/useStore";
import { fetchHistory } from "../api";

const SEV_NUM = { Clear: 0, Mild: 1, Moderate: 2, Severe: 3 };

function Trend({ prev, curr, label, unit = "", lowerIsBetter = true }) {
  if (prev === undefined || curr === undefined) return null;
  const diff = curr - prev;
  const improved = lowerIsBetter ? diff < 0 : diff > 0;
  const neutral = diff === 0;
  return (
    <div className="flex flex-col items-center gap-1 bg-slate-900/60 rounded-xl p-3 text-center">
      <span className="text-slate-500 text-xs">{label}</span>
      <span className="text-white font-bold text-lg">{curr}{unit}</span>
      {neutral ? (
        <span className="text-slate-500 text-xs flex items-center gap-0.5"><Minus size={10} /> No change</span>
      ) : (
        <span className={`text-xs flex items-center gap-0.5 ${improved ? "text-green-400" : "text-red-400"}`}>
          {improved ? <TrendingDown size={10} /> : <TrendingUp size={10} />}
          {Math.abs(diff).toFixed(1)}{unit} {improved ? "better" : "worse"}
        </span>
      )}
    </div>
  );
}

export default function ProgressTracker() {
  const { history, setHistory } = useStore();

  useEffect(() => {
    fetchHistory().then(setHistory).catch(() => {});
  }, [setHistory]);

  if (!history || history.length < 2) {
    return (
      <div className="rounded-2xl border border-slate-700/50 bg-slate-800/40 p-8 text-center">
        <p className="text-slate-400 text-sm">Upload 2+ scans to see your progress over time.</p>
        <p className="text-slate-600 text-xs mt-1">Each analysis is saved automatically.</p>
      </div>
    );
  }

  const chartData = [...history].reverse().map((scan, i) => ({
    scan: `#${i + 1}`,
    Lesions: scan.lesion_total,
    "Dark Spots %": scan.dark_spot_percent,
    Severity: SEV_NUM[scan.severity] ?? 1,
    date: scan.timestamp?.slice(0, 10),
  }));

  const latest = history[0];
  const prev   = history[1];

  return (
    <div className="rounded-2xl border border-slate-700/50 bg-slate-800/40 p-5 flex flex-col gap-5">
      <h3 className="text-slate-300 font-semibold">Progress Tracking</h3>

      {/* Delta cards */}
      <div className="grid grid-cols-3 gap-2">
        <Trend prev={prev?.lesion_total} curr={latest?.lesion_total} label="Lesions" />
        <Trend prev={prev?.dark_spot_percent} curr={latest?.dark_spot_percent} label="Dark Spots" unit="%" />
        <Trend
          prev={SEV_NUM[prev?.severity]}
          curr={SEV_NUM[latest?.severity]}
          label="Severity"
        />
      </div>

      {/* Line chart */}
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <CartesianGrid stroke="#1e293b" />
          <XAxis dataKey="scan" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 8 }}
            labelStyle={{ color: "#e2e8f0" }}
            itemStyle={{ color: "#94a3b8" }}
          />
          <Legend wrapperStyle={{ color: "#94a3b8", fontSize: 11 }} />
          <Line type="monotone" dataKey="Lesions" stroke="#a855f7" strokeWidth={2} dot={{ r: 3, fill: "#a855f7" }} />
          <Line type="monotone" dataKey="Dark Spots %" stroke="#f97316" strokeWidth={2} dot={{ r: 3, fill: "#f97316" }} />
        </LineChart>
      </ResponsiveContainer>

      {/* History table */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs text-slate-400">
          <thead>
            <tr className="border-b border-slate-700">
              <th className="text-left py-1 pr-3">Date</th>
              <th className="text-left py-1 pr-3">Severity</th>
              <th className="text-right py-1 pr-3">Lesions</th>
              <th className="text-right py-1">Dark Spots %</th>
            </tr>
          </thead>
          <tbody>
            {history.map((scan) => (
              <tr key={scan.scan_id} className="border-b border-slate-800/60">
                <td className="py-1.5 pr-3">{scan.timestamp?.slice(0, 10)}</td>
                <td className="py-1.5 pr-3 font-medium text-slate-300">{scan.severity}</td>
                <td className="py-1.5 pr-3 text-right">{scan.lesion_total}</td>
                <td className="py-1.5 text-right">{scan.dark_spot_percent?.toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
