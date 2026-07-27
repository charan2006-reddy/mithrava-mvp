"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mic, MicOff, X, Minimize2, Maximize2, Loader2,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useLanguage } from "@/hooks/useLanguage";
import { useVoiceStore } from "@/stores/voiceStore";
import {
  processVoiceCommand,
  getVoiceCommandSuggestions,
  isSpeechRecognitionSupported,
  getSpeechRecognitionConstructor,
  getSpeechRecognitionLang,
} from "@/services/voiceCommandService";
import { Button } from "@/components/ui/button";

// ─── Language display names ───────────────────────────────────────────────────

const LANG_DISPLAY: Record<string, string> = {
  en: "English",
  hi: "हिंदी",
  te: "తెలుగు",
  kn: "ಕನ್ನಡ",
  ta: "தமிழ்",
};

// ─── Waveform animation component ────────────────────────────────────────────

function WaveformAnimation({ audioLevel = 0.5 }: { audioLevel?: number }) {
  // Use CSS animation instead of render-time Math.sin/Date.now to avoid hydration mismatch
  return (
    <div className="flex items-center justify-center gap-[3px] h-6">
      {[0, 1, 2, 3, 4, 5, 6].map((i) => (
        <motion.div
          key={i}
          className="w-[3px] bg-white rounded-full"
          animate={{
            height: [
              `${Math.max(4, audioLevel * 8)}px`,
              `${Math.max(4, audioLevel * 24)}px`,
              `${Math.max(4, audioLevel * 8)}px`,
            ],
            opacity: [0.7, 1, 0.7],
          }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            repeatType: "reverse",
            delay: i * 0.08,
          }}
        />
      ))}
    </div>
  );
}

// ─── Main VoiceBar Component ──────────────────────────────────────────────────

