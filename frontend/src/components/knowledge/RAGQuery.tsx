"use client";

import { useState, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, MicOff, Send, ThumbsUp, ThumbsDown, Loader2, RefreshCw, ExternalLink } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { knowledgeService } from "@/services/knowledgeService";
import { cn } from "@/lib/utils";
import {
  isSpeechRecognitionSupported,
  getSpeechRecognitionConstructor,
  getSpeechRecognitionLang,
} from "@/services/voiceCommandService";
import type { KnowledgeAskResponse, KnowledgeAskSource } from "@/types/knowledge";

interface RAGQueryProps {
  category?: string;
  className?: string;
}

export function RAGQuery({ category, className }: RAGQueryProps) {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<KnowledgeAskResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedbackGiven, setFeedbackGiven] = useState<"up" | "down" | null>(null);
  const [isListening, setIsListening] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /** Handle ask question */
  const handleAsk = useCallback(async () => {
    const trimmed = question.trim();
    if (!trimmed || isLoading) return;

    setIsLoading(true);
    setError(null);
    setResponse(null);
    setFeedbackGiven(null);

    try {
      const result = await knowledgeService.ask(trimmed, category);
      setResponse(result.data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [question, isLoading, category]);

  /** Handle retry */
  const handleRetry = useCallback(() => {
    handleAsk();
  }, [handleAsk]);

  /** Handle voice input (Web Speech API) */
  const toggleVoice = useCallback(() => {
    if (!isSpeechRecognitionSupported()) {
      return;
    }

    if (isListening) {
      setIsListening(false);
      return;
    }

    const SpeechRecognitionConstructor = getSpeechRecognitionConstructor();
    if (!SpeechRecognitionConstructor) return;

    const recognition = new SpeechRecognitionConstructor();
    recognition.lang = getSpeechRecognitionLang("en");
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript;
      setQuestion((prev) => (prev ? `${prev} ${transcript}` : transcript));
      setIsListening(false);
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    setIsListening(true);
    recognition.start();
  }, [isListening]);

  /** Handle feedback */
  const handleFeedback = useCallback(async (helpful: boolean) => {
    setFeedbackGiven(helpful ? "up" : "down");
    // Fire and forget - don't block UI
    try {
      await knowledgeService.ask("", category); // In production, send feedback endpoint
    } catch {
      // Silently fail
    }
  }, [category]);

  return (
    <div className={cn("space-y-4", className)}>
      {/* Input Section */}
      <Card className="border-mithrava-200 bg-gradient-to-br from-mithrava-50/50 to-white">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xl">🤖</span>
            <h3 className="font-semibold text-sm text-mithrava-800">
              Ask Mitra Anything
            </h3>
          </div>

          <div className="relative">
            <textarea
              ref={textareaRef}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleAsk();
                }
              }}
              placeholder="Ask about farming, crops, diseases..."
              rows={3}
              className={cn(
                "w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm resize-none",
                "placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-mithrava-500 focus:border-mithrava-500",
                "min-h-[80px]"
              )}
              disabled={isLoading}
            />

            <div className="flex items-center justify-between mt-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleVoice}
                className={cn(
                  "gap-1.5 text-xs",
                  isListening && "text-red-500"
                )}
                disabled={isLoading}
              >
                {isListening ? (
                  <>
                    <MicOff className="h-4 w-4" />
                    Stop
                  </>
                ) : (
                  <>
                    <Mic className="h-4 w-4" />
                    Voice
                  </>
                )}
              </Button>

              <Button
                onClick={handleAsk}
                disabled={!question.trim() || isLoading}
                size="default"
                className="gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Thinking...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    Ask
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center justify-center py-8"
          >
            <motion.div
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className="text-4xl mb-3"
            >
              🤖
            </motion.div>
            <p className="text-sm text-gray-500 font-medium">Thinking...</p>
            <p className="text-xs text-gray-400 mt-1">
              Searching through farming knowledge
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error State */}
      {error && !isLoading && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card className="border-red-200 bg-red-50">
            <CardContent className="p-4 text-center">
              <p className="text-sm text-red-700 mb-3">
                ⚠️ {error}
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRetry}
                className="gap-1.5"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Try Again
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Response */}
      {response && !isLoading && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-3"
        >
          {/* Answer Card */}
          <Card className="border-gray-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-lg">💡</span>
                <h4 className="font-semibold text-sm">Answer</h4>
                {/* Confidence indicator */}
                <span
                  className={cn(
                    "text-[10px] font-medium px-2 py-0.5 rounded-full ml-auto",
                    response.confidence >= 0.8
                      ? "bg-green-100 text-green-700"
                      : response.confidence >= 0.5
                      ? "bg-amber-100 text-amber-700"
                      : "bg-red-100 text-red-700"
                  )}
                >
                  {Math.round(response.confidence * 100)}% confident
                </span>
              </div>

              <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed whitespace-pre-wrap">
                {response.answer}
              </div>

              {/* Feedback */}
              <div className="flex items-center gap-3 mt-4 pt-3 border-t border-gray-100">
                <span className="text-xs text-gray-500">Was this helpful?</span>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => handleFeedback(true)}
                    className={cn(
                      "p-1.5 rounded-lg transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center",
                      feedbackGiven === "up"
                        ? "bg-green-100 text-green-600"
                        : "text-gray-400 hover:text-green-600 hover:bg-green-50"
                    )}
                    aria-label="Yes, helpful"
                  >
                    <ThumbsUp className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleFeedback(false)}
                    className={cn(
                      "p-1.5 rounded-lg transition-colors min-h-[36px] min-w-[36px] flex items-center justify-center",
                      feedbackGiven === "down"
                        ? "bg-red-100 text-red-600"
                        : "text-gray-400 hover:text-red-600 hover:bg-red-50"
                    )}
                    aria-label="No, not helpful"
                  >
                    <ThumbsDown className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Source Citations */}
          {response.sources.length > 0 && (
            <Card className="border-gray-200">
              <CardContent className="p-4">
                <h4 className="font-semibold text-xs text-gray-500 uppercase tracking-wider mb-3">
                  📚 Sources
                </h4>
                <div className="space-y-2">
                  {response.sources.map((source: KnowledgeAskSource, i: number) => (
                    <div
                      key={i}
                      className="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <span className="text-sm font-bold text-mithrava-500 mt-0.5">
                        {i + 1}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {source.title}
                        </p>
                        <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                          {source.excerpt}
                        </p>
                      </div>
                      <a
                        href={`/knowledge/article/${source.articleId}`}
                        className="shrink-0 p-1 text-gray-400 hover:text-mithrava-500 transition-colors"
                        aria-label={`Open ${source.title}`}
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      )}
    </div>
  );
}
