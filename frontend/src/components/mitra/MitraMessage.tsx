"use client";

import { useState, useCallback, useRef } from "react";
import { Volume2, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { getInitials } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/hooks/useLanguage";
import { mitraService } from "@/services/mitraService";
import type { MitraMessage as MitraMessageType } from "@/types/mitra";

interface MitraMessageBubbleProps {
  message: MitraMessageType;
}

export function MitraMessageBubble({ message }: MitraMessageBubbleProps) {
  const { user } = useAuth();
  const { language } = useLanguage();
  const isUser = message.role === "user";
  const [isPlaying, setIsPlaying] = useState(false);
  const [ttsError, setTtsError] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  /** Play TTS audio for this message */
  const handlePlayTTS = useCallback(async () => {
    // If already playing, stop
    if (audioRef.current && !audioRef.current.paused) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
      return;
    }

    setIsPlaying(true);
    setTtsError(false);

    try {
      const response = await mitraService.getTTS(message.content, language);
      const url = URL.createObjectURL(response);
      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(url);
        audioRef.current = null;
      };

      audio.onerror = () => {
        setIsPlaying(false);
        setTtsError(true);
        URL.revokeObjectURL(url);
        audioRef.current = null;
      };

      await audio.play();
    } catch {
      setIsPlaying(false);
      setTtsError(true);
    }
  }, [message.content, language]);

  return (
    <div
      className={cn(
        "flex items-end gap-2",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold",
          isUser
            ? "bg-mithrava-500 text-white"
            : "bg-mithrava-100 text-mithrava-600"
        )}
      >
        {isUser ? (
          user?.name ? (
            getInitials(user.name)
          ) : (
            "U"
          )
        ) : (
          "M"
        )}
      </div>

      {/* Message Bubble */}
      <div
        className={cn(
          "max-w-[75%] rounded-2xl px-4 py-3",
          isUser
            ? "rounded-tr-sm bg-mithrava-500 text-white"
            : "rounded-tl-sm bg-gray-100 text-gray-900"
        )}
      >
        <p className="text-sm whitespace-pre-wrap break-words">
          {message.content}
        </p>
        <div
          className={cn(
            "mt-1 flex items-center gap-2 text-[10px]",
            isUser ? "text-mithrava-100" : "text-gray-400"
          )}
        >
          <span>
            {new Date(message.createdAt).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
          {message.isVoice && <span>🎤</span>}

          {/* TTS Play button — only for assistant messages */}
          {!isUser && (
            <button
              onClick={handlePlayTTS}
              disabled={isPlaying}
              className={cn(
                "inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-full transition-colors",
                isPlaying
                  ? "bg-mithrava-200 text-mithrava-700"
                  : "hover:bg-gray-200 text-gray-500",
                ttsError && "text-red-400"
              )}
              title={ttsError ? "TTS unavailable" : "Listen to this message"}
              aria-label="Play voice"
            >
              {isPlaying ? (
                <Loader2 className="h-3 w-3 animate-spin" />
              ) : (
                <Volume2 className="h-3 w-3" />
              )}
              <span className="text-[9px]">
                {isPlaying ? "..." : ttsError ? "N/A" : "Listen"}
              </span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
