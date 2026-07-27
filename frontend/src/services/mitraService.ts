import api from "./api";
import type { ApiResponse, PaginatedResponse } from "@/types/api";
import type {
  MitraMessage,
  MitraConversation,
  SendMessageRequest,
  VoiceMessageRequest,
  ChatResponse,
  CreateConversationRequest,
} from "@/types/mitra";

export const mitraService = {
  /** Send a text chat message */
  async chat(data: SendMessageRequest): Promise<ApiResponse<ChatResponse>> {
    const response = await api.post("/api/v1/mitra/chat", data);
    return response.data;
  },

  /** Send a voice message (audio base64 → server STT + TTS) */
  async voice(data: VoiceMessageRequest): Promise<ApiResponse<ChatResponse>> {
    const response = await api.post("/api/v1/mitra/voice", {
      content: "",
      voice_data: data.audioBase64,
      language: data.language,
      conversation_id: data.conversationId,
    });
    return response.data;
  },

  /** Generate TTS audio for text — returns raw audio Blob */
  async getTTS(text: string, language: string = "hi"): Promise<Blob> {
    const response = await api.post(
      "/api/v1/mitra/tts",
      { text, language },
      { responseType: "blob" }
    );
    return response.data;
  },

  /** Get available voice providers */
  async getVoiceProviders(): Promise<ApiResponse<{ stt: string[]; tts: string[] }>> {
    const response = await api.get("/api/v1/mitra/voice/providers");
    return response.data;
  },

  /** Get all conversations */
  async getConversations(): Promise<ApiResponse<MitraConversation[]>> {
    const response = await api.get("/api/v1/mitra/conversations");
    return response.data;
  },

  /** Get messages for a conversation */
  async getMessages(
    conversationId: string,
    _page: number = 1,
    _pageSize: number = 50
  ): Promise<ApiResponse<PaginatedResponse<MitraMessage>>> {
    const response = await api.get(`/api/v1/mitra/conversations/${conversationId}`);
    return response.data;
  },

  /** Create a new conversation */
  async createConversation(
    data: CreateConversationRequest
  ): Promise<ApiResponse<MitraConversation>> {
    const response = await api.post("/api/v1/mitra/conversations", null, {
      params: { language: data.language },
    });
    return response.data;
  },

  /** Delete a conversation */
  async deleteConversation(conversationId: string): Promise<ApiResponse<{ message: string }>> {
    const response = await api.delete(`/api/v1/mitra/conversations/${conversationId}`);
    return response.data;
  },
};
