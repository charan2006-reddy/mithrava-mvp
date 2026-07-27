"use client";

import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import { Phone, HelpCircle, Loader2, CheckCircle, ClipboardList } from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useLanguage } from "@/hooks/useLanguage";
import { useRequestCall, useMyCalls } from "@/hooks/useSupport";
import type { SupportCallItem } from "@/hooks/useSupport";

const faqs = [
  {
    question: "How do I detect crop diseases?",
    answer:
      "Go to Disease Detection, take a photo of your affected plant, and click Analyze. Mitra will identify the disease and suggest treatment.",
  },
  {
    question: "How accurate is the weather forecast?",
    answer:
      "We use real-time data from meteorological services. Forecasts are updated every 6 hours for the most accurate predictions.",
  },
  {
    question: "Can I use voice commands?",
    answer:
      "Yes! Click the microphone icon in the Mitra chat widget and speak in your preferred language (Hindi, Telugu, Kannada, Tamil, or English).",
  },
  {
    question: "How do I track my expenses?",
    answer:
      "Go to Finance > Expenses and tap 'Add Expense'. You can categorize expenses and track them over time.",
  },
];

const topicOptions = [
  { value: "crop_disease", label: "Crop Disease Help" },
  { value: "weather", label: "Weather Advisory" },
  { value: "market_prices", label: "Market Prices" },
  { value: "finance", label: "Loan & Finance" },
  { value: "technical_issue", label: "App Technical Issue" },
  { value: "other", label: "Other" },
];

const topicLabelMap: Record<string, string> = Object.fromEntries(
  topicOptions.map((opt) => [opt.value, opt.label])
);

const STATUS_COLORS: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700",
  scheduled: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
  cancelled: "bg-red-100 text-red-700",
};

export default function SupportPage() {
  const { t } = useLanguage();
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [form, setForm] = useState({
    topic: "",
    description: "",
    preferredTime: "",
  });

  const requestCall = useRequestCall();
  const { data: myCallsData, isLoading: myCallsLoading } = useMyCalls();

  const handleChange = useCallback(
    (field: string, value: string) => {
      setForm((prev) => ({ ...prev, [field]: value }));
    },
    []
  );

  const handleSubmit = useCallback(async () => {
    if (!form.topic) {
      toast.error(t("support.topicRequired"));
      return;
    }
    if (!form.description.trim()) {
      toast.error(t("support.descriptionRequired"));
      return;
    }

    try {
      await requestCall.mutateAsync({
        topic: form.topic,
        description: form.description,
        preferredTime: form.preferredTime,
      });
      setIsSubmitted(true);
      toast.success(t("support.requestSuccess"));
    } catch {
      toast.error(t("support.submitFailed"));
    }
  }, [form, requestCall, t]);

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-2xl font-bold">{t("support.title")}</h1>

      {/* Callback Request */}
      {isSubmitted ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <Card className="border-green-200 bg-green-50">
            <CardContent className="p-6 text-center">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-green-800">
                {t("support.requestSuccess")}
              </h3>
              <p className="text-sm text-green-600 mt-1">
                {t("support.expertWillCall")}
              </p>
              <Button
                variant="outline"
                className="mt-4"
                onClick={() => {
                  setIsSubmitted(false);
                  setForm({ topic: "", description: "", preferredTime: "" });
                }}
              >
                {t("support.submitAnother")}
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Phone className="h-5 w-5 text-mithrava-500" />
              {t("support.requestCallback")}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Topic *</Label>
              <select
                value={form.topic}
                onChange={(e) => handleChange("topic", e.target.value)}
                className="mt-1.5 flex h-12 w-full rounded-md border border-gray-200 bg-white px-4 py-3 text-base placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-mithrava-500 focus-visible:ring-offset-2"
              >
                <option value="">{t("support.selectTopic")}</option>
                {topicOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <Label>Description *</Label>
              <textarea
                placeholder={t("support.describeIssuePlaceholder")}
                value={form.description}
                onChange={(e) => handleChange("description", e.target.value)}
                rows={4}
                className="mt-1.5 flex w-full rounded-md border border-gray-200 bg-white px-4 py-3 text-base placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-mithrava-500 focus-visible:ring-offset-2"
              />
            </div>
            <div>
              <Label>{t("support.preferredTime")}</Label>
              <select
                value={form.preferredTime}
                onChange={(e) => handleChange("preferredTime", e.target.value)}
                className="mt-1.5 flex h-12 w-full rounded-md border border-gray-200 bg-white px-4 py-3 text-base placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-mithrava-500 focus-visible:ring-offset-2"
              >
                <option value="">{t("support.noPreference")}</option>
                <option value="morning">{t("support.morning")}</option>
                <option value="afternoon">{t("support.afternoon")}</option>
                <option value="evening">{t("support.evening")}</option>
              </select>
            </div>
            <Button
              onClick={handleSubmit}
              disabled={requestCall.isPending}
              className="w-full min-h-[48px]"
            >
              {requestCall.isPending ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                t("support.submitRequest")
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* My Past Requests */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <ClipboardList className="h-5 w-5 text-mithrava-500" />
              {t("support.myPastRequests")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {myCallsLoading ? (
              <div className="flex items-center justify-center py-6">
                <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
              </div>
            ) : myCallsData?.calls?.length === 0 ? (
              <p className="text-sm text-gray-500 py-4 text-center">
                {t("support.noRequests")}
              </p>
            ) : (
              <div className="space-y-3">
                {myCallsData?.calls?.map((call: SupportCallItem, index: number) => (
                  <motion.div
                    key={call.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="rounded-lg border border-gray-100 p-3 space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        {topicLabelMap[call.topic] ?? call.topic}
                      </span>
                      <Badge
                        className={`text-xs ${STATUS_COLORS[call.status] ?? "bg-gray-100 text-gray-700"}`}
                      >
                        {call.status}
                      </Badge>
                    </div>
                    {call.preferred_time && (
                      <p className="text-xs text-gray-500">
                        Preferred time: {call.preferred_time}
                      </p>
                    )}
                    {call.admin_notes && (
                      <p className="text-xs text-gray-500 italic">
                        {call.admin_notes}
                      </p>
                    )}
                    {call.created_at && (
                      <p className="text-xs text-gray-400">
                        {new Date(call.created_at).toLocaleDateString()}
                      </p>
                    )}
                  </motion.div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* FAQ Section */}
      <div>
        <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <HelpCircle className="h-5 w-5" />
          {t("support.faq")}
        </h2>
        <div className="space-y-3">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card>
                <CardContent className="p-4">
                  <p className="font-medium text-sm mb-1">{faq.question}</p>
                  <p className="text-sm text-gray-600">{faq.answer}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
