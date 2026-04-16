import React, { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Camera, Upload, RefreshCw } from "lucide-react";
import useStore from "../store/useStore";
import { analyzeImage } from "../api";
import toast from "react-hot-toast";

const TIPS = [
  "Face the camera directly in natural light",
  "Remove glasses and pull hair away from face",
  "No filter or heavy makeup for best results",
  "Use a 720p+ photo for highest accuracy",
];

export default function UploadZone() {
  const {
    previewUrl, uploadedFile, isAnalyzing,
    setUploadedFile, setIsAnalyzing, setAnalysisResult, setAnalysisError, reset,
  } = useStore();

  const onDrop = useCallback((accepted) => {
    if (accepted.length > 0) setUploadedFile(accepted[0]);
  }, [setUploadedFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/jpeg": [], "image/png": [], "image/webp": [] },
    maxFiles: 1,
    disabled: isAnalyzing,
  });

  const handleAnalyze = async () => {
    if (!uploadedFile) return;
    setIsAnalyzing(true);
    const toastId = toast.loading("Analyzing your skin…", { duration: 30000 });
    try {
      const result = await analyzeImage(uploadedFile);
      setAnalysisResult(result);
      toast.success("Analysis complete!", { id: toastId });
    } catch (err) {
      const msg = err?.response?.data?.detail || "Analysis failed. Please try again.";
      setAnalysisError(msg);
      toast.error(msg, { id: toastId });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-6 w-full max-w-xl mx-auto">
      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`relative w-full rounded-2xl border-2 border-dashed cursor-pointer transition-all
          ${isDragActive ? "border-violet-400 bg-violet-950/30" : "border-slate-600 bg-slate-800/50 hover:border-violet-500 hover:bg-slate-800"}
          ${previewUrl ? "p-2" : "p-10"}`}
      >
        <input {...getInputProps()} />
        {previewUrl ? (
          <img
            src={previewUrl}
            alt="Preview"
            className="w-full rounded-xl object-cover max-h-80"
          />
        ) : (
          <div className="flex flex-col items-center gap-3 text-slate-400">
            <div className="p-4 bg-slate-700 rounded-full">
              <Camera size={32} className="text-violet-400" />
            </div>
            <p className="text-lg font-semibold text-slate-200">
              {isDragActive ? "Drop your selfie here" : "Upload a selfie"}
            </p>
            <p className="text-sm">Drag & drop or click to browse</p>
            <p className="text-xs text-slate-500">JPEG · PNG · WebP · max 10MB</p>
          </div>
        )}
      </div>

      {/* Tips */}
      {!previewUrl && (
        <div className="grid grid-cols-2 gap-2 w-full">
          {TIPS.map((tip, i) => (
            <div key={i} className="flex items-start gap-2 text-xs text-slate-400 bg-slate-800/60 rounded-lg p-2">
              <span className="text-violet-400 font-bold mt-0.5">✓</span> {tip}
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      {previewUrl && (
        <div className="flex gap-3 w-full">
          <button
            onClick={reset}
            disabled={isAnalyzing}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-700 text-slate-300 hover:bg-slate-600 transition text-sm disabled:opacity-50"
          >
            <RefreshCw size={14} /> Retake
          </button>
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl
              bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white font-semibold
              hover:from-violet-500 hover:to-fuchsia-500 transition shadow-lg
              disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isAnalyzing ? (
              <>
                <span className="animate-spin">⏳</span> Analyzing…
              </>
            ) : (
              <>
                <Upload size={16} /> Analyze My Skin
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}
