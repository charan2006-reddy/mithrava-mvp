/** Forum post */
export interface ForumPost {
  id: string;
  farmerId: string;
  farmerName: string;
  farmerAvatar?: string;
  content: string;
  imageUrl?: string;
  likeCount: number;
  commentCount: number;
  isLiked: boolean;
  createdAt: string;
  updatedAt: string;
}

/** Forum comment */
export interface ForumComment {
  id: string;
  postId: string;
  farmerId: string;
  farmerName: string;
  farmerAvatar?: string;
  content: string;
  createdAt: string;
  updatedAt: string;
}

/** Create post request */
export interface CreatePostRequest {
  title?: string;
  content: string;
  category?: string;
  imageUrl?: string;
}

/** Create comment request */
export interface CreateCommentRequest {
  content: string;
}
