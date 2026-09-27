from django.urls import path
from .views import (
    ProjectListCreateView,
    ProjectDetailView,
    ProjectStarToggleView,
    ProjectCommentListCreateView,
    ProjectCommentDetailView,
    UserProjectsListView,
    TrendingProjectsView
)

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project_list_create'),
    path('trending/', TrendingProjectsView.as_view(), name='project_trending'),
    path('developer/<str:username>/', UserProjectsListView.as_view(), name='user_projects_list'),
    path('<slug:slug>/', ProjectDetailView.as_view(), name='project_detail'),
    path('<slug:slug>/star/', ProjectStarToggleView.as_view(), name='project_star_toggle'),
    path('<slug:slug>/comments/', ProjectCommentListCreateView.as_view(), name='project_comments_list_create'),
    path('comments/<int:pk>/', ProjectCommentDetailView.as_view(), name='project_comment_detail'),
]
