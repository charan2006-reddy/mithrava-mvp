"use client";

import { useState } from "react";
import { X, MessageCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/hooks/useLanguage";
import { useMitra } from "@/hooks/useMitra";
import { MitraChat } from "./MitraChat";
import { MitraInput } from "./MitraInput";
import { MitraQuickActions } from "./MitraQuickActions";

export function MitraWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const { t } = useLanguage();
  const {
    messages,
    isTyping,
    isListening,
    sendMessage,
    sendVoiceMessage,
    toggleVoice,
    startNewConversation,
  } = useMitra();

  const handleQuickAction = (prompt: string) => {
    sendMessage(prompt);
  };

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className={cn(
            "flex h-14 w-14 items-center justify-center rounded-full",
            "bg-mithrava-500 text-white shadow-lg hover:bg-mithrava-600",
            "transition-all duration-300 hover:scale-110",
            "animate-pulse"
          )}
          aria-label="Open Mitra AI assistant"
        >
          <MessageCircle className="h-6 w-6" />
        </button>
      )}

      {/* Chat Interface */}
      {isOpen && (
        <div
          className={cn(
            "bg-white rounded-2xl shadow-2xl border border-gray-200",
            "w-[calc(100vw-2rem)] max-w-md",
            "h-[70vh] max-h-[600px]",
            "flex flex-col overflow-hidden",
            "animate-in slide-in-from-bottom-4 fade-in duration-300"
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-200 bg-mithrava-500 px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-mithrava-500 font-bold text-sm">
                M
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">
                  {t("mitra.title")}
                </h3>
                <p className="text-xs text-mithrava-100">
                  {isTyping ? t("mitra.thinking") : "Online"}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={startNewConversation}
                className="rounded-lg p-2 text-white hover:bg-mithrava-600 transition-colors text-xs"
                aria-label="New conversation"
              >
                New Chat
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="rounded-lg p-2 text-white hover:bg-mithrava-600 transition-colors"
                aria-label="Close chat"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          {/* Chat Messages or Quick Actions */}
          {messages.length === 0 ? (
            <div className="flex-1 overflow-y-auto p-4">
              <div className="mb-6 text-center">
                <div className="mx-auto mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-mithrava-100 text-2xl">
                  🤖
                </div>
                <p className="text-sm font-medium text-gray-900">
                  {t("mitra.greeting")}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {t("mitra.welcomeMessage")}
                </p>
              </div>
              <MitraQuickActions onAction={handleQuickAction} />
            </div>
          ) : (
            <MitraChat messages={messages} isTyping={isTyping} />
          )}

          {/* Input */}
          <MitraInput
            onSend={sendMessage}
            onVoiceToggle={toggleVoice}
            onVoiceData={sendVoiceMessage}
            isListening={isListening}
            isDisabled={isTyping}
          />
        </div>
      )}
    </>
  );
}
