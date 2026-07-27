"use client";

import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import { Heart, MessageCircle, Send, Loader2, AlertCircle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useLanguage } from "@/hooks/useLanguage";
import { useAuth } from "@/hooks/useAuth";
import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from "@tanstack/react-query";
import { forumService } from "@/services/forumService";
import { cn, getInitials } from "@/lib/utils";
import type { ForumPost } from "@/types/forum";

const CATEGORIES = [
  { key: "all", label: "All", emoji: "📋" },
  { key: "crop_care", label: "Crop Care", emoji: "🌾" },
  { key: "pest_control", label: "Pest Control", emoji: "🐛" },
  { key: "weather", label: "Weather", emoji: "🌤️" },
  { key: "market", label: "Market", emoji: "💰" },
  { key: "tips", label: "Tips", emoji: "💡" },
  { key: "question", label: "Questions", emoji: "❓" },
];

const CATEGORY_COLORS: Record<string, string> = {
  crop_care: "bg-green-100 text-green-700",
  pest_control: "bg-red-100 text-red-700",
  weather: "bg-blue-100 text-blue-700",
  market: "bg-amber-100 text-amber-700",
  tips: "bg-purple-100 text-purple-700",
  question: "bg-gray-100 text-gray-700",
  general: "bg-gray-100 text-gray-600",
  finance: "bg-emerald-100 text-emerald-700",
};

function formatTimeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60_000);
  const diffHr = Math.floor(diffMs / 3_600_000);
  const diffDay = Math.floor(diffMs / 86_400_000);
  if (diffMin < 1) return "Just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;
  return date.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

