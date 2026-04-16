import React, { useState } from "react";
import { Sun, Moon, Sparkles, AlertTriangle, Leaf } from "lucide-react";

const STEP_COLORS = [
  "from-violet-600 to-fuchsia-600",
  "from-blue-600 to-cyan-600",
  "from-emerald-600 to-teal-600",
  "from-rose-600 to-pink-600",
  "from-amber-600 to-orange-600",
];

function RoutineStep({ step, index }) {
  return (
    <div className="flex gap-3 items-start">
      <div className={`min-w-[28px] h-7 rounded-full bg-gradient-to-br ${STEP_COLORS[index % STEP_COLORS.length]} flex items-center justify-center text-white text-xs font-bold flex-shrink-0`}>
        {step.step}
      </div>
      <div className="flex flex-col gap-0.5">
        <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">{step.action}</span>
        <span className="text-slate-200 text-sm font-medium">{step.ingredient}</span>
        <span className="text-slate-500 text-xs">{step.why}</span>
      </div>
    </div>
  );
}

export default function SkincareRoutine({ routine }) {
  const [tab, setTab] = useState("am");

  if (!routine) return null;

  const steps = tab === "am" ? routine.am_routine : routine.pm_routine;

  return (
    <div className="rounded-2xl border border-slate-700/50 bg-slate-800/40 p-5 flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <h3 className="text-slate-300 font-semibold flex items-center gap-2">
          <Sparkles size={16} className="text-violet-400" /> Personalized Routine
        </h3>
        <div className="flex rounded-xl overflow-hidden border border-slate-700">
          {["am", "pm"].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`flex items-center gap-1.5 px-4 py-1.5 text-sm font-medium transition
                ${tab === t ? "bg-violet-600 text-white" : "text-slate-400 hover:text-white"}`}
            >
              {t === "am" ? <Sun size={12} /> : <Moon size={12} />}
              {t.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Steps */}
      <div className="flex flex-col gap-4">
        {(steps || []).map((step, i) => (
          <RoutineStep key={i} step={step} index={i} />
        ))}
      </div>

      {/* Key Ingredients */}
      {routine.key_ingredients?.length > 0 && (
        <div>
          <h4 className="text-slate-400 text-xs font-semibold uppercase tracking-widest mb-2 flex items-center gap-1">
            <Leaf size={12} className="text-emerald-400" /> Key Ingredients
          </h4>
          <div className="flex flex-wrap gap-2">
            {routine.key_ingredients.map((ing, i) => (
              <div key={i} className="group relative">
                <span className="text-xs bg-emerald-950/50 border border-emerald-800/40 text-emerald-400 px-2 py-1 rounded-full cursor-default">
                  {ing.name} {ing.concentration ? `(${ing.concentration})` : ""}
                </span>
                <div className="absolute bottom-full left-0 mb-1 hidden group-hover:block z-10 bg-slate-900 border border-slate-700 rounded-lg p-2 w-48 text-xs text-slate-300 shadow-xl">
                  {ing.benefit}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Avoid list */}
      {routine.ingredients_to_avoid?.length > 0 && (
        <div>
          <h4 className="text-slate-400 text-xs font-semibold uppercase tracking-widest mb-2 flex items-center gap-1">
            <AlertTriangle size={12} className="text-red-400" /> Avoid
          </h4>
          <div className="flex flex-col gap-1">
            {routine.ingredients_to_avoid.map((item, i) => (
              <div key={i} className="flex items-start gap-2 text-xs">
                <span className="text-red-400 font-bold mt-0.5">✕</span>
                <span className="text-slate-400">
                  <span className="text-red-300 font-medium">{item.name}</span> — {item.reason}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Lifestyle tips */}
      {routine.lifestyle_tips?.length > 0 && (
        <div>
          <h4 className="text-slate-400 text-xs font-semibold uppercase tracking-widest mb-2">💡 Lifestyle Tips</h4>
          <ul className="flex flex-col gap-1">
            {routine.lifestyle_tips.map((tip, i) => (
              <li key={i} className="text-slate-400 text-xs flex items-start gap-2">
                <span className="text-violet-400">•</span> {tip}
              </li>
            ))}
          </ul>
        </div>
      )}

      <p className="text-slate-600 text-xs border-t border-slate-700/50 pt-3">
        ⚕️ These are ingredient suggestions only — not medical advice. Patch-test new products and consult a dermatologist for persistent conditions.
      </p>
    </div>
  );
}
