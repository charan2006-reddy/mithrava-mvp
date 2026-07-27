"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { MitraChat } from "@/components/mitra/MitraChat";
import { MitraInput } from "@/components/mitra/MitraInput";
import { MitraQuickActions } from "@/components/mitra/MitraQuickActions";
import { useLanguage } from "@/hooks/useLanguage";
import { useMitra } from "@/hooks/useMitra";

export default function MitraPage() {
  const router = useRouter();
  const { t } = useLanguage();
  const [isListening, setIsListening] = useState(false);

  const {
    messages,
    isTyping,
    sendMessage,
    sendVoiceMessage,
  } = useMitra();

  const handleSend = useCallback(
    (message: string) => {
      sendMessage(message);
    },
    [sendMessage]
  );

  const handleVoiceToggle = useCallback(() => {
    setIsListening((prev) => !prev);
  }, []);

  const handleVoiceData = useCallback(
    (base64Audio: string) => {
      setIsListening(false);
      sendVoiceMessage(base64Audio);
    },
    [sendVoiceMessage]
  );

  const hasMessages = messages.length > 0;

  return (
    <div className="flex flex-col h-[calc(100dvh-64px)] md:h-screen bg-white">
      {/* ── Header ── */}
      <div className="flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-3 shrink-0">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.back()}
          className="shrink-0"
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-mithrava-500 text-white text-lg shrink-0 shadow-sm">
            🤖
          </div>
          <div>
            <h1 className="text-lg font-bold">{t("mitra.title")}</h1>
            <p className="text-xs text-mithrava-500">
              {t("mitra.askAnything")}
            </p>
          </div>
        </div>
      </div>

      {/* ── Chat Area ── */}
      {!hasMessages ? (
        /* ── Empty State: Quick Actions ── */
        <div className="flex-1 flex flex-col items-center justify-center p-6 space-y-8 overflow-y-auto">
          <div className="text-center space-y-3">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-mithrava-100 text-4xl mx-auto shadow-md">
              🤖
            </div>
            <h2 className="text-xl font-bold text-gray-900">
              {t("mitra.greeting")}
            </h2>
            <p className="text-sm text-gray-500 max-w-xs mx-auto">
              {t("mitra.welcomeMessage")}
            </p>
          </div>

          <MitraQuickActions onAction={handleSend} />
        </div>
      ) : (
        /* ── Messages ── */
        <MitraChat messages={messages} isTyping={isTyping} />
      )}

      {/* ── Input Bar ── */}
      <div className="shrink-0">
        <MitraInput
          onSend={handleSend}
          onVoiceToggle={handleVoiceToggle}
          onVoiceData={handleVoiceData}
          isListening={isListening}
          isDisabled={isTyping}
        />
      </div>
    </div>
  );
}