export default function ForumContent() {
  const { t } = useLanguage();
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const [newPostTitle, setNewPostTitle] = useState("");
  const [newPostContent, setNewPostContent] = useState("");
  const [newPostCategory, setNewPostCategory] = useState("general");
  const [activeCategory, setActiveCategory] = useState("all");
  const [showComposer, setShowComposer] = useState(false);
  const [selectedPostId, setSelectedPostId] = useState<string | null>(null);
  const [commentText, setCommentText] = useState("");

  // Fetch posts with infinite scroll pagination
  const PAGE_SIZE = 20;
  const { data, isLoading, error, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
    queryKey: ["forum", activeCategory],
    queryFn: async ({ pageParam = 0 }) => {
      const params = activeCategory === "all"
        ? { skip: pageParam, limit: PAGE_SIZE }
        : { category: activeCategory, skip: pageParam, limit: PAGE_SIZE };
      const res = await forumService.list(params);
      return res.data;
    },
    getNextPageParam: (lastPage: any) => {
      if (!lastPage) return undefined;
      return lastPage.has_more ? (lastPage.skip || 0) + PAGE_SIZE : undefined;
    },
    initialPageParam: 0,
  });

  // Create post mutation
  const createPostMutation = useMutation({
    mutationFn: () => {
      const titleText = newPostTitle.trim();
      const contentText = newPostContent.trim();
      // Prepend the title to the content if both exist
      const fullContent = titleText
        ? `**${titleText}**\n\n${contentText}`
        : contentText;
      return forumService.create({
        content: fullContent,
        category: newPostCategory,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["forum"] });
      setNewPostTitle("");
      setNewPostContent("");
      setNewPostCategory("general");
      setShowComposer(false);
    },
  });

  // Like mutation with optimistic update
  const likeMutation = useMutation({
    mutationFn: (postId: string) => forumService.like(postId),
    onMutate: async (postId) => {
      await queryClient.cancelQueries({ queryKey: ["forum", activeCategory] });
      const previous = queryClient.getQueryData(["forum", activeCategory]);
      // Optimistically toggle the like count based on current state
      queryClient.setQueryData(["forum", activeCategory], (old: any) => {
        if (!old?.pages) return old;
        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            posts: (page?.posts ?? []).map((p: any) => {
              if (String(p.id) !== String(postId)) return p;
              return { ...p, likes_count: (p.likes_count || 0) + 1 };
            }),
          })),
        };
      });
      return { previous };
    },
    onError: (_err, _postId, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["forum", activeCategory], context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["forum"] });
    },
  });

  // Fetch comments for selected post
  const { data: commentsData, isLoading: commentsLoading } = useQuery({
    queryKey: ["forum-comments", selectedPostId],
    queryFn: async () => {
      if (!selectedPostId) return null;
      const res = await forumService.listComments(selectedPostId, { skip: 0, limit: 50 });
      return res.data;
    },
    enabled: !!selectedPostId,
  });

  // Add comment mutation
  const addCommentMutation = useMutation({
    mutationFn: ({ postId, content }: { postId: string; content: string }) =>
      forumService.comment(postId, { content }),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["forum-comments", variables.postId] });
      queryClient.invalidateQueries({ queryKey: ["forum"] });
      setCommentText("");
    },
  });

  const handlePost = useCallback(() => {
    if (!newPostTitle.trim() || !newPostContent.trim()) return;
    createPostMutation.mutate();
  }, [newPostTitle, newPostContent, newPostCategory, createPostMutation]);

  const toggleComments = useCallback((postId: string) => {
    setSelectedPostId((prev) => (prev === postId ? null : postId));
    setCommentText("");
  }, []);

  const handleSubmitComment = useCallback(() => {
    if (!selectedPostId || !commentText.trim()) return;
    addCommentMutation.mutate({ postId: selectedPostId, content: commentText.trim() });
  }, [selectedPostId, commentText, addCommentMutation]);

  const allPosts = data?.pages?.flatMap((page: any) => page?.posts ?? []) ?? [];

  return (
    <div className="p-4 space-y-4 pb-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">💬 {t("forum.title")}</h1>
        <Button onClick={() => setShowComposer(!showComposer)} className="gap-2" size="sm">
          <Send className="h-4 w-4" />
          New Post
        </Button>
      </div>

      {/* Category tabs */}
      <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.key}
            onClick={() => setActiveCategory(cat.key)}
            className={cn(
              "shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors flex items-center gap-1",
              activeCategory === cat.key
                ? "bg-mithrava-500 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            )}
          >
            <span>{cat.emoji}</span>
            {cat.label}
          </button>
        ))}
      </div>

      {/* Post Composer */}
      {showComposer && (
        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}>
          <Card className="border-mithrava-200">
            <CardContent className="p-4 space-y-3">
              <div className="flex items-center gap-3">
                <Avatar className="h-10 w-10 shrink-0">
                  <AvatarFallback className="text-sm">
                    {user?.name ? getInitials(user.name) : "U"}
                  </AvatarFallback>
                </Avatar>
                <p className="text-sm font-medium">{user?.name || "You"}</p>
              </div>
              <Input
                placeholder="Post title (e.g., 'Best fertilizer for tomato')"
                value={newPostTitle}
                onChange={(e) => setNewPostTitle(e.target.value)}
              />
              <textarea
                placeholder="Share your experience, ask a question, or give advice..."
                value={newPostContent}
                onChange={(e) => setNewPostContent(e.target.value)}
                rows={3}
                className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-mithrava-500 resize-none"
              />
              <div className="flex items-center justify-between">
                <select
                  value={newPostCategory}
                  onChange={(e) => setNewPostCategory(e.target.value)}
                  className="text-xs rounded-lg border border-gray-200 px-2 py-1.5 bg-white"
                >
                  {CATEGORIES.filter((c) => c.key !== "all").map((cat) => (
                    <option key={cat.key} value={cat.key}>
                      {cat.emoji} {cat.label}
                    </option>
                  ))}
                </select>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => setShowComposer(false)}>
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    onClick={handlePost}
                    disabled={!newPostTitle.trim() || !newPostContent.trim() || createPostMutation.isPending}
                  >
                    {createPostMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      "Post"
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Error */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4 flex items-center gap-2 text-sm text-red-700">
            <AlertCircle className="h-4 w-4" />
            Failed to load posts. Please try again.
          </CardContent>
        </Card>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-32 bg-gray-100 rounded-xl animate-pulse" />
          ))}
        </div>
      )}

      {/* Posts Feed */}
      {!isLoading && allPosts.length === 0 && !error && (
        <Card className="border-dashed border-gray-300">
          <CardContent className="p-8 text-center">
            <span className="text-4xl block mb-2">💬</span>
            <p className="text-sm font-medium text-gray-500">No posts yet</p>
            <p className="text-xs text-gray-400 mt-1">Be the first to share something with the community!</p>
          </CardContent>
        </Card>
      )}

      {!isLoading && allPosts.length > 0 && (
        <>
        <div className="space-y-3">
          {allPosts.map((post: any, index: number) => (
            <motion.div
              key={post.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <Avatar className="h-10 w-10 shrink-0">
                      <AvatarFallback className="text-sm bg-mithrava-100 text-mithrava-600">
                        {String(post.farmer_id || "F").slice(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="font-semibold text-sm">
                          Farmer {String(post.farmer_id || "").slice(0, 8)}
                        </p>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500">
                          {post.created_at ? formatTimeAgo(post.created_at) : ""}
                        </span>
                        {post.category && (
                          <Badge
                            variant="secondary"
                            className={cn(
                              "text-[10px] px-1.5 py-0",
                              CATEGORY_COLORS[post.category] || "bg-gray-100 text-gray-600"
                            )}
                          >
                            {post.category}
                          </Badge>
                        )}
                      </div>
                      {post.title && (
                        <p className="font-semibold text-sm mt-1">{post.title}</p>
                      )}
                      <p className="text-sm text-gray-700 mt-1 whitespace-pre-wrap">
                        {post.content}
                      </p>
                      {post.tags && post.tags.length > 0 && (
                        <div className="flex gap-1 mt-2 flex-wrap">
                          {post.tags.map((tag: string) => (
                            <span
                              key={tag}
                              className="text-[10px] px-2 py-0.5 rounded-full bg-mithrava-50 text-mithrava-600"
                            >
                              #{tag}
                            </span>
                          ))}
                        </div>
                      )}
                      <div className="flex items-center gap-4 mt-3 pt-3 border-t border-gray-100">
                        <button
                          onClick={() => likeMutation.mutate(post.id)}
                          className="flex items-center gap-1 text-sm text-gray-500 hover:text-red-500 transition-colors"
                        >
                          <Heart className="h-4 w-4" />
                          {post.likes_count || 0}
                        </button>
                        <button
                          onClick={() => toggleComments(post.id)}
                          className={cn(
                            "flex items-center gap-1 text-sm transition-colors",
                            selectedPostId === post.id
                              ? "text-mithrava-500 font-medium"
                              : "text-gray-500 hover:text-mithrava-500"
                          )}
                        >
                          <MessageCircle className="h-4 w-4" />
                          {post.comments_count || 0}
                        </button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Comments Section */}
              {selectedPostId === post.id && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-2"
                >
                  <Card className="border-mithrava-100 bg-gray-50/50">
                    <CardContent className="p-4 space-y-3">
                      {commentsLoading ? (
                        <div className="flex items-center justify-center py-4 gap-2 text-sm text-gray-500">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          Loading comments...
                        </div>
                      ) : (
                        <>
                          {commentsData?.comments && commentsData.comments.length > 0 ? (
                            <div className="space-y-3">
                              {commentsData.comments.map((comment: any) => (
                                <div
                                  key={comment.id}
                                  className="flex items-start gap-2"
                                >
                                  <Avatar className="h-7 w-7 shrink-0">
                                    <AvatarFallback className="text-[10px] bg-mithrava-100 text-mithrava-600">
                                      {String(comment.farmer_id || "F").slice(0, 2).toUpperCase()}
                                    </AvatarFallback>
                                  </Avatar>
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                      <span className="text-xs font-semibold text-gray-700">
                                        Farmer {String(comment.farmer_id || "").slice(0, 8)}
                                      </span>
                                      <span className="text-[10px] text-gray-400">
                                        {comment.created_at ? formatTimeAgo(comment.created_at) : ""}
                                      </span>
                                    </div>
                                    <p className="text-sm text-gray-600 mt-0.5">{comment.content}</p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-sm text-gray-400 text-center py-2">No comments yet</p>
                          )}

                          {/* Comment input */}
                          <div className="flex items-center gap-2 pt-2 border-t border-gray-200">
                            <Input
                              placeholder="Write a comment..."
                              value={commentText}
                              onChange={(e) => setCommentText(e.target.value)}
                              onKeyDown={(e) => {
                                if (e.key === "Enter" && !e.shiftKey) {
                                  e.preventDefault();
                                  handleSubmitComment();
                                }
                              }}
                              className="text-sm"
                              disabled={addCommentMutation.isPending}
                            />
                            <Button
                              size="sm"
                              onClick={handleSubmitComment}
                              disabled={!commentText.trim() || addCommentMutation.isPending}
                              className="shrink-0"
                            >
                              {addCommentMutation.isPending ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <Send className="h-4 w-4" />
                              )}
                            </Button>
                          </div>
                        </>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </motion.div>
          ))}
        </div>

        {/* Load More */}
        {hasNextPage && (
          <div className="flex justify-center py-4">
            <Button
              variant="outline"
              onClick={() => fetchNextPage()}
              disabled={isFetchingNextPage}
              className="gap-2"
            >
              {isFetchingNextPage ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Loading...
                </>
              ) : (
                "Load More"
              )}
            </Button>
          </div>
        )}
        </>
      )}
    </div>
  );
}