export function VoiceBar() {
  const router = useRouter();
  const { language, setLanguage } = useLanguage();
  const {
    isListening,
    isSpeaking,
    transcript,
    lastCommand,
    isMinimized,
    setListening,
    setTranscript,
    setLastCommand,
    setMinimized,
    setSpeaking,
  } = useVoiceStore();

  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);
  const [feedbackType, setFeedbackType] = useState<"success" | "error" | "info">("info");
  const [audioLevel, setAudioLevel] = useState(0);
  const [isSupported] = useState(() => isSpeechRecognitionSupported());

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const levelIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const feedbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Cleanup on unmount ──
  useEffect(() => {
    return () => {
      stopListening();
      if (feedbackTimerRef.current) clearTimeout(feedbackTimerRef.current);
      if (levelIntervalRef.current) clearInterval(levelIntervalRef.current);
      if (audioContextRef.current) {
        audioContextRef.current.close().catch(() => {});
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Show feedback message ──
  const showFeedback = useCallback(
    (message: string, type: "success" | "error" | "info" = "info", duration = 3000) => {
      setFeedbackMessage(message);
      setFeedbackType(type);
      if (feedbackTimerRef.current) clearTimeout(feedbackTimerRef.current);
      feedbackTimerRef.current = setTimeout(() => {
        setFeedbackMessage(null);
      }, duration);
    },
    []
  );

  // ── Start audio level monitoring ──
  const startLevelMonitoring = useCallback((stream: MediaStream) => {
    try {
      const audioCtx = new AudioContext();
      const source = audioCtx.createMediaStreamSource(stream);
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      audioContextRef.current = audioCtx;
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

  // ── Stop audio level monitoring ──
  const stopLevelMonitoring = useCallback(() => {
    if (levelIntervalRef.current) {
      clearInterval(levelIntervalRef.current);
      levelIntervalRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    analyserRef.current = null;
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setAudioLevel(0);
  }, []);

  // ── Process the recognized command ──
  const processCommand = useCallback(
    (text: string) => {
      const command = processVoiceCommand(text, language);
      setLastCommand(command);

      switch (command.intent) {
        case "navigate": {
          if (command.target) {
            showFeedback(`Navigating to ${command.target}`, "success");
            setTimeout(() => router.push(command.target!), 500);
          }
          break;
        }
        case "query": {
          // Navigate to the relevant page for the query
          const queryRoutes: Record<string, string> = {
            weather_query: "/weather",
            crop_query: "/crops",
            price_query: "/market",
            finance_query: "/finance",
            general_query: "/mitra",
          };
          const route = queryRoutes[command.target || "general_query"] || "/mitra";
          const cropParam = command.params?.crop ? `?crop=${command.params.crop}` : "";
          showFeedback(`Opening ${command.target?.replace("_query", "") || "results"}`, "info");
          setTimeout(() => router.push(`${route}${cropParam}`), 500);
          break;
        }
        case "action": {
          switch (command.target) {
            case "read_aloud":
              showFeedback("Reading aloud enabled", "info");
              // Dispatch a custom event that TextToSpeech components can listen to
              window.dispatchEvent(new CustomEvent("mithrava:read-aloud"));
              break;
            case "stop_reading":
              showFeedback("Stopping playback", "info");
              // Stop all audio
              document.querySelectorAll("audio").forEach((a) => {
                a.pause();
                a.currentTime = 0;
              });
              setSpeaking(false);
              break;
            case "change_language": {
              const newLang = command.params?.language;
              if (newLang) {
                setLanguage(newLang as "en" | "hi" | "te" | "kn" | "ta");
                showFeedback(
                  `Language changed to ${LANG_DISPLAY[newLang] || newLang}`,
                  "success"
                );
              }
              break;
            }
            case "add_crop":
              showFeedback("Opening crop form", "info");
              setTimeout(() => router.push("/crops/add"), 500);
              break;
            case "scan_disease":
              showFeedback("Opening disease detection", "info");
              setTimeout(() => router.push("/diseases"), 500);
              break;
            case "open_mitra":
              showFeedback("Opening Mitra chat", "info");
              setTimeout(() => router.push("/mitra"), 500);
              break;
            case "search": {
              const query = command.params?.query || "";
              showFeedback(`Searching: ${query}`, "info");
              setTimeout(() => router.push(`/mitra?q=${encodeURIComponent(query)}`), 500);
              break;
            }
            default:
              showFeedback("Command not recognized", "error");
          }
          break;
        }
        case "unknown":
        default:
          showFeedback(
            `"${text}" — command not recognized. Try again.`,
            "error"
          );
          break;
      }
    },
    [language, router, setLastCommand, setLanguage, setSpeaking, showFeedback]
  );

  // ── Start listening ──
  const startListening = useCallback(async () => {
    if (!isSupported) {
      showFeedback("Voice not supported in this browser", "error");
      return;
    }

    const SpeechRecognition = getSpeechRecognitionConstructor();
    if (!SpeechRecognition) {
      showFeedback("Voice not supported in this browser", "error");
      return;
    }

    // Stop any previous session
    if (recognitionRef.current) {
      recognitionRef.current.abort();
      recognitionRef.current = null;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = getSpeechRecognitionLang(language);
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setListening(true);
      setTranscript("");
      showFeedback("Listening...", "info", 10000);

      // Try to get microphone for audio level monitoring
      navigator.mediaDevices
        .getUserMedia({ audio: true })
        .then((stream) => {
          streamRef.current = stream;
          startLevelMonitoring(stream);
        })
        .catch(() => {
          // Mic access denied for level monitoring — still works without it
        });
    };

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let interimTranscript = "";
      let finalTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        } else {
          interimTranscript += result[0].transcript;
        }
      }

      // Show interim results in real-time
      if (interimTranscript) {
        setTranscript(interimTranscript);
      }

      // Process final result
      if (finalTranscript) {
        setTranscript(finalTranscript);
        processCommand(finalTranscript);
      }
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      if (event.error === "no-speech") {
        showFeedback("No speech detected. Try again.", "error");
      } else if (event.error === "audio-capture") {
        showFeedback("Microphone not available", "error");
      } else if (event.error === "not-allowed") {
        showFeedback("Microphone permission denied", "error");
      } else {
        showFeedback("Voice error. Please try again.", "error");
      }
      setListening(false);
      stopLevelMonitoring();
      recognitionRef.current = null;
    };

    recognition.onend = () => {
      setListening(false);
      stopLevelMonitoring();
      recognitionRef.current = null;
    };

    recognitionRef.current = recognition;

    try {
      recognition.start();
    } catch {
      showFeedback("Could not start voice recognition", "error");
      setListening(false);
    }
  }, [
    isSupported,
    language,
    setListening,
    setTranscript,
    processCommand,
    startLevelMonitoring,
    stopLevelMonitoring,
    showFeedback,
  ]);

  // ── Stop listening ──
  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.abort();
      recognitionRef.current = null;
    }
    setListening(false);
    stopLevelMonitoring();
  }, [setListening, stopLevelMonitoring]);

  // ── Toggle listening ──
  const handleToggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  // ── Get suggestions ──
  const suggestions = getVoiceCommandSuggestions(language);

  // ── Don't render if not supported ──
  if (!isSupported) {
    return null;
  }

  return (
    <>
      {/* ── Floating Voice Bar ── */}
      <div
        className={cn(
          "transition-all duration-300 ease-in-out",
          "w-full md:w-auto"
        )}
      >
        <AnimatePresence mode="wait">
          {isMinimized ? (
            /* ── Minimized: floating mic button ── */
            <motion.div
              key="minimized"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              className="flex justify-end"
            >
              <Button
                type="button"
                onClick={() => setMinimized(false)}
                className={cn(
                  "h-14 w-14 rounded-full shadow-xl transition-all duration-200",
                  "bg-mithrava-500 text-white hover:bg-mithrava-600",
                  isListening && "animate-pulse ring-4 ring-mithrava-300",
                  isSpeaking && "bg-blue-500 hover:bg-blue-600"
                )}
                aria-label={isListening ? "Listening... tap to expand" : "Open voice commands"}
              >
                {isListening ? (
                  <Loader2 className="h-6 w-6 animate-spin" />
                ) : isSpeaking ? (
                  <span className="text-xl">🔊</span>
                ) : (
                  <Mic className="h-6 w-6" />
                )}
              </Button>
            </motion.div>
          ) : (
            /* ── Expanded: full voice bar ── */
            <motion.div
              key="expanded"
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 20, opacity: 0 }}
              className={cn(
                "bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden",
                "md:w-[400px]"
              )}
            >
              {/* ── Header ── */}
              <div className="flex items-center justify-between px-4 pt-3 pb-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm">🎙️</span>
                  <h3 className="text-sm font-semibold text-gray-800">
                    Voice Commands
                  </h3>
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-mithrava-100 text-mithrava-700 font-medium">
                    {LANG_DISPLAY[language] || language}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => setMinimized(true)}
                    className="h-7 w-7 p-0 text-gray-400 hover:text-gray-600"
                    aria-label="Minimize voice bar"
                  >
                    <Minimize2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>

              {/* ── Transcript Display ── */}
              {(transcript || isListening) && (
                <div className="px-4 pb-2">
                  <div
                    className={cn(
                      "rounded-lg px-3 py-2 text-sm min-h-[36px]",
                      isListening && !transcript
                        ? "bg-gray-50 text-gray-400 italic"
                        : transcript
                        ? "bg-mithrava-50 text-mithrava-800"
                        : "bg-gray-50 text-gray-400"
                    )}
                  >
                    {isListening && !transcript ? (
                      "Listening..."
                    ) : (
                      transcript
                    )}
                  </div>
                </div>
              )}

              {/* ── Feedback Message ── */}
              <AnimatePresence>
                {feedbackMessage && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="px-4 pb-2"
                  >
                    <div
                      className={cn(
                        "rounded-lg px-3 py-2 text-xs font-medium",
                        feedbackType === "success" && "bg-green-50 text-green-700 border border-green-200",
                        feedbackType === "error" && "bg-red-50 text-red-700 border border-red-200",
                        feedbackType === "info" && "bg-blue-50 text-blue-700 border border-blue-200"
                      )}
                    >
                      {feedbackMessage}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* ── Mic Button + Waveform ── */}
              <div className="flex items-center gap-3 px-4 pb-3">
                <button
                  type="button"
                  onClick={handleToggleListening}
                  className={cn(
                    "relative flex items-center justify-center rounded-full transition-all duration-300 shrink-0",
                    "h-14 w-14 shadow-lg",
                    isListening
                      ? "bg-red-500 hover:bg-red-600 ring-4 ring-red-200 animate-pulse"
                      : "bg-mithrava-500 hover:bg-mithrava-600"
                  )}
                  aria-label={isListening ? "Stop listening" : "Start voice command"}
                  aria-pressed={isListening}
                >
                  {isListening ? (
                    <MicOff className="h-6 w-6 text-white" />
                  ) : (
                    <Mic className="h-6 w-6 text-white" />
                  )}
                  {/* Pulse ring when listening */}
                  {isListening && (
                    <span className="absolute inset-0 rounded-full animate-ping bg-red-400 opacity-30" />
                  )}
                </button>

                {/* Waveform / Status */}
                <div className="flex-1 flex items-center">
                  {isListening ? (
                    <WaveformAnimation audioLevel={audioLevel} />
                  ) : (
                    <div className="flex flex-col">
                      <p className="text-xs text-gray-500">
                        Tap mic to speak a command
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* ── Suggestions ── */}
              {!isListening && !transcript && (
                <div className="px-4 pb-3 border-t border-gray-100 pt-2">
                  <p className="text-[10px] text-gray-400 uppercase tracking-wider font-medium mb-1.5">
                    Try saying
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {suggestions.slice(0, 5).map((suggestion) => (
                      <button
                        key={suggestion}
                        type="button"
                        onClick={() => {
                          setTranscript(suggestion);
                          processCommand(suggestion);
                        }}
                        className="text-[11px] px-2 py-1 rounded-full bg-gray-50 text-gray-600 hover:bg-mithrava-50 hover:text-mithrava-700 transition-colors border border-gray-100"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  );
}
