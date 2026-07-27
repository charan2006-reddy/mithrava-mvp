"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, ArrowRight, Check, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useLanguage } from "@/hooks/useLanguage";
import { useCreateCrop } from "@/hooks/useCrops";
import { cn } from "@/lib/utils";

/* ─── Crop Grid Data ─── */

const CROP_OPTIONS = [
  { name: "Tomato", emoji: "🍅" },
  { name: "Wheat", emoji: "🌾" },
  { name: "Rice (Paddy)", emoji: "🍚" },
  { name: "Onion", emoji: "🧅" },
  { name: "Potato", emoji: "🥔" },
  { name: "Cotton", emoji: "🧶" },
  { name: "Maize (Corn)", emoji: "🌽" },
  { name: "Chilli", emoji: "🌶️" },
  { name: "Sugarcane", emoji: "🪴" },
  { name: "Soybean", emoji: "🫘" },
  { name: "Groundnut", emoji: "🥜" },
  { name: "Banana", emoji: "🍌" },
  { name: "Mango", emoji: "🥭" },
  { name: "Brinjal (Eggplant)", emoji: "🍆" },
  { name: "Okra (Lady Finger)", emoji: "🟢" },
  { name: "Cabbage", emoji: "🥬" },
  { name: "Carrot", emoji: "🥕" },
  { name: "Coconut", emoji: "🥥" },
  { name: "Turmeric", emoji: "🟡" },
  { name: "Ginger", emoji: "🫚" },
];

/* ─── Step Definitions ─── */

const STEPS = ["Select Crop", "Details", "Review"];

interface FormData {
  name: string;
  emoji: string;
  variety: string;
  sowingDate: string;
  expectedHarvestDate: string;
  area: string;
  areaUnit: "acres" | "hectares";
}

const INITIAL_FORM: FormData = {
  name: "",
  emoji: "",
  variety: "",
  sowingDate: "",
  expectedHarvestDate: "",
  area: "",
  areaUnit: "acres",
};

