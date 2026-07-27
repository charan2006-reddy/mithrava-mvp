"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { KnowledgeCategory } from "@/types/knowledge";

interface CategoryCardProps {
  category: KnowledgeCategory;
  index?: number;
}

export function CategoryCard({ category, index = 0 }: CategoryCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      whileHover={{ y: -4 }}
    >
      <Link href={`/knowledge/${category.id}`}>
        <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer group border-gray-200 hover:border-mithrava-300 h-full">
          <CardContent className="p-5 flex flex-col items-center text-center gap-3">
            {/* Large emoji icon */}
            <motion.span
              className="text-4xl"
              whileHover={{ scale: 1.2, rotate: 5 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              {category.icon}
            </motion.span>

            {/* Category name */}
            <h3 className="font-semibold text-sm group-hover:text-mithrava-600 transition-colors">
              {category.name}
            </h3>

            {/* Description */}
            <p className="text-xs text-gray-500 leading-relaxed line-clamp-2">
              {category.description}
            </p>

            {/* Article count badge */}
            <Badge variant="secondary" className="text-[10px]">
              {category.articleCount} {category.articleCount === 1 ? "article" : "articles"}
            </Badge>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}
