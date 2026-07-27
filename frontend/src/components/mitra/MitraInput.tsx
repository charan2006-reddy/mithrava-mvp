"use client";

import { useState, useCallback } from "react";
import { Send } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/hooks/useLanguage";
import { Button } from "@/components/ui/button";
import { MitraVoiceButton } from "./MitraVoiceButton";

interface MitraInputProps {
  onSend: (message: string) => void;
  onVoiceToggle: () => void;
  onVoiceData?: (base64Audio: string) => void;
  isListening: boolean;
  isDisabled?: boolean;
}

export function MitraInput({
  onSend,
  onVoiceToggle,
  onVoiceData,
  isListening,
  isDisabled = false,
}: MitraInputProps) {
  const [inputValue, setInputValue] = useState("");
  const { t } = useLanguage();

  const handleSubmit = useCallback(
    (e?: React.FormEvent) => {
      e?.preventDefault();
      if (inputValue.trim() && !isDisabled) {
        onSend(inputValue.trim());
        setInputValue("");
      }
    },
    [inputValue, isDisabled, onSend]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  const handleVoiceResult = useCallback(
    (transcript: string) => {
      if (transcript.trim()) {
        onSend(transcript.trim());
      }
    },
    [onSend]
  );

  const charCount = inputValue.length;
  const maxChars = 500;

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-3">
      <form onSubmit={handleSubmit} className="flex items-end gap-2">
        {/* Voice Button — with backend STT support */}
        <MitraVoiceButton
          isListening={isListening}
          onToggle={onVoiceToggle}
          onResult={handleVoiceResult}
          onVoiceData={onVoiceData}
          disabled={isDisabled}
        />

        {/* Text Input */}
        <div className="flex-1 relative">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value.slice(0, maxChars))}
            onKeyDown={handleKeyDown}
            placeholder={t("mitra.typeMessage")}
            disabled={isDisabled}
            rows={1}
            className={cn(
              "w-full resize-none rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 pr-12 text-sm",
              "placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-mithrava-500 focus:bg-white",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "min-h-[44px] max-h-[120px]"
            )}
            style={{
              height: "auto",
              minHeight: "44px",
            }}
          />
          <span className="absolute bottom-2 right-12 text-[10px] text-gray-400">
            {charCount}/{maxChars}
          </span>
        </div>

        {/* Send Button */}
        <Button
          type="submit"
          size="icon"
          disabled={!inputValue.trim() || isDisabled}
          className={cn(
            "h-11 w-11 rounded-xl shrink-0",
            inputValue.trim()
              ? "bg-mithrava-500 text-white hover:bg-mithrava-600"
              : "bg-gray-100 text-gray-400"
          )}
          aria-label="Send message"
        >
          <Send className="h-5 w-5" />
        </Button>
      </form>
    </div>
  );
}
