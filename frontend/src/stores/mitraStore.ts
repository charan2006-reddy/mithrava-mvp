import { create } from "zustand";
import type { MitraMessage, MitraConversation } from "@/types/mitra";

interface MitraStore {
  conversations: MitraConversation[];
  currentConversation: MitraConversation | null;
  messages: MitraMessage[];
  isTyping: boolean;
  isListening: boolean;
  setConversations: (conversations: MitraConversation[]) => void;
  setCurrentConversation: (conversation: MitraConversation | null) => void;
  setMessages: (messages: MitraMessage[]) => void;
  addMessage: (message: MitraMessage) => void;
  setTyping: (typing: boolean) => void;
  setListening: (listening: boolean) => void;
  addConversation: (conversation: MitraConversation) => void;
}

export const useMitraStore = create<MitraStore>()((set) => ({
  conversations: [],
  currentConversation: null,
  messages: [],
  isTyping: false,
  isListening: false,

  setConversations: (conversations: MitraConversation[]) => {
    set({ conversations });
  },

  setCurrentConversation: (conversation: MitraConversation | null) => {
    set({ currentConversation: conversation });
  },

  setMessages: (messages: MitraMessage[]) => {
    set({ messages });
  },

  addMessage: (message: MitraMessage) => {
    set((state) => ({
      messages: [...state.messages, message],
    }));
  },

  setTyping: (typing: boolean) => {
    set({ isTyping: typing });
  },

  setListening: (listening: boolean) => {
    set({ isListening: listening });
  },

  addConversation: (conversation: MitraConversation) => {
    set((state) => ({
      conversations: [conversation, ...state.conversations],
      currentConversation: conversation,
    }));
  },
}));
