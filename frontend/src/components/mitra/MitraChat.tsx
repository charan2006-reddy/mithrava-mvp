"use client";

import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";
import type { MitraMessage as MitraMessageType } from "@/types/mitra";
import { MitraMessageBubble } from "./MitraMessage";

interface MitraChatProps {
  messages: MitraMessageType[];
  isTyping: boolean;
}

export function MitraChat({ messages, isTyping }: MitraChatProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto px-4 py-3 space-y-4"
    >
      {messages.map((message) => (
        <MitraMessageBubble key={message.id} message={message} />
      ))}

      {/* Typing Indicator */}
      {isTyping && (
        <div className="flex items-start gap-2">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-mithrava-100 text-mithrava-600 text-xs font-bold">
            M
          </div>
          <div className="rounded-2xl rounded-tl-sm bg-gray-100 px-4 py-3">
            <div className="flex gap-1">
              <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.3s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.15s]" />
              <span className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
