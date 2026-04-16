import React from "react";
import useStore from "../store/useStore";

const VIEWS = [
  { key: "annotated", label: "Annotated" },
  { key: "heatmap",   label: "Heat Map"  },
  { key: "original",  label: "Original"  },
];

export default function AnnotatedImageViewer({ result }) {
  const { imageView, setImageView, previewUrl } = useStore();

  const src =
    imageView === "annotated" ? `data:image/png;base64,${result.annotated_image}` :
    imageView === "heatmap"   ? `data:image/png;base64,${result.heatmap_image}` :
    previewUrl;

  return (
    <div className="flex flex-col gap-3">
      {/* View switcher */}
      <div className="flex rounded-xl overflow-hidden border border-slate-700 w-fit">
        {VIEWS.map((v) => (
          <button
            key={v.key}
            onClick={() => setImageView(v.key)}
            className={`px-4 py-1.5 text-sm font-medium transition
              ${imageView === v.key ? "bg-violet-600 text-white" : "text-slate-400 hover:text-white"}`}
          >
            {v.label}
          </button>
        ))}
      </div>

      {/* Image */}
      <div className="relative rounded-2xl overflow-hidden border border-slate-700/50 bg-black">
        <img
          src={src}
          alt={imageView}
          className="w-full object-contain max-h-96"
        />

        {/* Overlay legend */}
        {imageView === "annotated" && (
          <div className="absolute bottom-2 left-2 flex flex-col gap-1 bg-black/60 rounded-lg p-2">
            {[
              { color: "#22c55e", label: "Comedonal" },
              { color: "#ef4444", label: "Inflammatory" },
              { color: "#3b82f6", label: "Nodular/Cystic" },
              { color: "#ff8c00", label: "Dark Spots" },
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-2 text-xs text-white">
                <span className="w-3 h-3 rounded-sm flex-shrink-0" style={{ background: item.color }} />
                {item.label}
              </div>
            ))}
          </div>
        )}

        {imageView === "heatmap" && (
          <div className="absolute bottom-2 left-2 bg-black/60 rounded-lg p-2">
            <div className="flex items-center gap-1 text-xs text-white">
              <div className="w-20 h-3 rounded" style={{
                background: "linear-gradient(to right, #000080, #0000ff, #00ffff, #ffff00, #ff0000)"
              }} />
              <span className="text-slate-400 text-xs ml-1">Low → High density</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