export default function AddCropPage() {
  const router = useRouter();
  const { t } = useLanguage();
  const [step, setStep] = useState(0);
  const [showSuccess, setShowSuccess] = useState(false);
  const [form, setForm] = useState<FormData>(INITIAL_FORM);
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});

  const createCrop = useCreateCrop();

  const handleChange = useCallback((field: keyof FormData, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  }, []);

  const validateStep = useCallback((): boolean => {
    const newErrors: Partial<Record<keyof FormData, string>> = {};

    if (step === 0) {
      if (!form.name) newErrors.name = "Please select a crop type";
    } else if (step === 1) {
      if (!form.sowingDate) newErrors.sowingDate = "Please select sowing date";
      if (!form.area || parseFloat(form.area) <= 0)
        newErrors.area = "Please enter valid area";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [step, form]);

  const handleNext = useCallback(() => {
    if (validateStep()) {
      setStep((prev) => Math.min(prev + 1, STEPS.length - 1));
    }
  }, [validateStep]);

  const handleBack = useCallback(() => {
    setStep((prev) => Math.max(prev - 1, 0));
  }, []);

  const handleSubmit = useCallback(async () => {
    createCrop.mutate(
      {
        name: form.name,
        variety: form.variety || undefined,
        area: parseFloat(form.area),
        areaUnit: form.areaUnit,
        sowingDate: form.sowingDate,
        expectedHarvestDate: form.expectedHarvestDate || undefined,
      },
      {
        onSuccess: () => {
          setShowSuccess(true);
          toast.success("Crop added successfully! 🌱");
          setTimeout(() => {
            router.push("/crops");
          }, 2000);
        },
        onError: (error: Error) => {
          toast.error(error.message || "Failed to add crop. Please try again.");
        },
      }
    );
  }, [createCrop, form, router]);

  /* ─── Success Animation ─── */
  if (showSuccess) {
    return (
      <div className="p-4 flex items-center justify-center min-h-[60vh]">
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", stiffness: 200, damping: 15 }}
          className="text-center"
        >
          <motion.div
            className="w-24 h-24 rounded-full bg-mithrava-500 flex items-center justify-center mx-auto mb-6"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring" }}
          >
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.5, type: "spring" }}
            >
              <Check className="h-12 w-12 text-white" />
            </motion.div>
          </motion.div>
          <motion.h2
            className="text-2xl font-bold text-gray-900"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            Crop Added! 🌱
          </motion.h2>
          <motion.p
            className="text-gray-500 mt-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9 }}
          >
            Redirecting to your crops...
          </motion.p>
        </motion.div>
      </div>
    );
  }

  const isSubmitting = createCrop.isPending;

  return (
    <div className="p-4 space-y-4">
      {/* Back Button */}
      <button
        onClick={() => (step === 0 ? router.back() : handleBack())}
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-2 min-h-[44px]"
      >
        <ArrowLeft className="h-4 w-4" />
        {step === 0 ? t("common.back") : "Back"}
      </button>

      {/* Step Indicator */}
      <div className="flex items-center gap-2 mb-4">
        {STEPS.map((s, i) => (
          <div key={s} className="flex items-center flex-1">
            <div className="flex flex-col items-center flex-1">
              <div
                className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all",
                  i < step && "bg-mithrava-500 text-white",
                  i === step && "bg-mithrava-500 text-white ring-4 ring-mithrava-100",
                  i > step && "bg-gray-200 text-gray-500"
                )}
              >
                {i < step ? <Check className="h-4 w-4" /> : i + 1}
              </div>
              <p
                className={cn(
                  "text-[10px] mt-1 text-center font-medium",
                  i <= step ? "text-mithrava-600" : "text-gray-400"
                )}
              >
                {s}
              </p>
            </div>
            {i < STEPS.length - 1 && (
              <div
                className={cn(
                  "h-0.5 flex-1 mx-1 mb-4",
                  i < step ? "bg-mithrava-500" : "bg-gray-200"
                )}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.2 }}
        >
          {/* Step 1: Select Crop Type */}
          {step === 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  🌱 Select Crop Type
                </CardTitle>
                {errors.name && (
                  <p className="text-xs text-red-500">{errors.name}</p>
                )}
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 sm:grid-cols-5 gap-2">
                  {CROP_OPTIONS.map((crop) => (
                    <motion.button
                      key={crop.name}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => {
                        handleChange("name", crop.name);
                        handleChange("emoji", crop.emoji);
                      }}
                      className={cn(
                        "flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 transition-all min-h-[80px]",
                        form.name === crop.name
                          ? "border-mithrava-500 bg-mithrava-50 shadow-sm"
                          : "border-gray-200 hover:border-gray-300 bg-white"
                      )}
                    >
                      <span className="text-2xl">{crop.emoji}</span>
                      <span className="text-[10px] font-medium text-center leading-tight text-gray-700">
                        {crop.name}
                      </span>
                    </motion.button>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 2: Details */}
          {step === 1 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  {form.emoji || "🌱"} Crop Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Variety */}
                <div>
                  <Label>Variety (Optional)</Label>
                  <Input
                    placeholder="e.g., Roma, HD-2967, Sona Masuri"
                    value={form.variety}
                    onChange={(e) => handleChange("variety", e.target.value)}
                    className="mt-1.5"
                  />
                </div>

                {/* Sowing Date */}
                <div>
                  <Label>Sowing Date *</Label>
                  <Input
                    type="date"
                    value={form.sowingDate}
                    onChange={(e) => handleChange("sowingDate", e.target.value)}
                    className="mt-1.5"
                  />
                  {errors.sowingDate && (
                    <p className="text-xs text-red-500 mt-1">{errors.sowingDate}</p>
                  )}
                </div>

                {/* Expected Harvest Date */}
                <div>
                  <Label>Expected Harvest Date (Optional)</Label>
                  <Input
                    type="date"
                    value={form.expectedHarvestDate}
                    onChange={(e) =>
                      handleChange("expectedHarvestDate", e.target.value)
                    }
                    className="mt-1.5"
                  />
                </div>

                {/* Area */}
                <div>
                  <Label>Area *</Label>
                  <div className="flex gap-2 mt-1.5">
                    <Input
                      type="number"
                      placeholder="0.0"
                      value={form.area}
                      onChange={(e) => handleChange("area", e.target.value)}
                      min="0"
                      step="0.1"
                      className="flex-1"
                    />
                    <Select
                      value={form.areaUnit}
                      onValueChange={(value) =>
                        handleChange("areaUnit", value as "acres" | "hectares")
                      }
                    >
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="acres">Acres</SelectItem>
                        <SelectItem value="hectares">Hectares</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  {errors.area && (
                    <p className="text-xs text-red-500 mt-1">{errors.area}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 3: Review */}
          {step === 2 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  ✅ Review & Confirm
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="bg-gray-50 rounded-xl p-4 space-y-3">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{form.emoji || "🌱"}</span>
                    <div>
                      <p className="font-semibold text-base">{form.name}</p>
                      {form.variety && (
                        <p className="text-sm text-gray-500">{form.variety}</p>
                      )}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="bg-white rounded-lg p-3 border border-gray-100">
                      <p className="text-gray-400 text-xs">Area</p>
                      <p className="font-medium">
                        {form.area ? `${form.area} ${form.areaUnit}` : "-"}
                      </p>
                    </div>
                    <div className="bg-white rounded-lg p-3 border border-gray-100">
                      <p className="text-gray-400 text-xs">Sowing Date</p>
                      <p className="font-medium">{form.sowingDate || "-"}</p>
                    </div>
                    <div className="bg-white rounded-lg p-3 border border-gray-100">
                      <p className="text-gray-400 text-xs">Expected Harvest</p>
                      <p className="font-medium">{form.expectedHarvestDate || "-"}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Navigation Buttons */}
      <div className="flex gap-3 pt-2">
        {step < STEPS.length - 1 ? (
          <Button onClick={handleNext} className="flex-1 gap-2">
            Next
            <ArrowRight className="h-4 w-4" />
          </Button>
        ) : (
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="flex-1 gap-2"
          >
            {isSubmitting ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <>
                <Check className="h-4 w-4" />
                Add Crop
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}
