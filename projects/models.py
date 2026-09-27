from django.db import models
from django.utils.text import slugify
from accounts.models import User, Skill
import uuid


class Project(models.Model):
    PROJECT_TYPE_CHOICES = (
        ('WEB', 'Web Application'),
        ('API', 'REST / GraphQL API'),
        ('MOBILE', 'Mobile App'),
        ('AI_ML', 'AI & Machine Learning'),
        ('CLI', 'CLI Tool / Library'),
        ('OPEN_SOURCE', 'Open Source Package'),
        ('OTHER', 'Other'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    tagline = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField()
    repo_url = models.URLField(max_length=500, help_text='Repository mapping link (e.g. GitHub, GitLab)')
    github_repo_name = models.CharField(max_length=150, blank=True, default='', help_text='Format: owner/repo')
    demo_url = models.URLField(max_length=500, blank=True, default='')
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default='WEB', db_index=True)
    tech_stack = models.ManyToManyField(Skill, related_name='projects', blank=True)
    tags = models.JSONField(default=list, blank=True, help_text='List of tags e.g. [\"django\", \"postgres\", \"jwt\"]')
    stars_count = models.PositiveIntegerField(default=0, db_index=True)
    views_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-stars_count', '-created_at']

    def __str__(self):
        return f'{self.title} by {self.owner.username}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'project'
            unique_id = str(uuid.uuid4())[:8]
            self.slug = f'{base_slug}-{unique_id}'
        super().save(*args, **kwargs)


class ProjectStar(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='starred_projects')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='stars')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'project')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} starred {self.project.title}'


class ProjectComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_comments')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.project.title}'
