"use client";

import { motion } from "framer-motion";
import { BookOpen } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { CategoryCard } from "@/components/knowledge/CategoryCard";
import { SearchBar } from "@/components/knowledge/SearchBar";
import { RAGQuery } from "@/components/knowledge/RAGQuery";
import { EmptyState } from "@/components/shared/EmptyState";
import { useKnowledgeCategories } from "@/hooks/useKnowledge";

export default function KnowledgePage() {
  const { data: categories = [], isLoading, isError } = useKnowledgeCategories();

  return (
    <div className="p-4 space-y-6 pb-8">
      {/* ── Hero Header ── */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-2xl bg-gradient-to-br from-mithrava-500 via-mithrava-600 to-mithrava-700 p-6 text-white shadow-lg shadow-mithrava-200"
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-2xl font-bold flex items-center gap-2">
              📚 Knowledge Base
            </h1>
            <p className="text-mithrava-100 text-sm mt-1">
              Everything you need to know about farming, from experts to AI
            </p>
          </div>
          <span className="text-4xl">📖</span>
        </div>
      </motion.div>

      {/* ── Search Bar ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <SearchBar
          placeholder="Search articles, crop tips, schemes..."
          className="w-full"
        />
      </motion.div>

      {/* ── Category Grid ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-mithrava-500" />
            Browse Topics
          </h2>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Card key={i} className="border-gray-200">
                <CardContent className="p-5 flex flex-col items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-gray-200 animate-pulse" />
                  <div className="h-4 w-20 bg-gray-200 rounded animate-pulse" />
                  <div className="h-3 w-24 bg-gray-100 rounded animate-pulse" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : isError || categories.length === 0 ? (
          <EmptyState
            icon={<span className="text-3xl">📚</span>}
            title="No topics available"
            description="Knowledge categories will appear here once they are added."
          />
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {categories.map((category, index) => (
              <CategoryCard
                key={category.id}
                category={category}
                index={index}
              />
            ))}
          </div>
        )}
      </motion.div>

      {/* ── Ask Mitra Anything (RAG) ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35 }}
      >
        <RAGQuery />
      </motion.div>
    </div>
  );
}
