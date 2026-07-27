"use client";

import { useCallback, useRef, useState } from "react";

interface UseVoiceRecordingOptions {
  /** MIME type preference — browser picks the best supported */
  mimeType?: string;
  /** Maximum recording duration in milliseconds (default: 60s) */
  maxDurationMs?: number;
  /** Called when recording completes with the audio blob */
  onRecordingComplete?: (blob: Blob) => void;
  /** Called on error */
  onError?: (error: string) => void;
}

interface UseVoiceRecordingReturn {
  /** Start recording audio */
  startRecording: () => void;
  /** Stop recording and trigger onRecordingComplete */
  stopRecording: () => void;
  /** Cancel the current recording without triggering completion */
  cancelRecording: () => void;
  /** Whether currently recording */
  isRecording: boolean;
  /** Recording duration in milliseconds (live) */
  durationMs: number;
  /** Audio level for visual feedback (0 to 1) */
  audioLevel: number;
  /** The recorded Blob after completion */
  recordedBlob: Blob | null;
  /** Whether the browser supports recording */
  isSupported: boolean;
}

/** Find a supported MIME type from a list of preferences */
function getSupportedMimeType(preferred?: string): string | null {
  if (typeof MediaRecorder === "undefined") return null;

  const types = preferred
    ? [preferred, "audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus", "audio/mp4"]
    : ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus", "audio/mp4"];

  for (const type of types) {
    if (MediaRecorder.isTypeSupported(type)) {
      return type;
    }
  }
  return null;
}

/**
 * Hook for recording audio from the microphone using MediaRecorder API.
 *
 * Features:
 * - Automatic MIME type detection (WebM, OGG, MP4)
 * - Live audio level metering for visual feedback
 * - Duration tracking
 * - Max duration auto-stop
 * - Clean cancellation support
 */
export function useVoiceRecording({
  mimeType,
  maxDurationMs = 60_000,
  onRecordingComplete,
  onError,
}: UseVoiceRecordingOptions = {}): UseVoiceRecordingReturn {
  const [isRecording, setIsRecording] = useState(false);
  const [durationMs, setDurationMs] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const startTimeRef = useRef<number>(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const levelIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const maxDurationTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const supportedMimeType = getSupportedMimeType(mimeType);
  const isSupported = typeof window !== "undefined" && !!supportedMimeType;

  /** Start audio level monitoring */
  const startLevelMonitoring = useCallback((stream: MediaStream) => {
    try {
      const audioCtx = new AudioContext();
      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);
      levelIntervalRef.current = setInterval(() => {
        analyser.getByteFrequencyData(dataArray);
        const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
        setAudioLevel(Math.min(1, avg / 128));
      }, 100);
    } catch {
      // AudioContext not available — no level feedback
    }
  }, []);

  /** Stop level monitoring and clean up audio context */
  const stopLevelMonitoring = useCallback(() => {
    if (levelIntervalRef.current) {
      clearInterval(levelIntervalRef.current);
      levelIntervalRef.current = null;
    }
    analyserRef.current = null;
    setAudioLevel(0);
  }, []);

  /** Clean up all intervals and stream */
  const cleanup = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    if (maxDurationTimerRef.current) {
      clearTimeout(maxDurationTimerRef.current);
      maxDurationTimerRef.current = null;
    }
    stopLevelMonitoring();

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  }, [stopLevelMonitoring]);

  /** Start recording */
  const startRecording = useCallback(async () => {
    if (!supportedMimeType) {
      onError?.("Audio recording is not supported in this browser.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      streamRef.current = stream;
      chunksRef.current = [];
      startTimeRef.current = Date.now();
      setDurationMs(0);
      setRecordedBlob(null);

      const recorder = new MediaRecorder(stream, {
        mimeType: supportedMimeType,
      });

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: supportedMimeType });
        setRecordedBlob(blob);
        setIsRecording(false);
        cleanup();
        onRecordingComplete?.(blob);
      };

      recorder.onerror = () => {
        onError?.("Recording failed. Please try again.");
        setIsRecording(false);
        cleanup();
      };

      mediaRecorderRef.current = recorder;
      recorder.start(100); // Collect data every 100ms
      setIsRecording(true);

      // Start duration timer
      timerRef.current = setInterval(() => {
        setDurationMs(Date.now() - startTimeRef.current);
      }, 100);

      // Auto-stop at max duration
      maxDurationTimerRef.current = setTimeout(() => {
        if (recorder.state === "recording") {
          recorder.stop();
        }
      }, maxDurationMs);

      // Start level monitoring
      startLevelMonitoring(stream);
    } catch (err) {
      const msg =
        err instanceof DOMException && err.name === "NotAllowedError"
          ? "Microphone permission denied. Please allow microphone access."
          : "Could not access microphone. Please check your device settings.";
      onError?.(msg);
    }
  }, [supportedMimeType, maxDurationMs, onRecordingComplete, onError, cleanup, startLevelMonitoring]);

  /** Stop recording */
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
  }, []);

  /** Cancel recording without triggering completion */
  const cancelRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.ondataavailable = null;
      mediaRecorderRef.current.onstop = null;
      mediaRecorderRef.current.stop();
    }
    chunksRef.current = [];
    setIsRecording(false);
    setRecordedBlob(null);
    cleanup();
  }, [cleanup]);

  return {
    startRecording,
    stopRecording,
    cancelRecording,
    isRecording,
    durationMs,
    audioLevel,
    recordedBlob,
    isSupported,
  };
}
