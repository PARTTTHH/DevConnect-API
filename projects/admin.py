from django.contrib import admin
from .models import Project, ProjectStar, ProjectComment


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'project_type', 'stars_count', 'views_count', 'is_featured', 'created_at']
    list_filter = ['project_type', 'is_featured', 'created_at']
    search_fields = ['title', 'tagline', 'description', 'owner__username', 'github_repo_name']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tech_stack',)


@admin.register(ProjectStar)
class ProjectStarAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'created_at']
    search_fields = ['user__username', 'project__title']


@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'created_at']
    search_fields = ['user__username', 'project__title', 'content']
