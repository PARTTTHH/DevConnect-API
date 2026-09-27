from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import F

from .models import Post, PostLike, PostComment
from .serializers import PostSerializer, PostCommentSerializer
from core.permissions import IsOwnerOrReadOnly
from accounts.models import Follow


class PostListCreateView(generics.ListCreateAPIView):
    """
    Explore all developer posts globally, search through discussions/code snippets, or create a new post.
    """
    queryset = Post.objects.select_related('author').prefetch_related('comments__user').all()
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author__username', 'code_language']
    search_fields = ['content', 'code_snippet', 'author__username', 'author__headline']
    ordering_fields = ['likes_count', 'created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific post.
    """
    queryset = Post.objects.select_related('author').prefetch_related('comments__user').all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]


class PersonalizedFeedView(generics.ListAPIView):
    """
    Personalized feed of posts from developers the current user follows.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        following_user_ids = Follow.objects.filter(follower=self.request.user).values_list('following_id', flat=True)
        # Include followed users + self
        user_ids = list(following_user_ids) + [self.request.user.id]
        return Post.objects.filter(author_id__in=user_ids).select_related('author').prefetch_related('comments__user').order_by('-created_at')


class PostLikeToggleView(APIView):
    """
    Like or unlike a post.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like = PostLike.objects.filter(user=request.user, post=post).first()

        if like:
            like.delete()
            Post.objects.filter(pk=post.pk).update(likes_count=F('likes_count') - 1)
            post.refresh_from_db()
            return Response({
                'is_liked': False,
                'likes_count': post.likes_count,
                'message': 'Post unliked.'
            }, status=status.HTTP_200_OK)
        else:
            PostLike.objects.create(user=request.user, post=post)
            Post.objects.filter(pk=post.pk).update(likes_count=F('likes_count') + 1)
            post.refresh_from_db()

            if post.author != request.user:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=post.author,
                    actor=request.user,
                    verb='liked your post',
                    target_url=f'/api/posts/{post.id}/',
                    notification_type='POST_LIKE'
                )

            return Response({
                'is_liked': True,
                'likes_count': post.likes_count,
                'message': 'Post liked.'
            }, status=status.HTTP_201_CREATED)


class PostCommentListCreateView(generics.ListCreateAPIView):
    """
    List comments on a post or submit a new comment.
    """
    serializer_class = PostCommentSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        post_id = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_id)
        return PostComment.objects.filter(post=post).select_related('user')

    def perform_create(self, serializer):
        post_id = self.kwargs['pk']
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(user=self.request.user, post=post)
        Post.objects.filter(pk=post.pk).update(comments_count=F('comments_count') + 1)

        if post.author != self.request.user:
            from notifications.models import Notification
            Notification.objects.create(
                recipient=post.author,
                actor=self.request.user,
                verb='commented on your post',
                target_url=f'/api/posts/{post.id}/',
                notification_type='POST_COMMENT'
            )


class PostCommentDetailView(generics.DestroyAPIView):
    """
    Delete a comment on a post (Owner only).
    """
    queryset = PostComment.objects.all()
    serializer_class = PostCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_destroy(self, instance):
        post = instance.post
        instance.delete()
        if post.comments_count > 0:
            Post.objects.filter(pk=post.pk).update(comments_count=F('comments_count') - 1)
