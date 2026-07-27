import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export interface VoiceCommand {
  intent: "navigate" | "query" | "action" | "unknown";
  target?: string;
  params?: Record<string, string>;
  confidence: number;
}

interface VoiceState {
  /** Whether the global voice bar is currently listening */
  isListening: boolean;
  /** Whether TTS audio is currently playing */
  isSpeaking: boolean;
  /** Real-time speech-to-text transcript while listening */
  transcript: string;
  /** Last processed voice command */
  lastCommand: VoiceCommand | null;
  /** Whether voice features are enabled (opt-in/opt-out) */
  voiceEnabled: boolean;
  /** Whether responses should auto-speak via TTS */
  autoSpeak: boolean;
  /** Whether the voice bar is minimized */
  isMinimized: boolean;

  // Actions
  setListening: (v: boolean) => void;
  setSpeaking: (v: boolean) => void;
  setTranscript: (t: string) => void;
  setLastCommand: (c: VoiceCommand | null) => void;
  setVoiceEnabled: (v: boolean) => void;
  setAutoSpeak: (v: boolean) => void;
  setMinimized: (v: boolean) => void;
}

export const useVoiceStore = create<VoiceState>()(
  persist(
    (set) => ({
      isListening: false,
      isSpeaking: false,
      transcript: "",
      lastCommand: null,
      voiceEnabled: true,
      autoSpeak: false,
      isMinimized: false,

      setListening: (v: boolean) => set({ isListening: v }),
      setSpeaking: (v: boolean) => set({ isSpeaking: v }),
      setTranscript: (t: string) => set({ transcript: t }),
      setLastCommand: (c: VoiceCommand | null) => set({ lastCommand: c }),
      setVoiceEnabled: (v: boolean) => set({ voiceEnabled: v }),
      setAutoSpeak: (v: boolean) => set({ autoSpeak: v }),
      setMinimized: (v: boolean) => set({ isMinimized: v }),
    }),
    {
      name: "mithrava-voice",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        voiceEnabled: state.voiceEnabled,
        autoSpeak: state.autoSpeak,
        isMinimized: state.isMinimized,
      }),
    }
  )
);
