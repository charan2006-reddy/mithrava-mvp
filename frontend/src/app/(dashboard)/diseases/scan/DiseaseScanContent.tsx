"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Camera, Upload, RotateCcw, ArrowLeft, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ScanResult } from "@/components/diseases/ScanResult";
import { diseaseService } from "@/services/diseaseService";
import type { DiseaseScanDetail } from "@/types/disease";

type ScanState = "idle" | "preview" | "analyzing" | "results";

export default function DiseaseScanContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const scanId = searchParams.get("id");

  const [state, setState] = useState<ScanState>(scanId ? "analyzing" : "idle");
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<DiseaseScanDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scanId) {
      loadExistingScan(scanId);
    }
  }, [scanId]);

  async function loadExistingScan(id: string) {
    setState("analyzing");
    try {
      const response = await diseaseService.getScanDetail(id);
      setResult(response.data);
      setState("results");
    } catch {
      toast.error("Could not load scan result");
      setState("idle");
    }
  }

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        const url = URL.createObjectURL(file);
        setPreviewUrl(url);
        setState("preview");
        setResult(null);
      }
    },
    []
  );

  const handleCameraCapture = useCallback(() => {
    cameraInputRef.current?.click();
  }, []);

  const handleGalleryUpload = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!previewUrl) {
      toast.error("Please select an image first");
      return;
    }

    setState("analyzing");
    setError(null);

    try {
      const file = fileInputRef.current?.files?.[0] || cameraInputRef.current?.files?.[0];
      const actualFile = file || fileInputRef.current?.files?.[0] || cameraInputRef.current?.files?.[0];
      if (!actualFile) {
        setError("Please re-select the image file and try again.");
        setState("idle");
        return;
      }

      const response = await diseaseService.scanImage(actualFile);
      setResult(response.data);
      setPreviewUrl(response.data.imageUrl || previewUrl);
      setState("results");
      toast.success("Analysis complete!");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Analysis failed. Please try again.";
      setError(msg);
      setState("idle");
      toast.error(msg);
    }
  }, [previewUrl]);

  const handleReset = useCallback(() => {
    setState("idle");
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
    if (cameraInputRef.current) cameraInputRef.current.value = "";
    router.replace("/diseases/scan");
  }, [router]);

  const handleSave = useCallback(() => {
    toast.success("Scan saved to history!");
  }, []);

  const handleAskMitra = useCallback(() => {
    if (result) {
      const question = `What is the best treatment for ${result.diseaseName} in ${result.cropName || "my crop"}?`;
      window.location.href = `/?mitra=${encodeURIComponent(question)}`;
    }
  }, [result]);

  return (
    <div className="p-4 space-y-4 pb-8">
      <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileSelect} className="hidden" />
      <input ref={cameraInputRef} type="file" accept="image/*" capture="environment" onChange={handleFileSelect} className="hidden" />

      <div className="flex items-center gap-3">
        {state !== "idle" ? (
          <Button variant="ghost" size="icon" onClick={state === "results" ? handleReset : () => setState("idle")}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
        ) : (
          <Button variant="ghost" size="icon" onClick={() => router.push("/diseases")}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
        )}
        <div>
          <h1 className="text-xl font-bold">🔬 Scan Plant</h1>
          <p className="text-xs text-gray-500">Take a clear photo of the affected area</p>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {state === "idle" && (
          <motion.div key="idle" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-4">
            <Card className="border-gray-200 overflow-hidden">
              <CardContent className="p-8">
                <div className="flex flex-col items-center gap-6">
                  <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} onClick={handleCameraCapture} className="flex h-32 w-32 items-center justify-center rounded-full bg-mithrava-500 text-white shadow-xl shadow-mithrava-200 hover:bg-mithrava-600 transition-colors">
                    <Camera className="h-14 w-14" />
                  </motion.button>
                  <div className="text-center">
                    <p className="font-semibold text-base">Take a Photo</p>
                    <p className="text-sm text-gray-500 mt-1">Point camera at affected leaves</p>
                  </div>
                  <div className="flex items-center gap-4 w-full">
                    <div className="flex-1 h-px bg-gray-200" />
                    <span className="text-xs text-gray-400 font-medium">OR</span>
                    <div className="flex-1 h-px bg-gray-200" />
                  </div>
                  <Button variant="outline" onClick={handleGalleryUpload} className="w-full gap-2">
                    <Upload className="h-5 w-5" />
                    Choose from Gallery
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="border-amber-200 bg-amber-50/50">
              <CardContent className="p-4">
                <h3 className="font-semibold text-sm mb-2">📸 Photo Tips</h3>
                <ul className="space-y-1.5">
                  <li className="text-xs text-gray-600 flex items-start gap-2"><span className="text-green-500 mt-0.5">✓</span>Use natural daylight for best accuracy</li>
                  <li className="text-xs text-gray-600 flex items-start gap-2"><span className="text-green-500 mt-0.5">✓</span>Get close to the affected leaf or stem</li>
                  <li className="text-xs text-gray-600 flex items-start gap-2"><span className="text-green-500 mt-0.5">✓</span>Include both healthy and affected areas</li>
                  <li className="text-xs text-gray-600 flex items-start gap-2"><span className="text-red-500 mt-0.5">✗</span>Avoid blurry or dark photos</li>
                </ul>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {state === "idle" && error && (
          <motion.div key="error" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="border-red-200 bg-red-50">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <span className="text-2xl">⚠️</span>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-red-800">Analysis Failed</p>
                    <p className="text-xs text-red-600 mt-1">{error}</p>
                  </div>
                  <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600 text-xs font-medium shrink-0">Dismiss</button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {state === "preview" && previewUrl && (
          <motion.div key="preview" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-4">
            <Card className="border-gray-200 overflow-hidden">
              <CardContent className="p-0">
                <div className="relative">
                  <img src={previewUrl} alt="Plant preview" className="w-full h-64 object-cover" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
                </div>
              </CardContent>
            </Card>
            <div className="flex gap-3">
              <Button variant="outline" onClick={handleReset} className="flex-1 gap-2">
                <RotateCcw className="h-4 w-4" />Retake
              </Button>
              <Button onClick={handleAnalyze} className="flex-1 gap-2">🔬 Analyze Plant</Button>
            </div>
          </motion.div>
        )}

        {state === "analyzing" && (
          <motion.div key="analyzing" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }}>
            <Card className="border-mithrava-200 bg-gradient-to-br from-mithrava-50 to-white">
              <CardContent className="p-12 flex flex-col items-center text-center">
                <motion.div animate={{ scale: [1, 1.15, 1], opacity: [0.8, 1, 0.8] }} transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }} className="text-6xl mb-6">🌿</motion.div>
                <div className="flex items-center gap-2 mb-4">
                  <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: 0 }} className="h-2 w-2 rounded-full bg-mithrava-500" />
                  <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: 0.3 }} className="h-2 w-2 rounded-full bg-mithrava-500" />
                  <motion.div animate={{ opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: 0.6 }} className="h-2 w-2 rounded-full bg-mithrava-500" />
                </div>
                <h3 className="text-lg font-bold text-mithrava-800">Analyzing your plant...</h3>
                <p className="text-sm text-gray-500 mt-2">Our AI is looking at leaf patterns, colors, and textures</p>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {state === "results" && result && (
          <motion.div key="results" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
            {(previewUrl || result.imageUrl) && (
              <div className="rounded-xl overflow-hidden mb-4">
                <img src={result.imageUrl || previewUrl || ""} alt="Scanned plant" className="w-full h-40 object-cover" />
              </div>
            )}
            <ScanResult result={result} onSave={handleSave} onAskMitra={handleAskMitra} />
            <div className="pt-4">
              <Button variant="outline" onClick={handleReset} className="w-full gap-2">
                <Camera className="h-5 w-5" />Scan Another Plant
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
