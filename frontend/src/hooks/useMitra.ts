"use client";

import { useCallback, useRef } from "react";
import { toast } from "sonner";
import { useMitraStore } from "@/stores/mitraStore";
import { useUIStore } from "@/stores/uiStore";
import { mitraService } from "@/services/mitraService";
import type { MitraMessage } from "@/types/mitra";

export function useMitra() {
  const {
    conversations,
    currentConversation,
    messages,
    isTyping,
    isListening,
    setConversations,
    setCurrentConversation,
    setMessages,
    addMessage,
    setTyping,
    setListening,
    addConversation,
  } = useMitraStore();

  const { language } = useUIStore();
  const abortControllerRef = useRef<AbortController | null>(null);

  /** Load conversations */
  const loadConversations = useCallback(async () => {
    try {
      const response = await mitraService.getConversations();
      setConversations(response.data);
    } catch {
      // Silent fail for initial load
    }
  }, [setConversations]);

  /** Load messages for a conversation */
  const loadMessages = useCallback(
    async (conversationId: string) => {
      try {
        const response = await mitraService.getMessages(conversationId);
        setMessages(response.data.items);
      } catch {
        toast.error("Failed to load messages");
      }
    },
    [setMessages]
  );

  /** Send a text message */
  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      // Add user message optimistically
      const userMessage: MitraMessage = {
        id: `temp-${Date.now()}`,
        conversationId: currentConversation?.id || "",
        role: "user",
        content: content.trim(),
        language,
        isVoice: false,
        createdAt: new Date().toISOString(),
      };
      addMessage(userMessage);
      setTyping(true);

      try {
        const response = await mitraService.chat({
          conversationId: currentConversation?.id,
          content: content.trim(),
          language,
          isVoice: false,
        });

        // Update conversation if new
        if (!currentConversation) {
          addConversation({
            id: response.data.conversationId,
            farmerId: "",
            title: content.trim().slice(0, 50),
            language,
            lastMessage: content.trim(),
            lastMessageAt: new Date().toISOString(),
            messageCount: 2,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          });
        }

        addMessage(response.data.message);
      } catch {
        toast.error("Failed to send message. Please try again.");
      } finally {
        setTyping(false);
      }
    },
    [currentConversation, language, addMessage, setTyping, addConversation]
  );

  /** Send a voice message via backend STT */
  const sendVoiceMessage = useCallback(
    async (audioBase64: string) => {
      if (!audioBase64) return;

      // Add user voice message indicator
      const userMessage: MitraMessage = {
        id: `temp-voice-${Date.now()}`,
        conversationId: currentConversation?.id || "",
        role: "user",
        content: "🎤 Voice message",
        language,
        isVoice: true,
        createdAt: new Date().toISOString(),
      };
      addMessage(userMessage);
      setTyping(true);

      try {
        const response = await mitraService.voice({
          conversationId: currentConversation?.id,
          audioBase64,
          language,
        });

        // Update conversation if new
        if (!currentConversation) {
          addConversation({
            id: response.data.conversationId,
            farmerId: "",
            title: "Voice conversation",
            language,
            lastMessage: "Voice message",
            lastMessageAt: new Date().toISOString(),
            messageCount: 2,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          });
        }

        addMessage(response.data.message);
      } catch {
        toast.error("Failed to process voice message. Please try again.");
      } finally {
        setTyping(false);
      }
    },
    [currentConversation, language, addMessage, setTyping, addConversation]
  );

  /** Toggle voice listening */
  const toggleVoice = useCallback(() => {
    setListening(!isListening);
  }, [isListening, setListening]);

  /** Start a new conversation */
  const startNewConversation = useCallback(() => {
    setCurrentConversation(null);
    setMessages([]);
  }, [setCurrentConversation, setMessages]);

  /** Select a conversation */
  const selectConversation = useCallback(
    (conversationId: string) => {
      const conversation = conversations.find((c) => c.id === conversationId);
      if (conversation) {
        setCurrentConversation(conversation);
        loadMessages(conversationId);
      }
    },
    [conversations, setCurrentConversation, loadMessages]
  );

  return {
    conversations,
    currentConversation,
    messages,
    isTyping,
    isListening,
    loadConversations,
    loadMessages,
    sendMessage,
    sendVoiceMessage,
    toggleVoice,
    startNewConversation,
    selectConversation,
  };
}
