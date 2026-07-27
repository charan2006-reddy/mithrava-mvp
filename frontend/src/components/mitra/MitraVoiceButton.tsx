"use client";

import { useCallback, useEffect } from "react";
import { Mic, MicOff, Square, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useVoiceRecording } from "@/hooks/useVoiceRecording";

interface MitraVoiceButtonProps {
  isListening: boolean;
  onToggle: () => void;
  onResult: (transcript: string) => void;
  onVoiceData?: (base64Audio: string) => void;
  disabled?: boolean;
  language?: string;
}

/** Format milliseconds as M:SS */
function formatDuration(ms: number): string {
  const totalSec = Math.floor(ms / 1000);
  const min = Math.floor(totalSec / 60);
  const sec = totalSec % 60;
  return `${min}:${sec.toString().padStart(2, "0")}`;
}

export function MitraVoiceButton({
  isListening,
  onToggle,
  onResult,
  onVoiceData,
  disabled = false,
  language = "hi",
}: MitraVoiceButtonProps) {
  const {
    startRecording,
    stopRecording,
    cancelRecording,
    isRecording,
    durationMs,
    audioLevel,
    isSupported,
  } = useVoiceRecording({
    mimeType: "audio/webm;codecs=opus",
    maxDurationMs: 60_000,
    onRecordingComplete: (blob) => {
      // Convert to base64 and send to backend for server-side STT
      const reader = new FileReader();
      reader.onloadend = () => {
        const dataUrl = reader.result as string;
        const base64 = dataUrl.split(",")[1];
        if (base64 && onVoiceData) {
          onVoiceData(base64);
        }
      };
      reader.readAsDataURL(blob);
    },
    onError: (error) => {
      console.error("Voice recording error:", error);
      // Fall back to Web Speech API for client-side transcription
    },
  });

  // Sync isListening state with recording state
  useEffect(() => {
    if (isListening && !isRecording) {
      startRecording();
    } else if (!isListening && isRecording) {
      stopRecording();
    }
  }, [isListening, isRecording, startRecording, stopRecording]);

  const handleToggle = useCallback(() => {
    onToggle();
  }, [onToggle]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      cancelRecording();
    };
  }, [cancelRecording]);

  const isWebSpeechSupported =
    typeof window !== "undefined" &&
    ("SpeechRecognition" in window || "webkitSpeechRecognition" in window);

  // Show unsupported state
  if (!isSupported && !isWebSpeechSupported) {
    return (
      <Button
        type="button"
        size="icon"
        disabled
        className="h-11 w-11 rounded-xl shrink-0 bg-gray-100 text-gray-400"
        title="Voice input not supported in this browser"
      >
        <MicOff className="h-5 w-5" />
      </Button>
    );
  }

  // Recording state with live feedback
  if (isRecording) {
    return (
      <div className="flex items-center gap-2">
        {/* Live audio level indicator */}
        <div className="flex items-center gap-1 px-2 py-1 rounded-lg bg-red-50 border border-red-200">
          {/* Pulsing bars */}
          <div className="flex items-end gap-0.5 h-4">
            {[0, 1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="w-0.5 bg-red-500 rounded-full transition-all duration-100"
                style={{
                  height: `${Math.max(4, audioLevel * 16 * (1 + Math.sin(i * 0.8)))}px`,
                }}
              />
            ))}
          </div>
          <span className="text-[10px] font-mono text-red-600 ml-1">
            {formatDuration(durationMs)}
          </span>
        </div>

        {/* Stop button */}
        <Button
          type="button"
          size="icon"
          onClick={stopRecording}
          className="h-11 w-11 rounded-xl shrink-0 bg-red-500 text-white hover:bg-red-600 animate-pulse"
          aria-label="Stop recording"
        >
          <Square className="h-4 w-4 fill-current" />
        </Button>
      </div>
    );
  }

  // Default idle state
  return (
    <Button
      type="button"
      size="icon"
      onClick={handleToggle}
      disabled={disabled}
      className={cn(
        "h-11 w-11 rounded-xl shrink-0 transition-all duration-200",
        isListening
          ? "bg-red-500 text-white hover:bg-red-600 animate-pulse"
          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
      )}
      aria-label={isListening ? "Stop recording" : "Start voice input"}
    >
      {isListening ? (
        <Loader2 className="h-5 w-5 animate-spin" />
      ) : (
        <Mic className="h-5 w-5" />
      )}
    </Button>
  );
}
