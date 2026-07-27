/** Mitra message role */
export type MessageRole = "user" | "assistant";

/** Mitra message */
export interface MitraMessage {
  id: string;
  conversationId: string;
  role: MessageRole;
  content: string;
  language: string;
  isVoice: boolean;
  createdAt: string;
}

/** Mitra conversation */
export interface MitraConversation {
  id: string;
  farmerId: string;
  title: string;
  language: string;
  lastMessage?: string;
  lastMessageAt?: string;
  messageCount: number;
  createdAt: string;
  updatedAt: string;
}

/** Send message request */
export interface SendMessageRequest {
  conversationId?: string;
  content: string;
  language: string;
  isVoice: boolean;
}

/** Voice message request */
export interface VoiceMessageRequest {
  conversationId?: string;
  audioBase64: string;
  language: string;
}

/** Chat response */
export interface ChatResponse {
  conversationId: string;
  message: MitraMessage;
  suggestedActions?: string[];
}

/** Create conversation request */
export interface CreateConversationRequest {
  title?: string;
  language: string;
}
