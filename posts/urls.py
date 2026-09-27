from django.urls import path
from .views import (
    PostListCreateView,
    PostDetailView,
    PersonalizedFeedView,
    PostLikeToggleView,
    PostCommentListCreateView,
    PostCommentDetailView
)

urlpatterns = [
    path('', PostListCreateView.as_view(), name='post_list_create'),
    path('feed/', PersonalizedFeedView.as_view(), name='post_feed'),
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('<int:pk>/like/', PostLikeToggleView.as_view(), name='post_like_toggle'),
    path('<int:pk>/comments/', PostCommentListCreateView.as_view(), name='post_comments_list_create'),
    path('comments/<int:pk>/', PostCommentDetailView.as_view(), name='post_comment_detail'),
]
