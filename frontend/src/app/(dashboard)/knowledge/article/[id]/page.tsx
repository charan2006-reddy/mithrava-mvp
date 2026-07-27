"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowLeft, Clock, ThumbsUp, ThumbsDown, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RAGQuery } from "@/components/knowledge/RAGQuery";
import { useKnowledgeArticle } from "@/hooks/useKnowledge";

/** Extended shape the API may return at runtime (extra fields beyond KnowledgeArticle) */
interface ArticleData {
  id: string;
  title: string;
  titleHi?: string;
  content: string;
  source: string;
  category: string;
  categoryIcon?: string;
  readTimeMinutes: number;
  createdAt?: string;
  updatedAt?: string;
}

export default function ArticlePage() {
  const params = useParams();
  const router = useRouter();
  const articleId = params.id as string;

  const { data: rawArticle, isLoading } = useKnowledgeArticle(articleId);
  const article = rawArticle as unknown as ArticleData | undefined;

  const [feedback, setFeedback] = useState<"up" | "down" | null>(null);

  function getSourceColor(source: string): string {
    switch (source) {
      case "ICAR":
        return "bg-blue-100 text-blue-700";
      case "Government":
        return "bg-purple-100 text-purple-700";
      case "Mithrava Team":
        return "bg-mithrava-100 text-mithrava-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  }

  function renderContent(content: string) {
    // Simple markdown-like rendering: split by double newlines for paragraphs,
    // bold text between ** markers, and bullet points
    const paragraphs = content.split("\n\n").filter(Boolean);

    return paragraphs.map((para, i) => {
      const trimmed = para.trim();

      // Check if it's a heading-like line (starts with a word followed by colon)
      if (/^[A-Z][a-z\s]+:/.test(trimmed)) {
        const colonIndex = trimmed.indexOf(":");
        const heading = trimmed.slice(0, colonIndex);
        const body = trimmed.slice(colonIndex + 1).trim();

        return (
          <div key={i} className="mb-4">
            <h3 className="font-semibold text-sm text-mithrava-800 mb-1.5">
              {heading}
            </h3>
            <p className="text-sm text-gray-700 leading-relaxed">{body}</p>
          </div>
        );
      }

      // Check if it contains bullet points (lines starting with -)
      if (trimmed.includes("\n") && trimmed.split("\n").some((l) => l.trim().startsWith("-"))) {
        const lines = trimmed.split("\n").filter(Boolean);
        return (
          <ul key={i} className="mb-4 space-y-1.5 ml-1">
            {lines.map((line, j) => (
              <li key={j} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-mithrava-500 mt-0.5 shrink-0">•</span>
                <span className="leading-relaxed">{line.replace(/^-\s*/, "")}</span>
              </li>
            ))}
          </ul>
        );
      }

      return (
        <p key={i} className="text-sm text-gray-700 leading-relaxed mb-4">
          {trimmed}
        </p>
      );
    });
  }

  if (isLoading) {
    return (
      <div className="p-4 space-y-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-gray-200 animate-pulse" />
          <div className="flex-1 space-y-2">
            <div className="h-5 w-3/4 bg-gray-200 rounded animate-pulse" />
            <div className="h-3 w-1/2 bg-gray-100 rounded animate-pulse" />
          </div>
        </div>
        <div className="space-y-3">
          {Array.from({ length: 8 }).map((_, i) => {
            // Fixed widths to avoid hydration mismatch from Math.random()
            const widths = ["75%", "60%", "85%", "55%", "70%", "90%", "65%", "80%"];
            return (
              <div key={i} className="h-4 bg-gray-100 rounded animate-pulse" style={{ width: widths[i % widths.length] }} />
            );
          })}
        </div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="p-4 space-y-4">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => router.push("/knowledge")}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </div>
        <div className="text-center py-12">
          <span className="text-3xl">📖</span>
          <p className="text-sm text-gray-500 mt-3">Article not found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 space-y-5 pb-8">
      {/* ── Header ── */}
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => {
            if (article.category) {
              router.push(`/knowledge/${article.category}`);
            } else {
              router.push("/knowledge");
            }
          }}
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-lg">{article.categoryIcon ?? "📖"}</span>
            <Badge
              variant="secondary"
              className={`text-[10px] font-medium ${getSourceColor(article.source)}`}
            >
              {article.source}
            </Badge>
          </div>
        </div>
      </div>

      {/* ── Article Title ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-xl font-bold text-gray-900 leading-tight">
          {article.title}
        </h1>
        {article.titleHi && (
          <p className="text-sm text-gray-400 mt-1">{article.titleHi}</p>
        )}
        <div className="flex items-center gap-3 mt-3 text-xs text-gray-400">
          <span className="flex items-center gap-1">
            <Clock className="h-3.5 w-3.5" />
            {article.readTimeMinutes} min read
          </span>
          <span>•</span>
          <span className="flex items-center gap-1">
            <BookOpen className="h-3.5 w-3.5" />
            Knowledge Base
          </span>
        </div>
      </motion.div>

      {/* ── Article Content ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="border-gray-200">
          <CardContent className="p-5">
            {renderContent(article.content)}
          </CardContent>
        </Card>
      </motion.div>

      {/* ── Was This Helpful? ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="border-gray-200 bg-gray-50/50">
          <CardContent className="p-4">
            <p className="text-sm font-medium text-gray-700 mb-3">
              Was this article helpful?
            </p>
            <div className="flex items-center gap-3">
              <Button
                variant={feedback === "up" ? "default" : "outline"}
                size="sm"
                className="gap-1.5"
                onClick={() => setFeedback("up")}
              >
                <ThumbsUp className="h-4 w-4" />
                Yes
              </Button>
              <Button
                variant={feedback === "down" ? "default" : "outline"}
                size="sm"
                className="gap-1.5"
                onClick={() => setFeedback("down")}
              >
                <ThumbsDown className="h-4 w-4" />
                No
              </Button>
              {feedback && (
                <span className="text-xs text-gray-500">
                  Thank you for your feedback!
                </span>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* ── Ask Mitra About This Topic ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h2 className="text-base font-semibold mb-3">
          🤖 Ask Mitra about {article.title.split("—")[0].trim()}
        </h2>
        <RAGQuery category={article.category} />
      </motion.div>
    </div>
  );
}
