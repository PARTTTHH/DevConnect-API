from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import F

from .models import Project, ProjectStar, ProjectComment
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateUpdateSerializer,
    ProjectCommentSerializer
)
from .filters import ProjectFilter
from core.permissions import IsOwnerOrReadOnly, IsDeveloper


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    List projects with server-side pagination, advanced filtering, lookup searches, or create a new project repository entry.
    """
    queryset = Project.objects.select_related('owner').prefetch_related('tech_stack', 'comments').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['title', 'tagline', 'description', 'github_repo_name', 'tags', 'owner__username']
    ordering_fields = ['stars_count', 'views_count', 'created_at', 'title']
    ordering = ['-stars_count', '-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectCreateUpdateSerializer
        return ProjectListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a project. Automatically increments view count upon retrieval.
    """
    queryset = Project.objects.select_related('owner').prefetch_related('tech_stack', 'comments__user').all()
    lookup_field = 'slug'
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Atomic view count increment
        Project.objects.filter(pk=instance.pk).update(views_count=F('views_count') + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProjectStarToggleView(APIView):
    """
    Star or unstar a project.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        star = ProjectStar.objects.filter(user=request.user, project=project).first()

        if star:
            star.delete()
            Project.objects.filter(pk=project.pk).update(stars_count=F('stars_count') - 1)
            project.refresh_from_db()
            return Response({
                'is_starred': False,
                'stars_count': project.stars_count,
                'message': f'Unstarred {project.title}.'
            }, status=status.HTTP_200_OK)
        else:
            ProjectStar.objects.create(user=request.user, project=project)
            Project.objects.filter(pk=project.pk).update(stars_count=F('stars_count') + 1)
            project.refresh_from_db()

            # Trigger notification if not starring own project
            if project.owner != request.user:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=project.owner,
                    actor=request.user,
                    verb=f'starred your project \"{project.title}\"',
                    target_url=f'/api/projects/{project.slug}/',
                    notification_type='PROJECT_STAR'
                )

            return Response({
                'is_starred': True,
                'stars_count': project.stars_count,
                'message': f'Starred {project.title}.'
            }, status=status.HTTP_201_CREATED)


class ProjectCommentListCreateView(generics.ListCreateAPIView):
    """
    List comments on a project or post a new comment.
    """
    serializer_class = ProjectCommentSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        slug = self.kwargs['slug']
        project = get_object_or_404(Project, slug=slug)
        return ProjectComment.objects.filter(project=project).select_related('user')

    def perform_create(self, serializer):
        slug = self.kwargs['slug']
        project = get_object_or_404(Project, slug=slug)
        comment = serializer.save(user=self.request.user, project=project)

        if project.owner != self.request.user:
            from notifications.models import Notification
            Notification.objects.create(
                recipient=project.owner,
                actor=self.request.user,
                verb=f'commented on your project \"{project.title}\"',
                target_url=f'/api/projects/{project.slug}/',
                notification_type='PROJECT_COMMENT'
            )


class ProjectCommentDetailView(generics.DestroyAPIView):
    """
    Delete a comment (Owner only).
    """
    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]


class UserProjectsListView(generics.ListAPIView):
    """
    List all projects published by a specific developer.
    """
    serializer_class = ProjectListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['stars_count', 'created_at']

    def get_queryset(self):
        username = self.kwargs['username']
        return Project.objects.filter(owner__username=username).select_related('owner').prefetch_related('tech_stack')


class TrendingProjectsView(generics.ListAPIView):
    """
    Get top 10 trending projects by star count.
    """
    serializer_class = ProjectListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Project.objects.select_related('owner').prefetch_related('tech_stack').order_by('-stars_count', '-views_count')[:10]
