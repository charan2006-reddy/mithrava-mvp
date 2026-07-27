"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowLeft, Clock, ExternalLink, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ListSkeleton } from "@/components/shared/LoadingSkeleton";
import { EmptyState } from "@/components/shared/EmptyState";
import { useKnowledgeCategories, useKnowledgeArticles } from "@/hooks/useKnowledge";
import { truncate } from "@/lib/utils";

/** Friendly names for well-known category slugs */
const CATEGORY_LABELS: Record<string, { name: string; icon: string; description: string }> = {
  "crop-guides": { name: "Crop Guides", icon: "🌾", description: "Step-by-step guides for growing popular Indian crops" },
  "disease-database": { name: "Disease Database", icon: "🐛", description: "Identify and treat common crop diseases" },
  "government-schemes": { name: "Government Schemes", icon: "🏛️", description: "PM-KISAN, crop insurance, subsidies, and more" },
  "fertilizer-guide": { name: "Fertilizer Guide", icon: "💊", description: "NPK ratios, organic options, and timing tips" },
  "weather-tips": { name: "Weather Tips", icon: "🌤️", description: "Farm-friendly weather advice and seasonal planning" },
  "market-intelligence": { name: "Market Intelligence", icon: "💰", description: "Price trends, best time to sell, mandi info" },
};

function slugToTitle(slug: string): string {
  return slug
    .replace(/-/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

interface ArticleBrief {
  id: string;
  title: string;
  titleHi?: string;
  source: string;
  excerpt?: string;
  content?: string;
  readTimeMinutes: number;
  createdAt?: string;
}

export default function CategoryPage() {
  const params = useParams();
  const router = useRouter();
  const categorySlug = params.category as string;

  const [searchQuery, setSearchQuery] = useState("");

  const { data: categories = [] } = useKnowledgeCategories();
  const { data: rawArticles = [], isLoading } = useKnowledgeArticles(categorySlug);

  // Find category metadata from the cached categories list
  const categoryMeta =
    categories.find((c) => c.id === categorySlug) ??
    CATEGORY_LABELS[categorySlug] ?? {
      name: slugToTitle(categorySlug),
      icon: "📖",
      description: "",
    };

  // Cast raw articles to our local brief shape – the API may return extra fields
  // like `titleHi` and `excerpt` that the TypeScript type doesn't declare.
  const articles = rawArticles as unknown as ArticleBrief[];

  const filteredArticles = articles.filter(
    (a) =>
      a.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (a.excerpt ?? "").toLowerCase().includes(searchQuery.toLowerCase())
  );

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

  return (
    <div className="p-4 space-y-5 pb-8">
      {/* ── Header ── */}
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push("/knowledge")}
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-2xl">{categoryMeta.icon}</span>
            <h1 className="text-xl font-bold">{categoryMeta.name}</h1>
          </div>
          {"description" in categoryMeta && categoryMeta.description && (
            <p className="text-xs text-gray-500 mt-0.5">
              {categoryMeta.description}
            </p>
          )}
        </div>
      </div>

      {/* ── Search Within Category ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder={`Search in ${categoryMeta.name}...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 bg-white text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-mithrava-500 focus:border-mithrava-500 min-h-[48px]"
          />
        </div>
      </motion.div>

      {/* ── Article List ── */}
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        {isLoading ? (
          <ListSkeleton items={4} />
        ) : filteredArticles.length === 0 ? (
          <EmptyState
            icon={<span className="text-3xl">📖</span>}
            title="No articles found"
            description={
              searchQuery
                ? "Try a different search term"
                : "Articles for this category will be added soon"
            }
          />
        ) : (
          <div className="space-y-3">
            {filteredArticles.map((article, index) => (
              <motion.div
                key={article.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + index * 0.05 }}
              >
                <Card
                  className="border-gray-200 hover:border-mithrava-300 hover:shadow-md transition-all cursor-pointer"
                  onClick={() => router.push(`/knowledge/article/${article.id}`)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-sm text-gray-900 line-clamp-2">
                          {article.title}
                        </h3>
                        {article.titleHi && (
                          <p className="text-xs text-gray-400 mt-0.5">
                            {article.titleHi}
                          </p>
                        )}
                        <p className="text-xs text-gray-500 mt-2 line-clamp-2 leading-relaxed">
                          {article.excerpt ?? truncate(article.content ?? "", 150)}
                        </p>
                        <div className="flex items-center gap-3 mt-3">
                          <Badge
                            variant="secondary"
                            className={`text-[10px] font-medium ${getSourceColor(article.source)}`}
                          >
                            {article.source}
                          </Badge>
                          <span className="flex items-center gap-1 text-[10px] text-gray-400">
                            <Clock className="h-3 w-3" />
                            {article.readTimeMinutes} min read
                          </span>
                        </div>
                      </div>
                      <ExternalLink className="h-4 w-4 text-gray-300 shrink-0 mt-1" />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
}
