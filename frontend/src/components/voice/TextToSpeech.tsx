"use client";

import { useState, useCallback, useRef } from "react";
import { Volume2, VolumeX, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/hooks/useLanguage";
import { useVoiceStore } from "@/stores/voiceStore";
import { mitraService } from "@/services/mitraService";
import { Button } from "@/components/ui/button";

interface TextToSpeechProps {
  /** The text content to read aloud */
  text: string;
  /** Optional override for language code. Defaults to current app language. */
  language?: string;
  /** Size variant */
  size?: "sm" | "default";
  /** Additional CSS classes */
  className?: string;
  /** Accessible label override */
  ariaLabel?: string;
}

/**
 * Reusable "Read Aloud" button that uses server-side TTS via mitraService.
 *
 * Usage:
 *   <TextToSpeech text="Weather: 32°C, Sunny" />
 *   <TextToSpeech text={cropSummary} language="hi" size="sm" />
 */
export function TextToSpeech({
  text,
  language,
  size = "sm",
  className,
  ariaLabel,
}: TextToSpeechProps) {
  const { language: appLanguage } = useLanguage();
  const { setSpeaking } = useVoiceStore();
  const [isPlaying, setIsPlaying] = useState(false);
  const [isError, setIsError] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const objectUrlRef = useRef<string | null>(null);

  const lang = language || appLanguage;

  /** Stop any currently playing audio */
  const stopPlayback = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
      objectUrlRef.current = null;
    }
    setIsPlaying(false);
    setSpeaking(false);
  }, [setSpeaking]);

  /** Toggle TTS playback */
  const handleToggle = useCallback(async () => {
    // If already playing, stop
    if (isPlaying) {
      stopPlayback();
      return;
    }

    if (!text?.trim()) return;

    setIsPlaying(true);
    setIsError(false);
    setSpeaking(true);

    try {
      const response = await mitraService.getTTS(text.trim(), lang);
      const url = URL.createObjectURL(response);
      objectUrlRef.current = url;

      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onended = () => {
        setIsPlaying(false);
        setSpeaking(false);
        URL.revokeObjectURL(url);
        objectUrlRef.current = null;
        audioRef.current = null;
      };

      audio.onerror = () => {
        setIsPlaying(false);
        setIsError(true);
        setSpeaking(false);
        URL.revokeObjectURL(url);
        objectUrlRef.current = null;
        audioRef.current = null;
      };

      await audio.play();
    } catch {
      setIsPlaying(false);
      setIsError(true);
      setSpeaking(false);
    }
  }, [text, lang, isPlaying, stopPlayback, setSpeaking]);

  const isSmall = size === "sm";

  return (
    <Button
      type="button"
      variant="ghost"
      size={isSmall ? "sm" : "default"}
      onClick={handleToggle}
      disabled={!text?.trim()}
      className={cn(
        "gap-1.5 transition-colors",
        isSmall ? "h-8 px-2 text-xs" : "h-10 px-3 text-sm",
        isPlaying
          ? "text-mithrava-600 bg-mithrava-50 hover:bg-mithrava-100"
          : isError
          ? "text-red-400 hover:text-red-500"
          : "text-gray-500 hover:text-mithrava-600 hover:bg-gray-50",
        className
      )}
      aria-label={ariaLabel || (isPlaying ? "Stop reading aloud" : "Read aloud")}
      title={isPlaying ? "Stop reading" : "Read aloud"}
    >
      {isPlaying ? (
        <>
          <VolumeX className={cn("animate-pulse", isSmall ? "h-3.5 w-3.5" : "h-4 w-4")} />
          <span className="hidden sm:inline">Stop</span>
        </>
      ) : isError ? (
        <>
          <Volume2 className={cn(isSmall ? "h-3.5 w-3.5" : "h-4 w-4")} />
          <span className="hidden sm:inline">N/A</span>
        </>
      ) : (
        <>
          <Volume2 className={cn(isSmall ? "h-3.5 w-3.5" : "h-4 w-4")} />
          <span className="hidden sm:inline">Listen</span>
        </>
      )}
    </Button>
  );
}
